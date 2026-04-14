"""Test the OmniLogic Local coordinator."""

import pytest
from pyomnilogic_local.models.mspconfig import MSPConfig
from pyomnilogic_local.models.telemetry import Telemetry

from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR

pytestmark = pytest.mark.asyncio

async def test_coordinator_load_via_mock(
    hass: HomeAssistant,
    init_integration,
) -> None:
    """Test the coordinator loads data via the mocked API (no UDP)."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]

    assert isinstance(coordinator.msp_config, MSPConfig)
    assert isinstance(coordinator.telemetry, Telemetry)

    # Verify the full device index was built using IDs from conftest.py's mock_omni_data
    assert 0 in coordinator.data   # Backyard
    assert 1 in coordinator.data   # Air Temp
    assert 2 in coordinator.data   # Water Temp
    assert 3 in coordinator.data   # Pool (BoW)
    assert 6 in coordinator.data   # Main Filter
    assert 7 in coordinator.data   # Pool Heater (Virtual Heater)
    assert 9 in coordinator.data   # Pool Light
    assert 10 in coordinator.data  # Chlorinator
    assert 12 in coordinator.data  # Waterfall (Relay)

async def test_coordinator_device_count(
    hass: HomeAssistant,
    init_integration,
) -> None:
    """Verify the correct number of devices is discovered."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]

    # From conftest.py fixture, we expect 12 devices:
    # None=System, 0=Backyard, 1=AirTemp, 2=WaterTemp, 3=Pool, 4=Flow, 6=Filter, 7=Heater, 9=Light, 10=Chlor, 11=CSAD, 12=Relay
    assert len(coordinator.data) == 12
