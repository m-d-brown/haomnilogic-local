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
    # Expected: VSP Presets (Low, Medium, High)
    assert any("speed_low" in eid for eid in entity_ids)
    assert any("speed_medium" in eid for eid in entity_ids)
    assert any("speed_high" in eid for eid in entity_ids)

async def test_preset_button_press(hass: HomeAssistant, init_integration) -> None:
    """Test pressing a preset speed button."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("button")
    target = [s for s in states if "speed_medium" in s.entity_id][0]

    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: target.entity_id},
        blocking=True,
    )

    mock_api.async_set_equipment.assert_called_once()
    call_args = mock_api.async_set_equipment.call_args
    # Medium preset in the generator should be 50
    assert call_args[0][2] == 50
