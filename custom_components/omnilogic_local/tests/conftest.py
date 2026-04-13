from __future__ import annotations

import os
import sys

# Prepend the fakes directory to sys.path and clear the library cache.
# This MUST happen before any pyomnilogic_local imports.
fake_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fakes"))
sys.path.insert(0, fake_path)
for mod in list(sys.modules.keys()):
    if mod.startswith("pyomnilogic_local") or mod.startswith("custom_components.omnilogic_local"):
        del sys.modules[mod]

import asyncio
from collections.abc import AsyncGenerator, Generator
import json
import logging
import random
import types
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pyomnilogic_local.api import OmniLogicAPI
from pyomnilogic_local.models.mspconfig import MSPConfig, MSPSystem
from pyomnilogic_local.models.telemetry import Telemetry
from pyomnilogic_local.omnitypes import MessageType
from pyomnilogic_local.protocol import OmniLogicMessage

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
)
from homeassistant.core import HomeAssistant
import homeassistant.loader as loader

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR

# ---------------------------------------------------------------------------
# Module aliasing: map custom_components.omnilogic_local → homeassistant.components.omnilogic_local
# This allows imports like `from homeassistant.components.omnilogic_local.config_flow import ...`
# to resolve to the custom component.
# ---------------------------------------------------------------------------
from custom_components import omnilogic_local  # noqa: E402

_BASE_PKG = "custom_components.omnilogic_local"
_TARGET_PKG = "homeassistant.components.omnilogic_local"
sys.modules[_TARGET_PKG] = omnilogic_local
for _name, _module in list(sys.modules.items()):
    if _name.startswith(_BASE_PKG) and isinstance(_module, types.ModuleType):
        sys.modules[_name.replace(_BASE_PKG, _TARGET_PKG)] = _module

_LOGGER = logging.getLogger(__name__)

# Path to the XML fixture directory (relative to the project root, which is CWD)
_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


# ---------------------------------------------------------------------------
# Auto-use fixture: make the custom component discoverable by HA's loader
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def auto_enable_custom_integrations(hass: HomeAssistant) -> None:
    """Symlink our custom component into the hass temp config dir."""
    custom_components_dir = os.path.join(hass.config.config_dir, "custom_components")
    os.makedirs(custom_components_dir, exist_ok=True)
    source_dir = os.path.abspath("custom_components/omnilogic_local")
    dest_dir = os.path.join(custom_components_dir, "omnilogic_local")
    if not os.path.exists(dest_dir):
        os.symlink(source_dir, dest_dir)
    hass.data.pop(loader.DATA_CUSTOM_COMPONENTS, None)
    await loader.async_get_custom_components(hass)


@pytest.fixture(autouse=True)
def debug_json_serialization(monkeypatch):
    """Monkeypatch json_bytes to debug MagicMock serialization errors."""
    from homeassistant.core import json_bytes
    import homeassistant.core
    original_json_bytes = json_bytes

    def mocked_json_bytes(obj):
        try:
            return original_json_bytes(obj)
        except TypeError as e:
            if "MagicMock" in str(e):
                def find_mock(data, path=""):
                    if isinstance(data, dict):
                        for k, v in data.items():
                            find_mock(v, f"{path}.{k}")
                    elif isinstance(data, list):
                        for i, v in enumerate(data):
                            find_mock(v, f"{path}[{i}]")
                    elif isinstance(data, MagicMock):
                        print(f"DEBUG_MOCK_LEAK: Found MagicMock at {path}: {data}")
                find_mock(obj)
            raise e

    monkeypatch.setattr(homeassistant.core, "json_bytes", mocked_json_bytes)


