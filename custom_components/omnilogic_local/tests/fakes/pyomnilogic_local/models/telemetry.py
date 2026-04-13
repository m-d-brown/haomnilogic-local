from __future__ import annotations
from typing import Any, TypeAlias, cast
from pydantic.v1 import BaseModel, Field
from pyomnilogic_local.omnitypes import (
    OmniType,
    BackyardState,
    ChlorinatorOperatingMode,
    ColorLogicBrightness,
    ColorLogicPowerState,
    ColorLogicShow,
    ColorLogicSpeed,
    FilterState,
    FilterValvePosition,
    FilterWhyOn,
    HeaterMode,
    HeaterState,
    PumpState,
    RelayState,
    ValveActuatorState,
)

class TelemetryBase(BaseModel):
    system_id: int = Field(alias="@systemId", default=0)
    
    class Config:
        allow_population_by_field_name = True

    def __iter__(self):
        return iter(self.__dict__.items())

class TelemetryBackyard(TelemetryBase):
    omni_type: OmniType = OmniType.BACKYARD
    status_version: int = Field(alias="@statusVersion", default=11)
    air_temp: int = Field(alias="@airTemp", default=75)
    state: BackyardState = Field(alias="@state", default=BackyardState.ON)
    config_checksum: int | None = Field(alias="@ConfigChksum", default=None)
    msp_version: str | None = Field(alias="@mspVersion", default=None)

class TelemetryBoW(TelemetryBase):
    omni_type: OmniType = OmniType.BOW
    water_temp: int = Field(alias="@waterTemp", default=80)
    flow: int = Field(alias="@flow", default=1)

class TelemetryChlorinator(TelemetryBase):
    omni_type: OmniType = OmniType.CHLORINATOR
    status_raw: int = Field(alias="@status", default=0)
    instant_salt_level: int = Field(alias="@instantSaltLevel", default=3200)
    avg_salt_level: int = Field(alias="@avg_salt_level", default=3200)
    chlr_alert: int = Field(alias="@chlrAlert", default=0)
    chlr_error: int = Field(alias="@chlrError", default=0)
    sc_mode: int = Field(alias="@scMode", default=0)
    operating_state: int = Field(alias="@operatingState", default=0)
    timed_percent: int | None = Field(alias="@Timed-Percent", default=50)
    operating_mode: ChlorinatorOperatingMode = Field(alias="@operatingMode", default=ChlorinatorOperatingMode.TIMED)
    enable: bool = Field(alias="@enable", default=True)

class TelemetryCSAD(TelemetryBase):
    omni_type: OmniType = OmniType.CSAD
    status_raw: int = Field(alias="@status", default=0)
    ph: float = Field(alias="@ph", default=7.5)
    orp: int = Field(alias="@orp", default=700)
    mode: int = Field(alias="@mode", default=0)

class TelemetryColorLogicLight(TelemetryBase):
    omni_type: OmniType = OmniType.CL_LIGHT
    state: ColorLogicPowerState = Field(alias="@lightState", default=ColorLogicPowerState.OFF)
    show: ColorLogicShow = Field(alias="@currentShow", default=ColorLogicShow.VOODOO_LOUNGE)
    speed: ColorLogicSpeed = Field(alias="@speed", default=ColorLogicSpeed.ONE_TIMES)
    brightness: ColorLogicBrightness = Field(alias="@brightness", default=ColorLogicBrightness.ONE_HUNDRED_PERCENT)
    special_effect: int = Field(alias="@specialEffect", default=0)

class TelemetryFilter(TelemetryBase):
    omni_type: OmniType = OmniType.FILTER
    state: FilterState = Field(alias="@filterState", default=FilterState.OFF)
    speed: int = Field(alias="@filterSpeed", default=50)
    valve_position: FilterValvePosition = Field(alias="@valvePosition", default=FilterValvePosition.POOL_ONLY)
    why_on: FilterWhyOn = Field(alias="@whyFilterIsOn", default=FilterWhyOn.OFF)
    reported_speed: int = Field(alias="@reportedFilterSpeed", default=50)
    power: int = Field(alias="@power", default=0)
    last_speed: int = Field(alias="@lastSpeed", default=50)

class TelemetryGroup(TelemetryBase):
    omni_type: OmniType = OmniType.GROUP
    state: int = Field(alias="@groupState", default=0)

