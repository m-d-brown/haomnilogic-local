"""Test the OmniLogic Local switch platform."""

from unittest.mock import AsyncMock

import pytest

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR


pytestmark = pytest.mark.asyncio


async def test_switch_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that switch entities are created for the fixture data."""
    states = hass.states.async_all("switch")
    # From the fixture we expect at least: Filter Pump (system_id 4), Chlorinator (6)
    assert len(states) >= 1, f"Expected >= 1 switch, got {len(states)}: {[s.entity_id for s in states]}"


async def test_filter_switch_initial_state(hass: HomeAssistant, init_integration) -> None:
    """Test the filter switch is off initially (filterState=0 in telemetry)."""
    states = hass.states.async_all("switch")
    filter_states = [s for s in states if "filter" in s.entity_id.lower()]
    assert len(filter_states) >= 1, f"No filter switch found: {[s.entity_id for s in states]}"
    assert filter_states[0].state == "off"


async def test_chlorinator_switch_initial_state(hass: HomeAssistant, init_integration) -> None:
    """Test the chlorinator switch is on initially (enable=1 in telemetry)."""
    states = hass.states.async_all("switch")
    chlor_states = [s for s in states if "chlorinator" in s.entity_id.lower()]
    assert len(chlor_states) >= 1, f"No chlorinator switch found: {[s.entity_id for s in states]}"
    assert chlor_states[0].state == "on"


async def test_filter_turn_on(hass: HomeAssistant, init_integration) -> None:
    """Test turning on the filter sends the correct API call."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("switch")
    filter_states = [s for s in states if "filter" in s.entity_id.lower()]
    assert len(filter_states) >= 1
    entity_id = filter_states[0].entity_id

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    # The filter turn_on calls async_set_equipment with last_speed
    mock_api.async_set_equipment.assert_called_once()
    call_args = mock_api.async_set_equipment.call_args
    # First arg is bow_id, second is system_id, third is speed/True
    assert call_args[0][0] == 3  # bow_id for Pool
    assert call_args[0][1] == 4  # system_id for Filter Pump


async def test_filter_turn_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning off the filter sends the correct API call."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("switch")
    filter_states = [s for s in states if "filter" in s.entity_id.lower()]
    assert len(filter_states) >= 1
    entity_id = filter_states[0].entity_id

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    mock_api.async_set_equipment.assert_called_once()
    call_args = mock_api.async_set_equipment.call_args
    assert call_args[0][0] == 3   # bow_id
    assert call_args[0][1] == 4   # system_id
    assert call_args[0][2] is False  # turn off


async def test_chlorinator_turn_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning off the chlorinator calls the correct API method."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("switch")
    chlor_states = [s for s in states if "chlorinator" in s.entity_id.lower()]
    assert len(chlor_states) >= 1
    entity_id = chlor_states[0].entity_id

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    mock_api.async_set_chlorinator_enable.assert_called_once()
    call_args = mock_api.async_set_chlorinator_enable.call_args
    assert call_args[0][0] == 3      # bow_id
    assert call_args[0][1] is False  # disable
