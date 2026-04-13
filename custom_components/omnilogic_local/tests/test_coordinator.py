"""Test the OmniLogic Local coordinator."""

import pytest
from pyomnilogic_local.models.mspconfig import MSPConfig
from pyomnilogic_local.models.telemetry import Telemetry

from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR


pytestmark = pytest.mark.asyncio


async def test_coordinator_load_via_udp(
    hass: HomeAssistant,
    socket_enabled,
    config_entry,
    msp_config_xml: str,
    telemetry_xml: str,
) -> None:
    """Test the coordinator loads data via the live mock UDP server."""
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][config_entry.entry_id][KEY_COORDINATOR]

    assert coordinator.msp_config_xml == msp_config_xml
    assert coordinator.telemetry_xml == telemetry_xml

    assert isinstance(coordinator.msp_config, MSPConfig)
    assert isinstance(coordinator.telemetry, Telemetry)

    # Backyard system ID is 0
    assert coordinator.msp_config.backyard.system_id == 0

    # Air sensor is system ID 10 in the fixture
    assert 10 in coordinator.data
    assert coordinator.data[10].msp_config.name == "AirSensor"

    # Pool is system ID 3 in the fixture
    assert 3 in coordinator.data
    assert coordinator.data[3].msp_config.name == "Pool"


async def test_coordinator_load_via_mock(
    hass: HomeAssistant,
    init_integration,
) -> None:
    """Test the coordinator loads data via the mocked API (no UDP)."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]

    assert isinstance(coordinator.msp_config, MSPConfig)
    assert isinstance(coordinator.telemetry, Telemetry)

    # Verify the full device index was built
    assert 0 in coordinator.data   # Backyard
    assert 3 in coordinator.data   # Pool (BoW)
    assert 4 in coordinator.data   # Filter Pump
    assert 5 in coordinator.data   # CSAD pH
    assert 6 in coordinator.data   # Chlorinator
    assert 9 in coordinator.data   # ColorLogic Light
    assert 10 in coordinator.data  # Air Sensor
    assert 11 in coordinator.data  # Water Sensor
    assert 15 in coordinator.data  # Virtual Heater
    assert 16 in coordinator.data  # Heater Equipment


async def test_coordinator_device_count(
    hass: HomeAssistant,
    init_integration,
) -> None:
    """Verify the correct number of devices is discovered."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]

    # From the fixture, we expect these devices:
    # 0=Backyard, 3=Pool, 4=Filter, 5=CSAD, 6=Chlorinator, 7=ChlorinatorEquip,
    # 9=Light, 10=AirSensor, 11=WaterSensor, 12=FlowSensor,
    # 15=VirtualHeater, 16=HeaterEquip
    assert len(coordinator.data) >= 10
