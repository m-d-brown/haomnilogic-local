from __future__ import annotations

import logging
from typing import Any, Optional

from .models.mspconfig import MSPConfig, OmniBase
from .models.telemetry import Telemetry
from .omnitypes import ColorLogicBrightness, ColorLogicShow, ColorLogicSpeed, HeaterMode
from .utils import DiscoveryDict

_LOGGER = logging.getLogger(__name__)


class OmniLogic:
    def __init__(self, ip_address: str, port: int, timeout: float):
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self._msp_config: Optional[MSPConfig] = None
        self._telemetry: Optional[Telemetry] = None
        self.state: dict[str | int, Any] = {}
        # Stub for diagnostics.py which expects _api
        self._api = self

    @property
    def msp_config(self) -> Optional[MSPConfig]:
        return self._msp_config

    @msp_config.setter
    def msp_config(self, value: MSPConfig) -> None:
        self._msp_config = value

    @property
    def telemetry(self) -> Optional[Telemetry]:
        return self._telemetry

    @telemetry.setter
    def telemetry(self, value: Telemetry) -> None:
        self._telemetry = value

    def _get_all_of_type(self, model_class: Any) -> DiscoveryDict:
        """Helper to find all equipment of a given type in the MSPConfig."""
        if not self._msp_config:
            return DiscoveryDict()

        results = DiscoveryDict()
        # Simple walk of the MSPConfig tree assuming Backyard -> BoW -> Equipment
        backyard_id = self._msp_config.backyard.system_id

        # Backyard level equipment
        for field in ["sensor", "csad"]:
            value = getattr(self._msp_config.backyard, field, [])
            for item in value:
                if isinstance(item, model_class):
                    # For backyard level, we use backyard_id as the first part of the key
                    results[(backyard_id, item.system_id)] = item

        # BoW level equipment
        for bow in self._msp_config.backyard.bow:
            bow_id = bow.system_id
            for field in [
                "filter",
                "heater",
                "heater_equipment",
                "sensor",
                "chlorinator",
                "chlorinator_equipment",
                "color_logic_light",
                "relay",
                "csad",
            ]:
                value = getattr(bow, field, [])
                for item in value:
                    if isinstance(item, model_class):
                        results[(bow_id, item.system_id)] = item

        return results

    @property
    def backyard(self) -> Any:
        if self._msp_config:
            return self._msp_config.backyard
        return None

    @property
    def all_backyards(self) -> DiscoveryDict:
        res = DiscoveryDict()
        if self._msp_config:
            # key: (0, backyard_id)
            res[(0, self._msp_config.backyard.system_id)] = self._msp_config.backyard
        return res

    @property
    def all_bows(self) -> DiscoveryDict:
        res = DiscoveryDict()
        if not self._msp_config:
            return res
        backyard_id = self._msp_config.backyard.system_id
        for bow in self._msp_config.backyard.bow:
            res[(backyard_id, bow.system_id)] = bow
        return res

    @property
    def all_sensors(self) -> DiscoveryDict:
        from .models.mspconfig import MSPSensor

        return self._get_all_of_type(MSPSensor)

    @property
    def all_heater_equipment(self) -> DiscoveryDict:
        from .models.mspconfig import MSPHeaterEquip

        return self._get_all_of_type(MSPHeaterEquip)

    @property
    def all_heaters(self) -> DiscoveryDict:
        from .models.mspconfig import MSPHeater

        return self._get_all_of_type(MSPHeater)

    @property
    def all_lights(self) -> DiscoveryDict:
        from .models.mspconfig import MSPColorLogicLight

        return self._get_all_of_type(MSPColorLogicLight)

    @property
    def all_filters(self) -> DiscoveryDict:
        from .models.mspconfig import MSPFilter

        return self._get_all_of_type(MSPFilter)

    @property
    def all_pumps(self) -> DiscoveryDict:
        from .models.mspconfig import MSPPump

        return self._get_all_of_type(MSPPump)

    @property
    def all_relays(self) -> DiscoveryDict:
        from .models.mspconfig import MSPRelay

        return self._get_all_of_type(MSPRelay)

    @property
    def all_csads(self) -> DiscoveryDict:
        from .models.mspconfig import MSPCSAD

        return self._get_all_of_type(MSPCSAD)

    @property
    def all_virtual_heaters(self) -> DiscoveryDict:
        from .models.mspconfig import MSPVirtualHeater

        return self._get_all_of_type(MSPVirtualHeater)

    @property
    def all_chlorinators(self) -> DiscoveryDict:
        from .models.mspconfig import MSPChlorinator

        return self._get_all_of_type(MSPChlorinator)

    @property
    def all_chlorinator_equipment(self) -> DiscoveryDict:
        from .models.mspconfig import MSPChlorinatorEquip

        return self._get_all_of_type(MSPChlorinatorEquip)

    async def refresh(self, force: bool = False) -> None:
        _LOGGER.debug("FakeOmniLogic: refresh called (force: %s)", force)
        # In the real library, this updates msp_config and telemetry
        # In our fake, we assume they are already set or patched by the test

    def get_equipment_by_id(self, system_id: int) -> Optional[OmniBase]:
        """Recursive search for equipment by system ID."""
        if not self._msp_config:
            return None

        def _walk(base: Any) -> Optional[OmniBase]:
            if hasattr(base, "system_id") and base.system_id == system_id:
                return base

            # Use the model's fields to find sub-items
            # This is a bit simplified compared to the real library but should work for tests
            for field_name in [
                "sensor",
                "bow",
                "filter",
                "heater",
                "chlorinator",
                "color_logic_light",
                "relay",
                "valve_actuator",
                "virtual_heater",
                "schedule",
                "favorites",
                "group",
            ]:
                items = getattr(base, field_name, [])
                if isinstance(items, list):
                    for item in items:
                        res = _walk(item)
                        if res:
                            return res
                elif items:
                    res = _walk(items)
                    if res:
                        return res
            return None

        # Start walk from backyard and system (if system has id)
        res = _walk(self._msp_config.backyard)
        if res:
            return res
        return _walk(self._msp_config.system)

    async def async_get_config(self, raw: bool = False) -> str:
        _LOGGER.debug("FakeOmniLogic: async_get_config called")
        return "<mock_msp_config/>"

    async def async_get_mspconfig(self, raw: bool = False) -> str:
        return await self.async_get_config(raw=raw)

    async def async_get_telemetry(self, raw: bool = False) -> str:
        _LOGGER.debug("FakeOmniLogic: async_get_telemetry called")
        return "<mock_telemetry/>"

    async def async_set_equipment(self, bow_id: int, system_id: int, state: bool | int) -> None:
        _LOGGER.debug("FakeOmniLogic: async_set_equipment called (bow_id: %s, system_id: %s, state: %s)", bow_id, system_id, state)
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
            "FakeOmniLogic: async_set_light_show called (bow_id: %s, system_id: %s, show: %s, speed: %s, brightness: %s)",
            bow_id,
            system_id,
            show,
            speed,
            brightness,
        )
        self.state[system_id] = {"show": show, "speed": speed, "brightness": brightness}
        self.state[f"light_show_{system_id}"] = show

    async def async_set_filter_speed(self, bow_id: int, system_id: int, speed: int) -> None:
        _LOGGER.debug("FakeOmniLogic: async_set_filter_speed called (bow_id: %s, system_id: %s, speed: %s)", bow_id, system_id, speed)
        self.state[system_id] = speed
        self.state[f"speed_{system_id}"] = speed

    async def async_set_heater(self, bow_id: int, system_id: int, temp: int, unit: str = "F") -> None:
        _LOGGER.debug(
            "FakeOmniLogic: async_set_heater called (bow_id: %s, system_id: %s, temp: %s, unit: %s)", bow_id, system_id, temp, unit
        )
        self.state[f"set_point_{system_id}"] = temp

    async def async_set_heater_enable(self, bow_id: int, system_id: int, enabled: bool | int) -> None:
        _LOGGER.debug("FakeOmniLogic: async_set_heater_enable called (bow_id: %s, system_id: %s, enabled: %s)", bow_id, system_id, enabled)
        self.state[f"heater_enable_{system_id}"] = bool(enabled)

    async def async_set_heater_mode(self, bow_id: int, system_id: int, mode: HeaterMode) -> None:
        _LOGGER.debug("FakeOmniLogic: async_set_heater_mode called (bow_id: %s, system_id: %s, mode: %s)", bow_id, system_id, mode)
        self.state[system_id] = mode

    async def async_set_chlorinator_enable(self, bow_id: int, enabled: bool | int) -> None:
        _LOGGER.debug("FakeOmniLogic: async_set_chlorinator_enable called (bow_id: %s, enabled: %s)", bow_id, enabled)
        self.state[f"chlor_enable_{bow_id}"] = bool(enabled)

    async def async_set_chlorinator_params(self, pool_id: int, equipment_id: int, timed_percent: int, **kwargs: Any) -> None:
        _LOGGER.debug(
            "FakeOmniLogic: async_set_chlorinator_params called (pool_id: %s, equipment_id: %s, timed_percent: %s)",
            pool_id,
            equipment_id,
            timed_percent,
        )
        self.state[equipment_id] = timed_percent
        self.state[f"timed_percent_{equipment_id}"] = timed_percent

    async def async_set_chlorinator_superchlorinate(self, bow_id: int, system_id: int, enabled: bool | int) -> None:
        _LOGGER.debug(
            "FakeOmniLogic: async_set_chlorinator_superchlorinate called (bow_id: %s, system_id: %s, enabled: %s)",
            bow_id,
            system_id,
            enabled,
        )
        self.state[f"superchlor_{system_id}"] = bool(enabled)

    async def async_set_solar_heater(self, bow_id: int, system_id: int, temp: int, unit: str = "F") -> None:
        _LOGGER.debug(
            "FakeOmniLogic: async_set_solar_heater called (bow_id: %s, system_id: %s, temp: %s, unit: %s)", bow_id, system_id, temp, unit
        )
        self.state[f"solar_set_point_{system_id}"] = temp
