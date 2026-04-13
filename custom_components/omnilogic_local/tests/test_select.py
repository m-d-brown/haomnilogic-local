"""Test the OmniLogic Local select platform."""

import pytest
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN, SERVICE_SELECT_OPTION
from homeassistant.const import ATTR_ENTITY_ID, ATTR_OPTION
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR

pytestmark = pytest.mark.asyncio

async def test_select_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that select entities are created."""
    states = hass.states.async_all("select")
    # Expected: Light Show
    entity_ids = [s.entity_id for s in states]
    assert any("light_show" in eid for eid in entity_ids)

async def test_light_show_select_option(hass: HomeAssistant, init_integration) -> None:
    """Test selecting a light show option."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("select")
    target = [s for s in states if "light_show" in s.entity_id][0]

    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: target.entity_id, ATTR_OPTION: "Voodoo Lounge"},
        blocking=True,
    )

    mock_api.async_set_equipment.assert_called_once()
    call_args = mock_api.async_set_equipment.call_args
    # Data1 is the show ID (Voodoo Lounge is usually 1)
    assert call_args[0][2] == 1
