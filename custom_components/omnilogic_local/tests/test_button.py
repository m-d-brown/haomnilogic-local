"""Test the OmniLogic Local button platform."""

from unittest.mock import AsyncMock

import pytest

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR


pytestmark = pytest.mark.asyncio


async def test_button_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that button entities are created."""
    states = hass.states.async_all("button")
    # Expected: Low/Medium/High speed for Filter (3), maybe Restore Idle
    assert len(states) >= 3, f"Expected >= 3 buttons, got {len(states)}: {[s.entity_id for s in states]}"


async def test_filter_speed_button_press(hass: HomeAssistant, init_integration) -> None:
    """Test pressing a filter speed button sends the correct API call."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("button")
    high_speed = [s for s in states if "high_speed" in s.entity_id.lower() and "filter" in s.entity_id.lower()][0]

    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: high_speed.entity_id},
        blocking=True,
    )

    mock_api.async_set_equipment.assert_called_once()
    call_args = mock_api.async_set_equipment.call_args
    assert call_args[0][0] == 3     # bow_id
    assert call_args[0][1] == 4     # system_id
    # Default high speed in many pools is 100%, but check fixture if it fails.
    # In our fixture issue-144-mspconfig.xml, Filter system_id 4 has HighSpeed="100"
    assert call_args[0][2] == 100


async def test_restore_idle_button_press(hass: HomeAssistant, init_integration) -> None:
    """Test pressing the restore idle button."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("button")
    restore_idle = [s for s in states if "restore_idle" in s.entity_id.lower()][0]

    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: restore_idle.entity_id},
        blocking=True,
    )

    mock_api.async_restore_idle_state.assert_called_once()
