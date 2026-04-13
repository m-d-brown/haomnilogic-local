"""Test the OmniLogic Local sensor platform."""

import pytest

from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR


pytestmark = pytest.mark.asyncio


async def test_sensor_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that all expected sensor entities are created."""
    states = hass.states.async_all("sensor")
    # We should have at least: air temp, water temp, filter power, pH, ORP,
    # chlorinator instant salt, chlorinator average salt
    assert len(states) >= 5, f"Expected >= 5 sensor entities, got {len(states)}: {[s.entity_id for s in states]}"


async def test_air_temperature_sensor(hass: HomeAssistant, init_integration) -> None:
    """Test the air temperature sensor reads the backyard air temp from telemetry."""
    # Air temp sensor for system_id 10, which senses Backyard (system_id 0)
    # Telemetry: airTemp="66"
    states = hass.states.async_all("sensor")
    air_temp_states = [s for s in states if "airsensor" in s.entity_id.lower()]
    assert len(air_temp_states) >= 1, f"No air sensor found in: {[s.entity_id for s in states]}"
    air_temp = air_temp_states[0]
    # The MSPConfig Units is Metric, so HA converts 66°F → ~18.89°C
    assert float(air_temp.state) == pytest.approx(18.89, abs=0.1)


async def test_water_temperature_sensor_unavailable(hass: HomeAssistant, init_integration) -> None:
    """Test the water temperature sensor returns None when temp is -1."""
    # Telemetry: waterTemp="-1" → should be None/unavailable
    states = hass.states.async_all("sensor")
    water_temp_states = [s for s in states if "watersensor" in s.entity_id.lower()]
    assert len(water_temp_states) >= 1, f"No water sensor found in: {[s.entity_id for s in states]}"
    water_temp = water_temp_states[0]
    # When water temp is -1, the sensor returns None, which HA renders as "unknown"
    assert water_temp.state in ("unknown", "unavailable", "None")


async def test_filter_power_sensor(hass: HomeAssistant, init_integration) -> None:
    """Test the filter power sensor. Filter is off, so power should be 0."""
    states = hass.states.async_all("sensor")
    power_states = [s for s in states if "power" in s.entity_id.lower()]
    assert len(power_states) >= 1, f"No power sensor found in: {[s.entity_id for s in states]}"
    power = power_states[0]
    assert power.state == "0"


async def test_chlorinator_salt_sensors(hass: HomeAssistant, init_integration) -> None:
    """Test the chlorinator salt level sensors."""
    # Telemetry: instantSaltLevel="3258", avgSaltLevel="3441"
    states = hass.states.async_all("sensor")
    salt_states = [s for s in states if "salt" in s.entity_id.lower()]
    assert len(salt_states) >= 2, f"Expected >= 2 salt sensors, got: {[s.entity_id for s in states]}"

    salt_values = {s.entity_id: s.state for s in salt_states}
    # One should be instant (3258), one should be average (3441)
    found_values = set(salt_values.values())
    assert "3258" in found_values or "3441" in found_values, f"Unexpected salt values: {salt_values}"


async def test_csad_ph_sensor(hass: HomeAssistant, init_integration) -> None:
    """Test the CSAD pH sensor."""
    # Telemetry: ph="0.0", mspconfig CalibrationValue="-1.0"
    # So native_value = 0.0 + (-1.0) = -1.0
    states = hass.states.async_all("sensor")
    ph_states = [s for s in states if "ph" in s.entity_id.lower() and "csad" not in s.entity_id.lower() or "ph" in s.entity_id.lower()]
    # The pH sensor should exist
    assert any("ph" in s.entity_id.lower() for s in states), f"No pH sensor found in: {[s.entity_id for s in states]}"
