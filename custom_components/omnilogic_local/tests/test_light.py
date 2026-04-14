"""Test the OmniLogic Local light platform."""

import pytest
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
)
from homeassistant.components.light import (
    DOMAIN as LIGHT_DOMAIN,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.core import HomeAssistant
from pyomnilogic_local.omnitypes import ColorLogicShow

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
    """Test turning on the light via API state."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni
    system_id = 9

    states = hass.states.async_all("light")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    # State-based assertion: system_id 9 should be True (ON) in mock_api state
    assert mock_api.state.get(system_id) is True


async def test_light_turn_on_with_brightness(hass: HomeAssistant, init_integration) -> None:
    """Test turning on the light with brightness."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni
    system_id = 9

    states = hass.states.async_all("light")
    entity_id = states[0].entity_id

    # HA brightness 128 (approx 50%) maps to ColorLogicBrightness.SIXTY_PERCENT or similar depending on conversion
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id, ATTR_BRIGHTNESS: 128},
        blocking=True,
    )

    result = mock_api.state.get(system_id)
    assert isinstance(result, dict)
    assert "brightness" in result
    # We don't strictly assert the exact enum member here unless we want to test the conversion logic
    assert result["brightness"] is not None


async def test_light_turn_on_with_effect(hass: HomeAssistant, init_integration) -> None:
    """Test turning on the light with an effect."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni
    system_id = 9

    states = hass.states.async_all("light")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id, ATTR_EFFECT: "VOODOO_LOUNGE"},
        blocking=True,
    )

    result = mock_api.state.get(system_id)
    assert isinstance(result, dict)
    assert result["show"] == ColorLogicShow.VOODOO_LOUNGE


async def test_light_turn_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning off the light."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni
    system_id = 9

    states = hass.states.async_all("light")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    assert mock_api.state.get(system_id) is False


async def test_light_effect_list(hass: HomeAssistant, init_integration) -> None:
    """Test the light exposes the ColorLogicShow effect list."""
    states = hass.states.async_all("light")
    light = states[0]
    effect_list = light.attributes.get("effect_list")
    assert effect_list is not None
    assert len(effect_list) > 0
    assert "VOODOO_LOUNGE" in effect_list