class TelemetryHeater(TelemetryBase):
    omni_type: OmniType = OmniType.HEATER
    state: HeaterState = Field(alias="@heaterState", default=HeaterState.ON)
    temp: int = Field(alias="@temp", default=80)
    enabled: bool = Field(alias="@enable", default=True)
    priority: int = Field(alias="@priority", default=1)
    maintain_for: int = Field(alias="@maintainFor", default=24)

class TelemetryPump(TelemetryBase):
    omni_type: OmniType = OmniType.PUMP
    state: PumpState = Field(alias="@pumpState", default=PumpState.ON)
    speed: int = Field(alias="@pumpSpeed", default=50)
    last_speed: int = Field(alias="@lastSpeed", default=50)
    why_on: int = Field(alias="@whyOn", default=0)

class TelemetryRelay(TelemetryBase):
    omni_type: OmniType = OmniType.RELAY
    state: RelayState = Field(alias="@relayState", default=RelayState.ON)
    why_on: int = Field(alias="@whyOn", default=0)

class TelemetryValveActuator(TelemetryBase):
    omni_type: OmniType = OmniType.VALVE_ACTUATOR
    state: ValveActuatorState = Field(alias="@valveActuatorState", default=ValveActuatorState.ON)
    why_on: int = Field(alias="@whyOn", default=0)

class TelemetryVirtualHeater(TelemetryBase):
    omni_type: OmniType = OmniType.VIRT_HEATER
    current_set_point: int = Field(alias="@Current-Set-Point", default=85)
    enabled: bool = Field(alias="@enable", default=True)
    solar_set_point: int = Field(alias="@SolarSetPoint", default=90)
    mode: HeaterMode = Field(alias="@Mode", default=HeaterMode.HEAT)
    silent_mode: int = Field(alias="@SilentMode", default=0)
    why_on: int = Field(alias="@whyHeaterIsOn", default=0)

TelemetryType: TypeAlias = (
    TelemetryBackyard
    | TelemetryBoW
    | TelemetryChlorinator
    | TelemetryCSAD
    | TelemetryColorLogicLight
    | TelemetryFilter
    | TelemetryGroup
    | TelemetryHeater
    | TelemetryPump
    | TelemetryRelay
    | TelemetryValveActuator
    | TelemetryVirtualHeater
)

class Telemetry(BaseModel):
    version: str = Field(alias="@version", default="1.11")
    backyard: TelemetryBackyard = Field(alias="Backyard", default_factory=TelemetryBackyard)
    bow: list[TelemetryBoW] = Field(alias="BodyOfWater", default_factory=list)
    chlorinator: list[TelemetryChlorinator] | None = Field(alias="Chlorinator", default_factory=list)
    colorlogic_light: list[TelemetryColorLogicLight] | None = Field(alias="ColorLogic-Light", default_factory=list)
    csad: list[TelemetryCSAD] | None = Field(alias="CSAD", default_factory=list)
    filter: list[TelemetryFilter] | None = Field(alias="Filter", default_factory=list)
    group: list[TelemetryGroup] | None = Field(alias="Group", default_factory=list)
    heater: list[TelemetryHeater] | None = Field(alias="Heater", default_factory=list)
    pump: list[TelemetryPump] | None = Field(alias="Pump", default_factory=list)
    relay: list[TelemetryRelay] | None = Field(alias="Relay", default_factory=list)
    valve_actuator: list[TelemetryValveActuator] | None = Field(alias="ValveActuator", default_factory=list)
    virtual_heater: list[TelemetryVirtualHeater] | None = Field(alias="VirtualHeater", default_factory=list)

    class Config:
        allow_population_by_field_name = True

    def __iter__(self):
        return iter(self.__dict__.items())

    @staticmethod
    def load_xml(xml: str) -> Telemetry:
        return Telemetry.construct()

    @staticmethod
    def load_json(data: dict[str, Any]) -> Telemetry:
        return Telemetry.construct()

    def get_telem_by_systemid(self, system_id: int) -> TelemetryType | None:
        for field_name, value in self:
            if field_name == "version" or value is None:
                continue
            if isinstance(value, list):
                for model in value:
                    cast_model = cast(TelemetryType, model)
                    if hasattr(cast_model, "system_id") and cast_model.system_id == system_id:
                        return cast_model
            else:
                cast_model = cast(TelemetryType, value)
                if hasattr(cast_model, "system_id") and cast_model.system_id == system_id:
                    return cast_model
        return None
