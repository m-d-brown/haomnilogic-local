"""Test the OmniLogic Local number platform."""

from unittest.mock import AsyncMock

import pytest

from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR


pytestmark = pytest.mark.asyncio


async def test_number_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that number entities are created."""
    states = hass.states.async_all("number")
    # Expected: Filter Speed, Solar Set Point (if heater enabled), Chlorinator Timed Percent
    assert len(states) >= 2, f"Expected >= 2 numbers, got {len(states)}: {[s.entity_id for s in states]}"


async def test_filter_speed_set_value(hass: HomeAssistant, init_integration) -> None:
    """Test setting the filter speed number value."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("number")
    filter_speed = [s for s in states if "filter" in s.entity_id.lower() and "speed" in s.entity_id.lower()][0]

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: filter_speed.entity_id, ATTR_VALUE: 50},
        blocking=True,
    )

    mock_api.async_set_equipment.assert_called_once()
    call_args = mock_api.async_set_equipment.call_args
    assert call_args[0][0] == 3     # bow_id
    assert call_args[0][1] == 4     # system_id
    assert call_args[0][2] == 50    # speed pct


async def test_chlorinator_timed_percent_set_value(hass: HomeAssistant, init_integration) -> None:
    """Test setting the chlorinator timed percent."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("number")
    chlor_timed = [s for s in states if "chlorinator" in s.entity_id.lower() and "timed" in s.entity_id.lower()][0]

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: chlor_timed.entity_id, ATTR_VALUE: 75},
        blocking=True,
    )

    mock_api.async_set_chlorinator_params.assert_called_once()
    call_kwargs = mock_api.async_set_chlorinator_params.call_args[1]
    assert call_kwargs["timed_percent"] == 75


async def test_solar_set_point_set_value(hass: HomeAssistant, init_integration) -> None:
    """Test setting the solar set point."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("number")
    solar_sp = [s for s in states if "solar_set_point" in s.entity_id.lower()]
    if not solar_sp:
        pytest.skip("No solar set point entity found in this fixture")
    
    entity_id = solar_sp[0].entity_id

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: entity_id, ATTR_VALUE: 30}, # 30°C
        blocking=True,
    )

    mock_api.async_set_solar_heater.assert_called_once()
    call_args = mock_api.async_set_solar_heater.call_args
    assert call_args[0][0] == 3     # bow_id
    assert call_args[0][1] == 15    # system_id
    assert call_args[0][2] == 30    # temp
