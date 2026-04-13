"""Test the OmniLogic Local water_heater platform."""

import pytest

from homeassistant.components.water_heater import (
    ATTR_TEMPERATURE,
    DOMAIN as WATER_HEATER_DOMAIN,
    SERVICE_SET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR


pytestmark = pytest.mark.asyncio


async def test_water_heater_entity_created(hass: HomeAssistant, init_integration) -> None:
    """Test the water heater entity is created."""
    states = hass.states.async_all("water_heater")
    # From fixture: VirtualHeater system_id=15
    assert len(states) >= 1, f"Expected >= 1 water heater, got {len(states)}: {[s.entity_id for s in states]}"


async def test_water_heater_initial_state(hass: HomeAssistant, init_integration) -> None:
    """Test water heater initial state from telemetry.

    Fixture telemetry: VirtualHeater systemId="15" Current-Set-Point="65" enable="1"
    """
    states = hass.states.async_all("water_heater")
    heater = states[0]

    # enabled=1 → operation mode is "on"
    # HA converts temperatures: 65°F → ~18.3°C, 55°F → ~12.8°C, 104°F → ~40°C
    assert heater.attributes.get("temperature") == pytest.approx(18.3, abs=0.1)
    assert heater.attributes.get("min_temp") == pytest.approx(12.8, abs=0.1)
    assert heater.attributes.get("max_temp") == pytest.approx(40.0, abs=0.1)


async def test_water_heater_set_temperature(hass: HomeAssistant, init_integration) -> None:
    """Test setting the water heater target temperature."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("water_heater")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {ATTR_ENTITY_ID: entity_id, ATTR_TEMPERATURE: 80},
        blocking=True,
    )

    mock_api.async_set_heater.assert_called_once()
    call_args = mock_api.async_set_heater.call_args
    assert call_args[0][0] == 3     # bow_id
    assert call_args[0][1] == 15    # system_id (VirtualHeater)
    # HA converts 80°C → 176°F because the integration declares Fahrenheit
    assert call_args[0][2] == 176   # temperature in °F


async def test_water_heater_turn_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning off the water heater."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("water_heater")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    mock_api.async_set_heater_enable.assert_called_once()
    call_args = mock_api.async_set_heater_enable.call_args
    assert call_args[0][0] == 3     # bow_id
    assert call_args[0][1] == 15    # system_id
    assert call_args[0][2] is False # disable


async def test_water_heater_turn_on(hass: HomeAssistant, init_integration) -> None:
    """Test turning on the water heater."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all("water_heater")
    entity_id = states[0].entity_id

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    mock_api.async_set_heater_enable.assert_called_once()
    call_args = mock_api.async_set_heater_enable.call_args
    assert call_args[0][0] == 3     # bow_id
    assert call_args[0][1] == 15    # system_id
    assert call_args[0][2] is True  # enable


async def test_water_heater_extra_attributes(hass: HomeAssistant, init_integration) -> None:
    """Test extra state attributes include heater equipment info."""
    states = hass.states.async_all("water_heater")
    heater = states[0]
    attrs = heater.attributes

    # Should have solar_set_point from VirtualHeater config
    assert "solar_set_point" in attrs

    # Should have heater equipment attributes (Heat Pump, system_id=16)
    heat_pump_keys = [k for k in attrs if "heat_pump" in k.lower() or "heat pump" in k.lower()]
    assert len(heat_pump_keys) >= 1, f"No heat pump attributes found in: {list(attrs.keys())}"
