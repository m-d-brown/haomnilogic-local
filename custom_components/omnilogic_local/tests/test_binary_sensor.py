"""Test the OmniLogic Local binary sensor platform."""

import pytest
from homeassistant.core import HomeAssistant
from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR

pytestmark = pytest.mark.asyncio

async def test_binary_sensor_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that binary sensor entities are created."""
    states = hass.states.async_all("binary_sensor")
    entity_ids = [s.entity_id for s in states]
    assert any("service_mode" in eid for eid in entity_ids)
    assert any("flow" in eid for eid in entity_ids)

async def test_service_mode_sensor_state(hass: HomeAssistant, init_integration) -> None:
    """Test the service mode sensor state."""
    states = hass.states.async_all("binary_sensor")
    target = [s for s in states if "service_mode" in s.entity_id][0]
    # In the fixture status=72 for chlorinator, but backyard status is 1
    # Service mode is usually on if Backyard state is not 1 (ON)
    # Actually check binary_sensor.py for the logic.
    assert target.state == "off"

async def test_flow_sensor_state(hass: HomeAssistant, init_integration) -> None:
    """Test the flow sensor state."""
    states = hass.states.async_all("binary_sensor")
    target = [s for s in states if "flow" in s.entity_id][0]
    # In telemetry flow=0
    assert target.state == "off"
