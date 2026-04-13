"""Test the OmniLogic Local sensor platform using generated fixtures."""

import pytest
from homeassistant.core import HomeAssistant
from .generator import OmniLogicFixtureGenerator

pytestmark = pytest.mark.asyncio

@pytest.fixture
def generated_fixtures():
    """Generate custom XML fixtures for sensing."""
    gen = OmniLogicFixtureGenerator()
    gen.add_air_sensor(temp=68)
    gen.add_pool(name="Testing Pool", water_temp=82)
    gen.add_filter_pump(speed=100)
    gen.add_chlorinator(timed_percent=45)
    
    return gen.dump_msp_config(), gen.dump_telemetry()

async def test_sensors_dynamic(hass: HomeAssistant, generated_fixtures, init_integration_dynamic) -> None:
    """Test sensors with dynamically generated data."""
    # Note: init_integration_dynamic would be a version of init_integration 
    # that accepts the XMLs as arguments instead of from fixed fixtures.
    # For this demo, let's assume we've updated init_integration or use a simpler patch.
    
    states = hass.states.async_all("sensor")
    
    # Verify Air Temp
    air_temp = [s for s in states if "airsensor" in s.entity_id.lower()][0]
    # 68°F -> ~20°C
    assert float(air_temp.state) == pytest.approx(20.0, abs=0.1)
    
    # Verify Salt Level (Default in generator is 3200)
    salt = [s for s in states if "salt" in s.entity_id.lower()][0]
    assert salt.state == "3200"
