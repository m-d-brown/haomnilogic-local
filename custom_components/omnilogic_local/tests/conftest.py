"""Common fixtures for the OmniLogic Local tests."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
import logging
import os
import random
import sys
import types
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from pyomnilogic_local.api import OmniLogicAPI
from pyomnilogic_local.models.mspconfig import MSPConfig
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
    loader.async_get_custom_components(hass)


# ===========================================================================
#  XML fixture helpers
# ===========================================================================
@pytest.fixture
def msp_config_xml() -> str:
    """Return sample MSPConfig XML."""
    with open(os.path.join(_FIXTURES_DIR, "issue-144-mspconfig.xml")) as fh:
        return fh.read()


@pytest.fixture
def telemetry_xml() -> str:
    """Return sample Telemetry XML."""
    with open(os.path.join(_FIXTURES_DIR, "issue-144-telemetry.xml")) as fh:
        return fh.read()


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
async def init_integration(
    hass: HomeAssistant,
    msp_config_xml: str,
    telemetry_xml: str,
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

    # Pre-parsed models from fixture XML
    msp_config = MSPConfig.load_xml(msp_config_xml)
    telemetry = Telemetry.load_xml(telemetry_xml)

    mock_api = AsyncMock(spec=OmniLogicAPI)
    # async_get_config is called twice: once in validate (returns raw XML), once in coordinator (returns raw XML)
    mock_api.async_get_config = AsyncMock(return_value=msp_config_xml)
    mock_api.async_get_telemetry = AsyncMock(return_value=telemetry_xml)
    # Command stubs
    mock_api.async_set_equipment = AsyncMock()
    mock_api.async_set_light_show = AsyncMock()
    mock_api.async_set_heater = AsyncMock()
    mock_api.async_set_heater_enable = AsyncMock()
    mock_api.async_set_solar_heater_enable = AsyncMock()
    mock_api.async_set_chlorinator_enable = AsyncMock()
    mock_api.async_set_spillover = AsyncMock()

    with patch(
        "custom_components.omnilogic_local.OmniLogicAPI",
        return_value=mock_api,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

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
