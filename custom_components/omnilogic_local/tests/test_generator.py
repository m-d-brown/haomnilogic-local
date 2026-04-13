"""Test the OmniLogic fixture generator."""

from .generator import OmniLogicFixtureGenerator

def test_generator_basic() -> None:
    """Test basic XML generation."""
    gen = OmniLogicFixtureGenerator()
    gen.add_air_sensor(temp=72)
    gen.add_pool(name="Pool", water_temp=82)
    gen.add_filter_pump(speed=100)
    
    msp = gen.dump_msp_config()
    tele = gen.dump_telemetry()
    
    assert "Backyard" in msp
    assert "Pool" in msp
    assert "Filter Pump" in msp
    assert 'airTemp="72"' in tele
    assert 'waterTemp="82"' in tele
    assert 'filterSpeed="100"' in tele

def test_multi_bow() -> None:
    """Test multiple bodies of water."""
    gen = OmniLogicFixtureGenerator()
    gen.add_pool("Pool", water_temp=80)
    gen.add_filter_pump("Pool Pump")
    
    gen.add_pool("Spa", water_temp=100)
    gen.add_filter_pump("Spa Pump")
    
    msp = gen.dump_msp_config()
    tele = gen.dump_telemetry()
    
    assert "Pool" in msp
    assert "Spa" in msp
    assert 'waterTemp="80"' in tele
    assert 'waterTemp="100"' in tele
