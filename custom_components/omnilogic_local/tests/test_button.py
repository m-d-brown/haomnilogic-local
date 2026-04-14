"""Test the OmniLogic Local button platform."""

import pytest

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR

pytestmark = pytest.mark.asyncio

async def test_button_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that button entities are created."""
    states = hass.states.async_all("button")
    entity_ids = [s.entity_id for s in states]
    
    # Expected: VSP Presets (Low, Medium, High) for the Filter (ID 4)
    assert any("speed_low" in eid for eid in entity_ids)
    assert any("speed_medium" in eid for eid in entity_ids)
    assert any("speed_high" in eid for eid in entity_ids)

async def test_preset_button_press(hass: HomeAssistant, init_integration) -> None:
    """Test pressing a preset speed button updates the shadow library state."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("button")
    target_states = [s for s in states if "speed_medium" in s.entity_id]
    assert len(target_states) >= 1
    state = target_states[0]

    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: state.entity_id},
        blocking=True,
    )

    # Verify state in the shadow library. Medium preset is 50%.
    # System ID for filter pump is 4 in our updated conftest.
    assert mock_api.state["speed_4"] == 50
