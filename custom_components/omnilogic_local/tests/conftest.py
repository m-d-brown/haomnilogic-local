"""Conftest for OmniLogic Local integration."""

import logging
import sys
from pathlib import Path

from homeassistant.setup import async_setup_component

# Inject our fakes directory into sys.path so it takes precedence over the real library
FAKES_PATH = str(Path(__file__).parent / "fakes")

# Clear any existing local cache of the library to ensure our fakes are used
for module_name in list(sys.modules.keys()):
    if module_name.startswith("pyomnilogic_local"):
        del sys.modules[module_name]

# Ensure the root directory is in sys.path so Home Assistant can find custom_components
ROOT_PATH = str(Path(__file__).parent.parent.parent.parent)
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

if FAKES_PATH in sys.path:
    sys.path.remove(FAKES_PATH)
sys.path.insert(0, FAKES_PATH)

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL, CONF_TIMEOUT
from homeassistant.core import HomeAssistant
from pyomnilogic_local.api import OmniLogic
from pyomnilogic_local.models.mspconfig import MSPConfig, MSPSystem
from pyomnilogic_local.models.telemetry import Telemetry
from pyomnilogic_local.omnitypes import (
    ChlorinatorDispenserType,
    ChlorinatorOperatingMode,
    ColorLogicLightType,
    CSADType,
    FilterType,
    SensorType,
    SensorUnits,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from ..const import DOMAIN

# Import our mock factories using local relative path
from .mock_models import (
    create_mock_backyard,
    create_mock_bow,
    create_mock_chlorinator,
    create_mock_filter,
    create_mock_heater,
    create_mock_light,
    create_mock_relay,
    create_mock_sensor,
)

_LOGGER = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_omni_data():
    """Build a high-fidelity mock dataset using our Shadow Library models."""
    # Backyard
    backyard = create_mock_backyard()

    air_temp = create_mock_sensor(system_id=1, name="Air Temp", bow_id=None, type=SensorType.AIR_TEMP, units=SensorUnits.FAHRENHEIT)

    water_temp = create_mock_sensor(system_id=2, name="Water Temp", bow_id=3, type=SensorType.WATER_TEMP, units=SensorUnits.FAHRENHEIT)

    pool = create_mock_bow(system_id=3, name="Pool")

    filter_pump = create_mock_filter(system_id=6, name="Filter", bow_id=3, type=FilterType.VARIABLE_SPEED)

    heater = create_mock_heater(system_id=7, name="Heater", bow_id=3)

    flow_sensor = create_mock_sensor(system_id=4, name="Flow", bow_id=3, type=SensorType.FLOW)

    pool_light = create_mock_light(system_id=9, name="Light", bow_id=3, type=ColorLogicLightType.UCL)

    chlorinator = create_mock_chlorinator(system_id=10, name="Chlor", bow_id=3, dispenser_type=ChlorinatorDispenserType.SALT)
    chlorinator.telemetry.operating_mode = ChlorinatorOperatingMode.TIMED

    waterfall = create_mock_relay(system_id=12, name="Waterfall", bow_id=3)

    csad = create_mock_sensor(system_id=11, name="CSAD", bow_id=3, type=CSADType.ACID, units=SensorUnits.NO_UNITS)

    msp = MSPConfig(
        system=MSPSystem(vsp_speed_format="Percent", units="Standard"),
        backyard=backyard.msp_config,
    )
    backyard.msp_config.sensor[(backyard.msp_config.system_id, air_temp.msp_config.system_id)] = air_temp.msp_config
    backyard.msp_config.bow[(backyard.msp_config.system_id, pool.msp_config.system_id)] = pool.msp_config
    pool.msp_config.filter[(pool.msp_config.system_id, filter_pump.msp_config.system_id)] = filter_pump.msp_config
    pool.msp_config.heater[(pool.msp_config.system_id, heater.msp_config.system_id)] = heater.msp_config
    pool.msp_config.heater_equipment[(pool.msp_config.system_id, heater.msp_config.system_id)] = heater.msp_config
    pool.msp_config.sensor[(pool.msp_config.system_id, water_temp.msp_config.system_id)] = water_temp.msp_config
    pool.msp_config.sensor[(pool.msp_config.system_id, flow_sensor.msp_config.system_id)] = flow_sensor.msp_config
    pool.msp_config.sensor[(pool.msp_config.system_id, csad.msp_config.system_id)] = csad.msp_config
    pool.msp_config.chlorinator[(pool.msp_config.system_id, chlorinator.msp_config.system_id)] = chlorinator.msp_config
    pool.msp_config.chlorinator_equipment[(pool.msp_config.system_id, chlorinator.msp_config.system_id)] = chlorinator.msp_config
    pool.msp_config.color_logic_light[(pool.msp_config.system_id, pool_light.msp_config.system_id)] = pool_light.msp_config
    pool.msp_config.relay[(pool.msp_config.system_id, waterfall.msp_config.system_id)] = waterfall.msp_config
    pool.msp_config.csad[(pool.msp_config.system_id, csad.msp_config.system_id)] = csad.msp_config

    telemetry = Telemetry()
    telemetry.backyard = backyard.telemetry
    telemetry.backyard.state = 1  # BackyardState.ON
    telemetry.backyard.air_temp = 75

    telemetry.bow = [pool.telemetry]
    pool.telemetry.water_temp = 80
    pool.telemetry.flow = 1

    telemetry.filter = [filter_pump.telemetry]
    telemetry.heater = [heater.telemetry]
    telemetry.chlorinator = [chlorinator.telemetry]
    telemetry.color_logic_light = [pool_light.telemetry]
    telemetry.relay = [waterfall.telemetry]
    telemetry.sensor = [air_temp.telemetry, water_temp.telemetry, flow_sensor.telemetry, csad.telemetry]

    csad.telemetry.ph = 7.5

    return msp, telemetry


@pytest.fixture
async def init_integration(hass: HomeAssistant, mock_omni_data):
    """Initialize the integration using our FakeOmniLogicAPI and Shadow Library data."""
    _LOGGER.info("DEBUG: init_integration fixture called")

    mock_msp_config, mock_telemetry = mock_omni_data

    # High-fidelity mock API that tracks state change in-memory
    mock_api = OmniLogic("127.0.0.1", 6103, 5.0)
    mock_api.msp_config = mock_msp_config
    mock_api.telemetry = mock_telemetry

    # Patch the real API class to use our fake
    with (
        patch("custom_components.omnilogic_local.config_flow.OmniLogic", return_value=mock_api),
        patch("custom_components.omnilogic_local.OmniLogic", return_value=mock_api),
        patch("pyomnilogic_local.models.mspconfig.MSPConfig.load_xml", return_value=mock_msp_config),
        patch("pyomnilogic_local.models.telemetry.Telemetry.load_xml", return_value=mock_telemetry),
    ):
        # Force import to see any errors
        try:
            import custom_components.omnilogic_local

            _LOGGER.info(f"DEBUG: Successfully imported {custom_components.omnilogic_local}")
        except Exception as e:
            _LOGGER.error(f"DEBUG: Failed to import: {e}")

        # Ensure the component is correctly registered in Hass before setting up the entry
        setup_result = await async_setup_component(hass, DOMAIN, {})
        _LOGGER.info(f"DEBUG: async_setup_component result: {setup_result}")
        await hass.async_block_till_done()

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_IP_ADDRESS: "127.0.0.1",
                CONF_PORT: 6103,
                CONF_NAME: "Test Omni",
                CONF_TIMEOUT: 5.0,
                CONF_SCAN_INTERVAL: 60,
            },
            title="Test Omni",
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Ensure the coordinator has been set up successfully
        entry_id = entry.entry_id
        if DOMAIN in hass.data and entry_id in hass.data[DOMAIN]:
            # No need to set msp_config/telemetry on coordinator anymore as it uses omni object
            pass

        yield entry


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Override async_setup_entry."""
    with patch("custom_components.omnilogic_local.async_setup_entry", return_value=True) as mock_setup_entry:
        yield mock_setup_entry
