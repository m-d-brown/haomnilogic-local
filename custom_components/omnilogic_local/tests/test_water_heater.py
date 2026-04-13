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
)
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR

pytestmark = pytest.mark.asyncio

async def test_water_heater_entity_created(hass: HomeAssistant, init_integration) -> None:
    """Test the water heater entity is created."""
    states = hass.states.async_all("water_heater")
    # From fixture: VirtualHeater system_id=7
    assert len(states) >= 1, f"Expected >= 1 water heater, got {len(states)}: {[s.entity_id for s in states]}"

async def test_water_heater_initial_state(hass: HomeAssistant, init_integration) -> None:
    """Test water heater initial state from telemetry.

    Fixture telemetry: VirtualHeater system_id=7 set_point=85 (F), min_temp=50 (F), max_temp=104 (F)
    """
    states = hass.states.async_all("water_heater")
    # Pool Heater is system_id 7
    heater = next(s for s in states if s.attributes.get("omni_system_id") == 7)

    # enabled=1 → operation mode is "on"
    # HA converts temperatures: 85°F → ~29.4°C, 50°F → ~10.0°C, 104°F → ~40.0°C
    assert heater.attributes.get("temperature") == pytest.approx(29.4, abs=0.1)
    assert heater.attributes.get("min_temp") == pytest.approx(10.0, abs=0.1)
    assert heater.attributes.get("max_temp") == pytest.approx(40.0, abs=0.1)

async def test_water_heater_set_temperature(hass: HomeAssistant, init_integration) -> None:
    """Test setting the water heater target temperature."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api
    system_id = 7

    states = hass.states.async_all("water_heater")
    heater = next(s for s in states if s.attributes.get("omni_system_id") == 7)
    entity_id = heater.entity_id

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {ATTR_ENTITY_ID: entity_id, ATTR_TEMPERATURE: 30}, # 30°C
        blocking=True,
    )

    # State-based assertion: system_id 7 set_point should be ~86°F
    # HA converts 30°C -> 86°F
    assert mock_api.state.get(f"set_point_{system_id}") == 86

async def test_water_heater_turn_off(hass: HomeAssistant, init_integration) -> None:
    """Test turning off the water heater."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api
    system_id = 7

    states = hass.states.async_all("water_heater")
    heater = next(s for s in states if s.attributes.get("omni_system_id") == 7)
    entity_id = heater.entity_id

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    # State-based assertion: heater_enable_7 should be False
    assert mock_api.state.get(f"heater_enable_{system_id}") is False

async def test_water_heater_turn_on(hass: HomeAssistant, init_integration) -> None:
    """Test turning on the water heater."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api
    system_id = 7

    states = hass.states.async_all("water_heater")
    heater = next(s for s in states if s.attributes.get("omni_system_id") == 7)
    entity_id = heater.entity_id

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    # State-based assertion: heater_enable_7 should be True
    assert mock_api.state.get(f"heater_enable_{system_id}") is True

async def test_water_heater_extra_attributes(hass: HomeAssistant, init_integration) -> None:
    """Test extra state attributes include heater equipment info."""
    states = hass.states.async_all("water_heater")
    heater = next(s for s in states if s.attributes.get("omni_system_id") == 7)
    attrs = heater.attributes

    # Should have solar_set_point from VirtualHeater config
    assert "solar_set_point" in attrs
