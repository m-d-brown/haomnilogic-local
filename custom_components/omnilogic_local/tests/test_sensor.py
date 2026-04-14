"""Test the OmniLogic Local sensor platform."""

import pytest

from homeassistant.core import HomeAssistant

pytestmark = pytest.mark.asyncio

async def test_sensor_entities_created(hass: HomeAssistant, init_integration) -> None:
    """Test that all expected sensor entities are created."""
    states = hass.states.async_all("sensor")
    # Expected: air temp, water temp, filter power, salt level (instant/avg), pH, ORP
    # Our CSAD creates both pH and ORP
    assert len(states) >= 6

async def test_air_temperature_sensor(hass: HomeAssistant, init_integration) -> None:
    """Test the air temperature sensor reads the backyard air temp."""
    states = hass.states.async_all("sensor")
    target = [s for s in states if "air_temp" in s.entity_id][0]
    # 75F converted to Celsius is approx 23.89
    assert float(target.state) == pytest.approx(23.89, abs=0.1)

async def test_water_temperature_sensor(hass: HomeAssistant, init_integration) -> None:
    """Test the water temperature sensor reads the BoW water temp."""
    states = hass.states.async_all("sensor")
    target = [s for s in states if "water_temp" in s.entity_id][0]
    # 80F converted to Celsius is approx 26.67
    assert float(target.state) == pytest.approx(26.67, abs=0.1)

async def test_chlorinator_salt_sensors(hass: HomeAssistant, init_integration) -> None:
    """Test the chlorinator salt level sensors."""
    states = hass.states.async_all("sensor")
    # Finding the 'Chlor' instant salt level
    target = [s for s in states if "chlor" in s.entity_id and "instant" in s.entity_id][0]
    assert target.state == "3200"

async def test_csad_ph_sensor(hass: HomeAssistant, init_integration) -> None:
    """Test the CSAD pH sensor."""
    states = hass.states.async_all("sensor")
    # CSAD with type ACID creates a pH sensor. Naming might be 'Pool CSAD' or similar.
    ph_states = [s for s in states if "csad" in s.entity_id and "orp" not in s.entity_id]
    assert len(ph_states) >= 1
    state = ph_states[0]
    assert state.state == "7.5"
