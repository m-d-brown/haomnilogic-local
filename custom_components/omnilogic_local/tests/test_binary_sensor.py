"""Test the OmniLogic Local binary sensor platform."""

import pytest

from homeassistant.core import HomeAssistant

pytestmark = pytest.mark.asyncio

async def test_binary_sensor_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that all expected binary sensor entities are created."""
    states = hass.states.async_all("binary_sensor")
    entity_ids = [s.entity_id for s in states]
    
    # Expected: Backyard Service Mode, Pool Flow
    assert any("service_mode" in eid for eid in entity_ids)
    assert any("flow" in eid for eid in entity_ids)

async def test_service_mode_sensor_state(hass: HomeAssistant, init_integration) -> None:
    """Test the service mode sensor state."""
    states = hass.states.async_all("binary_sensor")
    target_states = [s for s in states if "service_mode" in s.entity_id]
    assert len(target_states) >= 1
    state = target_states[0]
    
    # Backyard status defaults to 1 (ON) in the shadow library
    # Service mode is ON if state is not 1. So it should be OFF.
    assert state.state == "off"

async def test_flow_sensor_state(hass: HomeAssistant, init_integration) -> None:
    """Test the flow sensor state."""
    states = hass.states.async_all("binary_sensor")
    target_states = [s for s in states if "flow" in s.entity_id]
    assert len(target_states) >= 1
    state = target_states[0]
    
    # BoW Flow defaults to 1 (FLOW) in the shadow library
    assert state.state == "on"
