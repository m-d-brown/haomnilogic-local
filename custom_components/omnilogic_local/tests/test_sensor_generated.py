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

@pytest.fixture
def msp_config_xml(generated_fixtures):
    return generated_fixtures[0]

@pytest.fixture
def telemetry_xml(generated_fixtures):
    return generated_fixtures[1]

async def test_sensors_dynamic(hass: HomeAssistant, init_integration) -> None:
    """Test sensors with dynamically generated data."""
    states = hass.states.async_all("sensor")
    
    # Verify Air Temp
    air_temp = [s for s in states if "airsensor" in s.entity_id.lower()][0]
    # 68°F -> ~20°C (Home Assistant converts based on system units)
    # The integration uses whatever the system config says.
    assert float(air_temp.state) == pytest.approx(20.0, abs=0.1)
    
    # Verify Salt Level (Default in generator is 3200)
    salt = [s for s in states if "saltlevel" in s.entity_id.lower()][0]
    assert salt.state == "3200"