# ===========================================================================
#  Mock UDP Server
# ===========================================================================
class MockOmniLogicServer(asyncio.DatagramProtocol):
    """Stateful mock of the OmniLogic controller's UDP interface."""

    def __init__(self, msp_config_xml: str, telemetry_xml: str) -> None:
        self.msp_config_xml = msp_config_xml
        self.telemetry_xml = telemetry_xml
        self.transport: asyncio.DatagramTransport | None = None
        self.received_commands: list[OmniLogicMessage] = []

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport  # type: ignore[assignment]

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        msg = OmniLogicMessage.from_bytes(data)
        _LOGGER.debug("MockServer received: %s from %s", msg, addr)
        self.received_commands.append(msg)

        # ACK everything that isn't itself an ACK
        if msg.type not in (MessageType.ACK, MessageType.XML_ACK):
            ack = OmniLogicMessage(msg.id, MessageType.ACK)
            self.transport.sendto(bytes(ack), addr)  # type: ignore[union-attr]

        if msg.type == MessageType.REQUEST_CONFIGURATION:
            self._send_large_response(msg.id, self.msp_config_xml, addr)
        elif msg.type == MessageType.GET_TELEMETRY:
            self._send_large_response(msg.id, self.telemetry_xml, addr)

    def _send_large_response(
        self, source_id: int, content: str, addr: tuple[str | Any, int]
    ) -> None:
        data = content.encode("utf-8")
        block_size = 512
        blocks = [data[i : i + block_size] for i in range(0, len(data), block_size)]

        lead_msg_xml = (
            '<?xml version="1.0" encoding="UTF-8" ?>'
            '<LeadMessage xmlns="http://nextgen.hayward.com/api">'
            f'<Parameter name="SourceOpId">{source_id}</Parameter>'
            f'<Parameter name="MsgSize">{len(data)}</Parameter>'
            f'<Parameter name="MsgBlockCount">{len(blocks)}</Parameter>'
            '<Parameter name="Type">1</Parameter>'
            "</LeadMessage>"
        )
        lead_msg = OmniLogicMessage(
            random.getrandbits(32), MessageType.MSP_LEADMESSAGE, lead_msg_xml
        )
        self.transport.sendto(bytes(lead_msg), addr)  # type: ignore[union-attr]

        for i, block in enumerate(blocks):
            payload = b"\x00" * 8 + block
            block_msg = OmniLogicMessage(i, MessageType.MSP_BLOCKMESSAGE)
            block_msg.payload = payload
            self.transport.sendto(bytes(block_msg), addr)  # type: ignore[union-attr]


# ===========================================================================
#  Server / API fixtures (for end-to-end UDP tests)
# ===========================================================================
@pytest.fixture
async def omni_server(
    msp_config_xml: str, telemetry_xml: str
) -> AsyncGenerator[tuple[str, int], None]:
    """Start the mock OmniLogic UDP server; returns (host, port)."""
    loop = asyncio.get_running_loop()
    transport, _protocol = await loop.create_datagram_endpoint(
        lambda: MockOmniLogicServer(msp_config_xml, telemetry_xml),
        local_addr=("127.0.0.1", 0),
    )
    host, port = transport.get_extra_info("sockname")
    yield host, port
    transport.close()


@pytest.fixture
async def omni_api(omni_server: tuple[str, int]) -> OmniLogicAPI:
    """OmniLogicAPI instance wired to the mock server."""
    host, port = omni_server
    return OmniLogicAPI(host, port, 5.0)


# ===========================================================================
#  Config-entry fixture that goes through the real config flow + UDP server
# ===========================================================================
@pytest.fixture
async def config_entry(
    hass: HomeAssistant, omni_server: tuple[str, int]
) -> AsyncGenerator[ConfigEntry, None]:
    """Set up a mock config entry via the real config flow."""
    host, port = omni_server
    entry_data = {
        CONF_IP_ADDRESS: host,
        CONF_PORT: port,
        CONF_NAME: "Mock Omni",
        CONF_TIMEOUT: 5.0,
        CONF_SCAN_INTERVAL: 10,
    }
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}, data=entry_data
    )
    assert result["type"] == "create_entry"
    yield result["result"]


# ===========================================================================
#  "init_integration" fixture: bypass config flow, patch API, load platforms
#  This is the standard HA testing pattern – much faster and more reliable
#  for platform-level tests.
# ===========================================================================
@pytest.fixture
def mock_omni_data() -> dict[int, EntityIndexData]:
    """Provide default mocked OmniLogic data for both core and expanded tests."""
    from pyomnilogic_local.omnitypes import (
        BodyOfWaterType,
        ChlorinatorDispenserType,
        ColorLogicLightType,
        FilterType,
        HeaterType,
        RelayFunction,
        RelayType,
        SensorType,
        SensorUnits,
    )

    from .mock_models import (
        create_mock_backyard,
        create_mock_bow,
        create_mock_chlorinator,
        create_mock_filter,
        create_mock_heater,
        create_mock_light,
        create_mock_relay,
        create_mock_sensor,
    )

    backyard = create_mock_backyard()
    # Air Temp Sensor
    air_temp = create_mock_sensor(
        system_id=1, name="Air Temp", bow_id=None, type=SensorType.AIR_TEMP, units=SensorUnits.FAHRENHEIT
    )
    # Water Temp Sensor
    water_temp = create_mock_sensor(
        system_id=2, name="Water Temp", bow_id=3, type=SensorType.WATER_TEMP, units=SensorUnits.FAHRENHEIT
    )
    # IDs here match the expectations in the core tests (issue-144 based)
    pool = create_mock_bow(system_id=3, name="Pool", type=BodyOfWaterType.POOL)
    filter_pump = create_mock_filter(system_id=6, name="Main Filter", bow_id=3, type=FilterType.VARIABLE_SPEED)
    heater = create_mock_heater(system_id=7, name="Pool Heater", bow_id=3)
    light = create_mock_light(system_id=9, name="Pool Light", bow_id=3, type=ColorLogicLightType.UCL)
    chlorinator = create_mock_chlorinator(
        system_id=10, name="Chlorinator", bow_id=3, dispenser_type=ChlorinatorDispenserType.SALT
    )
    # Relay
    relay = create_mock_relay(
        system_id=12, name="Waterfall", bow_id=3, type=RelayType.HIGH_VOLTAGE, function=RelayFunction.WATER_FEATURE
    )

    return {
        0: backyard,
        1: air_temp,
        2: water_temp,
        3: pool,
        6: filter_pump,
        7: heater,
        9: light,
        10: chlorinator,
        12: relay,
    }


