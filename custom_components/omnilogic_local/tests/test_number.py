"""Test the OmniLogic Local number platform."""

import pytest
from homeassistant.components.number import (
    ATTR_VALUE,
    SERVICE_SET_VALUE,
)
from homeassistant.components.number import (
    DOMAIN as NUMBER_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR

pytestmark = pytest.mark.asyncio


async def test_number_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that number entities are created."""
    states = hass.states.async_all("number")
    # Expected: Filter Speed, Chlor Timed Percent
    entity_ids = [s.entity_id for s in states]
    assert any("filter" in eid for eid in entity_ids)
    assert any("chlor" in eid for eid in entity_ids)


async def test_filter_speed_set_value(hass: HomeAssistant, init_integration) -> None:
    """Test setting the filter speed updates the shadow library state."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni

    states = hass.states.async_all("number")
    target_states = [s for s in states if "filter" in s.entity_id]
    assert len(target_states) >= 1
    state = target_states[0]

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: state.entity_id, ATTR_VALUE: 65},
        blocking=True,
    )

    # Verify state in the shadow library for Filter (ID 4)
    assert mock_api.state["speed_4"] == 65


async def test_chlorinator_timed_percent_set_value(hass: HomeAssistant, init_integration) -> None:
    """Test setting the chlorinator timed percent updates the shadow library state."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni

    states = hass.states.async_all("number")
    target_states = [s for s in states if "chlor" in s.entity_id]
    assert len(target_states) >= 1
    state = target_states[0]

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: state.entity_id, ATTR_VALUE: 75},
        blocking=True,
    )

    # Verify state in the shadow library for Chlor (ID 8)
    assert mock_api.state["timed_percent_8"] == 75
