"""Test the OmniLogic Local config flow."""

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME, CONF_PORT, CONF_TIMEOUT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.omnilogic_local.config_flow import CannotConnect, OmniLogicTimeout
from custom_components.omnilogic_local.const import DOMAIN


pytestmark = pytest.mark.asyncio


async def test_form_shows_on_init(hass: HomeAssistant) -> None:
    """Test the config flow shows a form when initiated."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}


async def test_form_creates_entry(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test a successful config flow creates an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_IP_ADDRESS: "127.0.0.1",
            CONF_PORT: 10444,
            CONF_NAME: "Mock Omni",
            CONF_TIMEOUT: 5.0,
        },
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Mock Omni"
    assert result2["data"][CONF_IP_ADDRESS] == "127.0.0.1"
    assert result2["data"][CONF_PORT] == 10444
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_timeout(hass: HomeAssistant) -> None:
    """Test we handle connection timeout."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.omnilogic_local.config_flow.OmniLogicAPI.async_get_config",
        side_effect=TimeoutError,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.4",
                CONF_PORT: 10444,
                CONF_NAME: "Timeout Omni",
                CONF_TIMEOUT: 5.0,
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "timeout"}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.omnilogic_local.config_flow.OmniLogicAPI.async_get_config",
        side_effect=ConnectionError("refused"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.4",
                CONF_PORT: 10444,
                CONF_NAME: "Bad Omni",
                CONF_TIMEOUT: 5.0,
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_unknown_error(hass: HomeAssistant) -> None:
    """Test we handle unexpected errors.

    The validate_input function catches TimeoutError and Exception from
    async_get_config, but async_get_telemetry errors propagate up to
    the config flow's broad except, producing 'unknown'.
    """
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.omnilogic_local.config_flow.validate_input",
        side_effect=RuntimeError("something weird"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.4",
                CONF_PORT: 10444,
                CONF_NAME: "Err Omni",
                CONF_TIMEOUT: 5.0,
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}
