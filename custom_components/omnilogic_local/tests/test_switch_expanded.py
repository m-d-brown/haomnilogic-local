"""Expanded tests for the OmniLogic Local switch platform using model-layer mocking."""

from unittest.mock import ANY

import pytest

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR
from custom_components.omnilogic_local.tests.mock_models import (
    create_mock_backyard,
    create_mock_bow,
    create_mock_pump,
    create_mock_relay,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_omni_data():
    """Provide mocked OmniLogic data with multiple switch-capable entities."""
    backyard = create_mock_backyard()
    pool = create_mock_bow(system_id=1, name="Pool")
    # Relay in Backyard
    waterfall = create_mock_relay(system_id=2, name="Waterfall")
    # Pump in Pool
    jet_pump = create_mock_pump(system_id=3, name="Jet Pump", bow_id=1)

    return {
        0: backyard,
        1: pool,
        2: waterfall,
        3: jet_pump,
    }


async def test_expanded_switches_created(hass: HomeAssistant, init_integration) -> None:
    """Test that all expected switches are created."""
    states = hass.states.async_all(SWITCH_DOMAIN)
    entity_ids = [state.entity_id for state in states]

    assert any("waterfall" in eid for eid in entity_ids)
    assert any("jet_pump" in eid for eid in entity_ids)


async def test_relay_turn_on_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning a relay on and off."""
    entry_id = init_integration.entry_id
    coordinator = hass.data[DOMAIN][entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all(SWITCH_DOMAIN)
    target = next(s for s in states if "waterfall" in s.entity_id)

    # Turn On
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: target.entity_id},
        blocking=True,
    )
    mock_api.async_set_equipment.assert_called_with(
        target.attributes["omni_bow_id"], target.attributes["omni_system_id"], True
    )

    # Turn Off
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: target.entity_id},
        blocking=True,
    )
    mock_api.async_set_equipment.assert_called_with(
        target.attributes["omni_bow_id"], target.attributes["omni_system_id"], False
    )


async def test_standalone_pump_turn_on_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning a standalone pump on and off."""
    entry_id = init_integration.entry_id
    coordinator = hass.data[DOMAIN][entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all(SWITCH_DOMAIN)
    target = next(s for s in states if "jet_pump" in s.entity_id)

    # Turn On
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: target.entity_id},
        blocking=True,
    )
    # Standalone pumps are set to 50% speed by default in switch.py
    mock_api.async_set_equipment.assert_called_with(
        target.attributes["omni_bow_id"], target.attributes["omni_system_id"], 50
    )
