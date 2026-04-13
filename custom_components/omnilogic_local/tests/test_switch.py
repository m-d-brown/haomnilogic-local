"""Test the OmniLogic Local switch platform."""

import pytest

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR

pytestmark = pytest.mark.asyncio

async def test_switch_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that switch entities are created for the fixture data."""
    states = hass.states.async_all("switch")
    # fixture has:
    # 1. Filter (system_id=6)
    # 2. Chlorinator (system_id=10)
    # 3. Waterfall (system_id=12)
    assert len(states) >= 3

async def test_filter_switch_initial_state(hass: HomeAssistant, init_integration) -> None:
    """Test the filter switch initial state."""
    states = hass.states.async_all("switch")
    # Filter system_id=6
    filter_switch = next(s for s in states if s.attributes.get("omni_system_id") == 6)
    assert filter_switch.state == "off"

async def test_filter_turn_on(hass: HomeAssistant, init_integration) -> None:
    """Test turning on the filter switch via API state."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api
    system_id = 6

    states = hass.states.async_all("switch")
    filter_switch = next(s for s in states if s.attributes.get("omni_system_id") == 6)
    entity_id = filter_switch.entity_id

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    # State-based assertion: system_id 6 should have some speed (e.g. 50 or True)
    assert mock_api.state.get(system_id) is not None

async def test_filter_turn_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning off the filter switch."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api
    system_id = 6

    states = hass.states.async_all("switch")
    filter_switch = next(s for s in states if s.attributes.get("omni_system_id") == 6)
    entity_id = filter_switch.entity_id

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    # State-based assertion: system_id 6 should be False (OFF)
    assert mock_api.state.get(system_id) is False

async def test_chlorinator_turn_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning off the chlorinator switch."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api
    bow_id = 3

    states = hass.states.async_all("switch")
    # Chlorinator switch for BOW 3
    chlor_switch = next(s for s in states if s.attributes.get("omni_bow_id") == 3 and "chlorinator" in s.entity_id)
    entity_id = chlor_switch.entity_id

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    # State-based assertion: chlor_enable_3 should be False
    assert mock_api.state.get(f"chlor_enable_{bow_id}") is False
