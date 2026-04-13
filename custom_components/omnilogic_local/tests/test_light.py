"""Test the OmniLogic Local light platform."""

import pytest
from pyomnilogic_local.omnitypes import ColorLogicBrightness, ColorLogicShow

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    DOMAIN as LIGHT_DOMAIN,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR


pytestmark = pytest.mark.asyncio


async def test_light_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that light entities are created for the fixture data."""
    states = hass.states.async_all("light")
    # fixture has one ColorLogic-Light (system_id=9, type=UCL)
    assert len(states) >= 1, f"Expected >= 1 light, got {len(states)}: {[s.entity_id for s in states]}"


async def test_light_initial_state_off(hass: HomeAssistant, init_integration) -> None:
    """Test the light is off initially (lightState=0 in telemetry)."""
    states = hass.states.async_all("light")
    assert len(states) >= 1
    light = states[0]
    assert light.state == "off"


async def test_light_turn_on(hass: HomeAssistant, init_integration) -> None:
    """Test turning on the light calls async_set_equipment."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("light")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    # Basic turn_on without kwargs → calls async_set_equipment
    mock_api.async_set_equipment.assert_called_once()
    call_args = mock_api.async_set_equipment.call_args
    assert call_args[0][0] == 3   # bow_id
    assert call_args[0][1] == 9   # system_id
    assert call_args[0][2] is True  # on


async def test_light_turn_on_with_brightness(hass: HomeAssistant, init_integration) -> None:
    """Test turning on the light with brightness calls async_set_light_show."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("light")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id, ATTR_BRIGHTNESS: 128},
        blocking=True,
    )

    # With kwargs → calls async_set_light_show
    mock_api.async_set_light_show.assert_called_once()
    call_args = mock_api.async_set_light_show.call_args
    assert call_args[0][0] == 3   # bow_id
    assert call_args[0][1] == 9   # system_id


async def test_light_turn_on_with_effect(hass: HomeAssistant, init_integration) -> None:
    """Test turning on the light with an effect."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("light")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id, ATTR_EFFECT: "VOODOO_LOUNGE"},
        blocking=True,
    )

    mock_api.async_set_light_show.assert_called_once()
    call_kwargs = mock_api.async_set_light_show.call_args[1]
    assert call_kwargs["show"] == ColorLogicShow.VOODOO_LOUNGE


async def test_light_turn_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning off the light."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("light")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    mock_api.async_set_equipment.assert_called_once()
    call_args = mock_api.async_set_equipment.call_args
    assert call_args[0][0] == 3   # bow_id
    assert call_args[0][1] == 9   # system_id
    assert call_args[0][2] is False  # off


async def test_light_effect_list(hass: HomeAssistant, init_integration) -> None:
    """Test the light exposes the ColorLogicShow effect list."""
    states = hass.states.async_all("light")
    light = states[0]
    effect_list = light.attributes.get("effect_list")
    assert effect_list is not None
    assert len(effect_list) > 0
    assert "VOODOO_LOUNGE" in effect_list
