"""Expanded tests for the OmniLogic Local number platform using model-layer mocking."""

from unittest.mock import ANY

import pytest

from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.omnilogic_local.const import DOMAIN, KEY_COORDINATOR
from custom_components.omnilogic_local.tests.mock_models import (
    create_mock_backyard,
    create_mock_bow,
    create_mock_chlorinator,
    create_mock_filter,
    create_mock_heater,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_omni_data():
    """Provide mocked OmniLogic data with multiple number-capable entities."""
    backyard = create_mock_backyard()
    pool = create_mock_bow(system_id=1, name="Pool")
    # VSP Pump (Filter)
    filter_pump = create_mock_filter(system_id=2, name="Main Filter", bow_id=1)
    # Virtual Heater (for Solar Set Point)
    heater = create_mock_heater(system_id=3, name="Pool Heater", bow_id=1)
    # Chlorinator
    chlor = create_mock_chlorinator(system_id=4, name="Chlorinator", bow_id=1)

    return {
        0: backyard,
        1: pool,
        2: filter_pump,
        3: heater,
        4: chlor,
    }


async def test_vsp_set_value(hass: HomeAssistant, init_integration) -> None:
    """Test setting a value for a VSP number entity."""
    entry_id = init_integration.entry_id
    coordinator = hass.data[DOMAIN][entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all(NUMBER_DOMAIN)
    target = next(s for s in states if "main_filter_speed" in s.entity_id)

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: target.entity_id, ATTR_VALUE: 75},
        blocking=True,
    )

    mock_api.async_set_equipment.assert_called_with(
        target.attributes["omni_bow_id"],
        target.attributes["omni_system_id"],
        75,
    )


async def test_solar_set_point_set_value(hass: HomeAssistant, init_integration) -> None:
    """Test setting a value for a solar set point number entity."""
    entry_id = init_integration.entry_id
    coordinator = hass.data[DOMAIN][entry_id][KEY_COORDINATOR]
    mock_api = coordinator.omni_api

    states = hass.states.async_all(NUMBER_DOMAIN)
    target = next(s for s in states if "solar_set_point" in s.entity_id)

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: target.entity_id, ATTR_VALUE: 90},
        blocking=True,
    )

    mock_api.async_set_solar_heater.assert_called_with(
        target.attributes["omni_bow_id"],
        target.attributes["omni_system_id"],
        90,
        unit=ANY,
    )
