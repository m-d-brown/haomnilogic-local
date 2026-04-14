"""Test the OmniLogic Local diagnostics."""

import pytest

from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.diagnostics import async_get_config_entry_diagnostics

pytestmark = pytest.mark.asyncio

async def test_diagnostics(hass: HomeAssistant, init_integration) -> None:
    """Test diagnostics export."""
    diag = await async_get_config_entry_diagnostics(hass, init_integration)

    assert "config" in diag
    assert "msp_config" in diag
    assert "telemetry" in diag
    assert "data" in diag

    # Verify that we've correctly mocked the coordinator attributes
    assert diag["msp_config"] == "<mock_msp_config/>"
    assert diag["telemetry"] == "<mock_telemetry/>"
    
    # Verify that the internal data dictionary is present and contains our mock entities
    assert len(diag["data"]) > 0