@pytest.fixture
def mock_msp_config(mock_omni_data):
    """Mocked MSPConfig object with hierarchical data."""
    from pyomnilogic_local.models.mspconfig import MSPConfig, MSPSystem
    
    # Stitch the hierarchy
    backyard_data = mock_omni_data[0].msp_config
    pool_data = mock_omni_data[3].msp_config
    
    # Add sensors to backyard
    backyard_data.sensor = [mock_omni_data[1].msp_config]
    
    # Add BoW to backyard
    backyard_data.bow = [pool_data]
    
    # Add items to BoW
    pool_data.filter = [mock_omni_data[6].msp_config]
    pool_data.heater = mock_omni_data[7].msp_config
    pool_data.colorlogic_light = [mock_omni_data[9].msp_config]
    pool_data.chlorinator = mock_omni_data[10].msp_config
    pool_data.relay = [mock_omni_data[12].msp_config]
    pool_data.sensor = [mock_omni_data[2].msp_config] # Water temp
    
    msp = MSPConfig(
        system=MSPSystem(vsp_speed_format="Percent", units="Standard"),
        backyard=backyard_data
    )
    return msp


@pytest.fixture
def mock_telemetry(mock_omni_data):
    """Mocked Telemetry object with hierarchical data."""
    from pyomnilogic_local.models.telemetry import Telemetry
    tele = Telemetry()
    
    tele.backyard = mock_omni_data[0].telemetry
    tele.bow = [mock_omni_data[3].telemetry]
    tele.filter = [mock_omni_data[6].telemetry]
    tele.heater = [mock_omni_data[7].telemetry]
    tele.colorlogic_light = [mock_omni_data[9].telemetry]
    tele.chlorinator = [mock_omni_data[10].telemetry]
    tele.relay = [mock_omni_data[12].telemetry]
    # No way currently to handle multiple sensors in TelemetryBoW in my fake Telemetry easily,
    # but the core ones are handled by the lists.
    
    return tele


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    mock_omni_data,
    mock_msp_config,
    mock_telemetry,
) -> AsyncGenerator[ConfigEntry, None]:
    """Set up the omnilogic_local integration with fully mocked API responses.

    This fixture:
      1. Creates a MockConfigEntry with valid data.
      2. Patches OmniLogicAPI so no real UDP traffic is needed.
      3. Loads the integration and all platforms.

    Yields the ConfigEntry so tests can inspect hass.data, entities, etc.
    """
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_IP_ADDRESS: "127.0.0.1",
            CONF_PORT: 10444,
            CONF_NAME: "Test Omni",
            CONF_TIMEOUT: 5.0,
            CONF_SCAN_INTERVAL: 10,
        },
        title="Test Omni",
        version=2,
    )
    entry.add_to_hass(hass)

    entry.add_to_hass(hass)

    # Since we have globally injected our fakes directory into sys.path,
    # the integration will naturally load our FakeOmniLogicAPI.
    # We still patch the coordinator's data-loading methods for now to inject our mock data.
    with patch(
        "custom_components.omnilogic_local.coordinator.MSPConfig.load_xml",
        return_value=mock_msp_config,
    ), patch(
        "custom_components.omnilogic_local.coordinator.Telemetry.load_xml",
        return_value=mock_telemetry,
    ), patch(
        "custom_components.omnilogic_local.coordinator.OmniLogicCoordinator._async_update_data",
        new_callable=AsyncMock,
        return_value=mock_omni_data,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Ensure the coordinator has the mocked config and telemetry objects after setup
        entry_id = entry.entry_id
        if DOMAIN in hass.data and entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id][KEY_COORDINATOR]
            coordinator.msp_config = mock_msp_config
            coordinator.telemetry = mock_telemetry

        yield entry


# ===========================================================================
#  Small utility fixtures
# ===========================================================================
@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Override async_setup_entry (useful for config-flow-only tests)."""
    with patch(
        "custom_components.omnilogic_local.async_setup_entry", return_value=True
    ) as mock:
        yield mock
