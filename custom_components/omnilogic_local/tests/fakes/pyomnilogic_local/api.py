import logging
from typing import Any
from .omnitypes import ColorLogicShow, ColorLogicSpeed, ColorLogicBrightness, HeaterMode

_LOGGER = logging.getLogger(__name__)

class OmniLogicAPI:
    def __init__(self, ip_address: str, port: int, timeout: float):
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.state: dict[str | int, Any] = {}

    async def async_get_config(self, raw: bool = False) -> str:
        _LOGGER.debug("FakeOmniLogicAPI: async_get_config called")
        return "<dummy_config/>"

    async def async_get_telemetry(self, raw: bool = False) -> str:
        _LOGGER.debug("FakeOmniLogicAPI: async_get_telemetry called")
        return "<dummy_telemetry/>"

    async def async_set_equipment(self, bow_id: int, system_id: int, state: bool | int) -> None:
        _LOGGER.debug("FakeOmniLogicAPI: async_set_equipment called (bow_id: %s, system_id: %s, state: %s)", bow_id, system_id, state)
        self.state[system_id] = state

    async def async_set_light_show(
        self,
        bow_id: int,
        system_id: int,
        show: ColorLogicShow | int,
        speed: ColorLogicSpeed | int = ColorLogicSpeed.ONE_TIMES,
        brightness: ColorLogicBrightness | int = ColorLogicBrightness.ONE_HUNDRED_PERCENT,
    ) -> None:
        _LOGGER.debug(
            "FakeOmniLogicAPI: async_set_light_show called (bow_id: %s, system_id: %s, show: %s, speed: %s, brightness: %s)",
            bow_id, system_id, show, speed, brightness
        )
        self.state[system_id] = {"show": show, "speed": speed, "brightness": brightness}
        # Also set a simple key for verification
        self.state[f"light_show_{system_id}"] = show

    async def async_set_filter_speed(self, bow_id: int, system_id: int, speed: int) -> None:
        _LOGGER.debug("FakeOmniLogicAPI: async_set_filter_speed called (bow_id: %s, system_id: %s, speed: %s)", bow_id, system_id, speed)
        self.state[system_id] = speed
        self.state[f"speed_{system_id}"] = speed

    async def async_set_heater(self, bow_id: int, system_id: int, temp: int, unit: str = "F") -> None:
        _LOGGER.debug("FakeOmniLogicAPI: async_set_heater called (bow_id: %s, system_id: %s, temp: %s, unit: %s)", bow_id, system_id, temp, unit)
        self.state[f"set_point_{system_id}"] = temp

    async def async_set_heater_enable(self, bow_id: int, system_id: int, enabled: bool | int) -> None:
        _LOGGER.debug("FakeOmniLogicAPI: async_set_heater_enable called (bow_id: %s, system_id: %s, enabled: %s)", bow_id, system_id, enabled)
        self.state[f"heater_enable_{system_id}"] = bool(enabled)

    async def async_set_heater_mode(self, bow_id: int, system_id: int, mode: HeaterMode) -> None:
        _LOGGER.debug("FakeOmniLogicAPI: async_set_heater_mode called (bow_id: %s, system_id: %s, mode: %s)", bow_id, system_id, mode)
        self.state[system_id] = mode

    async def async_set_chlorinator_enable(self, bow_id: int, enabled: bool | int) -> None:
        _LOGGER.debug("FakeOmniLogicAPI: async_set_chlorinator_enable called (bow_id: %s, enabled: %s)", bow_id, enabled)
        self.state[f"chlor_enable_{bow_id}"] = bool(enabled)

    async def async_set_chlorinator_params(self, pool_id: int, equipment_id: int, timed_percent: int, **kwargs: Any) -> None:
        _LOGGER.debug("FakeOmniLogicAPI: async_set_chlorinator_params called (pool_id: %s, equipment_id: %s, timed_percent: %s)", pool_id, equipment_id, timed_percent)
        self.state[equipment_id] = timed_percent
        self.state[f"timed_percent_{equipment_id}"] = timed_percent

    async def async_set_chlorinator_superchlorinate(self, bow_id: int, system_id: int, enabled: bool | int) -> None:
        _LOGGER.debug("FakeOmniLogicAPI: async_set_chlorinator_superchlorinate called (bow_id: %s, system_id: %s, enabled: %s)", bow_id, system_id, enabled)
        self.state[f"superchlor_{system_id}"] = bool(enabled)

    async def async_set_solar_heater(self, bow_id: int, system_id: int, temp: int, unit: str = "F") -> None:
        _LOGGER.debug("FakeOmniLogicAPI: async_set_solar_heater called (bow_id: %s, system_id: %s, temp: %s, unit: %s)", bow_id, system_id, temp, unit)
        self.state[f"solar_set_point_{system_id}"] = temp
