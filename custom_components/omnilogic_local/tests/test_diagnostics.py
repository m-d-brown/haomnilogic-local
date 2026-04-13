"""Test the OmniLogic Local diagnostics."""

import pytest

from homeassistant.components.diagnostics import REDACTED
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

    # Verify basic data presence
    assert "Pool" in diag["msp_config"]
    assert "66" in diag["telemetry"]
