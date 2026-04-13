"""Test the OmniLogic Local binary_sensor platform."""

import pytest

from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN


pytestmark = pytest.mark.asyncio


async def test_binary_sensor_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that binary sensor entities are created."""
    states = hass.states.async_all("binary_sensor")
    # From fixture should have: Service Mode (Backyard), Heater Status (system_id 16), Flow Status (system_id 12)
    assert len(states) >= 3, f"Expected >= 3 binary sensors, got {len(states)}: {[s.entity_id for s in states]}"


async def test_service_mode_sensor_off(hass: HomeAssistant, init_integration) -> None:
    """Test the service mode sensor is off (state=1 in backyard telemetry)."""
    states = hass.states.async_all("binary_sensor")
    service_mode = [s for s in states if "service_mode" in s.entity_id.lower()][0]
    # Backyard state=1 is ON, not SERVICE_MODE
    assert service_mode.state == "off"


async def test_heater_equipment_status(hass: HomeAssistant, init_integration) -> None:
    """Test the heater equipment status sensor (heaterState=0 in telemetry)."""
    states = hass.states.async_all("binary_sensor")
    heater_status = [s for s in states if "heater_equipment" in s.entity_id or "heat_pump" in s.entity_id.lower()][0]
    # heaterState=0 is OFF
    assert heater_status.state == "off"


async def test_flow_sensor_status(hass: HomeAssistant, init_integration) -> None:
    """Test the flow sensor status (flow=0 in telemetry)."""
    states = hass.states.async_all("binary_sensor")
    flow_status = [s for s in states if "flow" in s.entity_id.lower()][0]
    # BoW flow=0 is OFF (flowing is 1)
    assert flow_status.state == "off"
