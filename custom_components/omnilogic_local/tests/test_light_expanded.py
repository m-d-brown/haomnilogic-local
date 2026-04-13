"""Expanded tests for the OmniLogic Local light platform using model-layer mocking."""

from unittest.mock import ANY

import pytest

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    DOMAIN as LIGHT_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON, SERVICE_TURN_OFF
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR
from custom_components.omnilogic_local.tests.mock_models import (
    create_mock_backyard,
    create_mock_bow,
    create_mock_light,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_omni_data():
    """Provide mocked OmniLogic data with a pool and a light."""
    backyard = create_mock_backyard()
    pool = create_mock_bow(system_id=1, name="Pool")
    light = create_mock_light(system_id=2, name="Pool Light", bow_id=1)

    return {
        0: backyard,
        1: pool,
        2: light,
    }


async def test_light_turn_on_with_brightness(
    hass: HomeAssistant, init_integration
) -> None:
    """Test turning a light on with brightness."""
    entry_id = init_integration.entry_id
    coordinator = hass.data[DOMAIN][entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all(LIGHT_DOMAIN)
    assert states, "No light entities found in states"
    target = states[0]

    # HA brightness is 0-255, Omni is 0-4 (ColorLogicBrightness)
    # 128 / 255 * 4 ~= 2
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: target.entity_id, ATTR_BRIGHTNESS: 128},
        blocking=True,
    )

    mock_api.async_set_light_show.assert_called_with(
        target.attributes["omni_bow_id"],
        target.attributes["omni_system_id"],
        show=ANY,
        speed=ANY,
        brightness=ANY,
    )


async def test_light_turn_on_with_effect(hass: HomeAssistant, init_integration) -> None:
    """Test turning a light on with an effect."""
    entry_id = init_integration.entry_id
    coordinator = hass.data[DOMAIN][entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all(LIGHT_DOMAIN)
    assert states, "No light entities found in states"
    target = states[0]

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: target.entity_id, ATTR_EFFECT: "VOODOO_LOUNGE"},
        blocking=True,
    )
    # VOODOO_LOUNGE mapping should be verified
    mock_api.async_set_light_show.assert_called_with(
        target.attributes["omni_bow_id"],
        target.attributes["omni_system_id"],
        show=ANY,
        speed=ANY,
        brightness=ANY,
    )
