from __future__ import annotations
import logging
from typing import Any, Literal, TypeAlias
from pydantic.v1 import BaseModel, Field
from ..omnitypes import (
    BodyOfWaterType,
    ChlorinatorCellType,
    ChlorinatorDispenserType,
    ColorLogicLightType,
    ColorLogicShow,
    CSADType,
    FilterType,
    HeaterType,
    OmniType,
    PumpFunction,
    PumpType,
    RelayFunction,
    RelayType,
    SensorType,
    SensorUnits,
)

_LOGGER = logging.getLogger(__name__)

class OmniBase(BaseModel):
    system_id: int = Field(alias="System-Id")
    name: str | None = Field(alias="Name")
    bow_id: int | None = None
    
    class Config:
        allow_population_by_field_name = True

class MSPSystem(BaseModel):
    omni_type: OmniType = OmniType.SYSTEM
    vsp_speed_format: Literal["RPM", "Percent"] = Field(alias="Msp-Vsp-Speed-Format", default="Percent")
    units: Literal["Standard", "Metric"] = Field(alias="Units", default="Standard")
    
    class Config:
        allow_population_by_field_name = True

class MSPSensor(OmniBase):
    omni_type: OmniType = OmniType.SENSOR
    type: SensorType | str = Field(alias="Type")
    units: SensorUnits | str = Field(alias="Units")

class MSPFilter(OmniBase):
    omni_type: OmniType = OmniType.FILTER
    type: FilterType | str = Field(alias="Filter-Type")
    max_percent: int = Field(alias="Max-Pump-Speed", default=100)
    min_percent: int = Field(alias="Min-Pump-Speed", default=20)
    max_rpm: int = Field(alias="Max-Pump-RPM", default=3450)
    min_rpm: int = Field(alias="Min-Pump-RPM", default=600)
    priming_enabled: Literal["yes", "no"] = Field(alias="Priming-Enabled", default="yes")
    low_speed: int = Field(alias="Vsp-Low-Pump-Speed", default=30)
    medium_speed: int = Field(alias="Vsp-Medium-Pump-Speed", default=50)
    high_speed: int = Field(alias="Vsp-High-Pump-Speed", default=100)

class MSPPump(OmniBase):
    omni_type: OmniType = OmniType.PUMP
    type: PumpType | str = Field(alias="Type")
    function: PumpFunction | str = Field(alias="Function")
    max_percent: int = Field(alias="Max-Pump-Speed", default=100)
    min_percent: int = Field(alias="Min-Pump-Speed", default=20)
    max_rpm: int = Field(alias="Max-Pump-RPM", default=3450)
    min_rpm: int = Field(alias="Min-Pump-RPM", default=600)
    priming_enabled: Literal["yes", "no"] = Field(alias="Priming-Enabled", default="yes")
    low_speed: int = Field(alias="Vsp-Low-Pump-Speed", default=30)
    medium_speed: int = Field(alias="Vsp-Medium-Pump-Speed", default=50)
    high_speed: int = Field(alias="Vsp-High-Pump-Speed", default=100)

class MSPRelay(OmniBase):
    omni_type: OmniType = OmniType.RELAY
    type: RelayType | str = Field(alias="Type")
    function: RelayFunction | str = Field(alias="Function")

class MSPHeaterEquip(OmniBase):
    omni_type: OmniType = OmniType.HEATER_EQUIP
    type: Literal["PET_HEATER"] = Field(alias="Type", default="PET_HEATER")
    heater_type: HeaterType | str = Field(alias="Heater-Type")
    enabled: Literal["yes", "no"] = Field(alias="Enabled", default="yes")
    min_filter_speed: int = Field(alias="Min-Speed-For-Operation", default=20)
    sensor_id: int = Field(alias="Sensor-System-Id", default=0)
    supports_cooling: Literal["yes", "no"] | None = Field(alias="SupportsCooling", default="no")

class MSPVirtualHeater(OmniBase):
    omni_type: OmniType = OmniType.VIRT_HEATER
    enabled: Literal["yes", "no"] = Field(alias="Enabled", default="yes")
    set_point: int = Field(alias="Current-Set-Point", default=85)
    solar_set_point: int | None = Field(alias="SolarSetPoint", default=None)
    max_temp: int = Field(alias="Max-Settable-Water-Temp", default=104)
    min_temp: int = Field(alias="Min-Settable-Water-Temp", default=50)
    heater_equipment: list[MSPHeaterEquip] | None = Field(default_factory=list)

class MSPChlorinatorEquip(OmniBase):
    omni_type: OmniType = OmniType.CHLORINATOR_EQUIP
    enabled: Literal["yes", "no"] = Field(alias="Enabled", default="yes")

class MSPChlorinator(OmniBase):
    omni_type: OmniType = OmniType.CHLORINATOR
    enabled: Literal["yes", "no"] = Field(alias="Enabled", default="yes")
    timed_percent: int = Field(alias="Timed-Percent", default=50)
    superchlor_timeout: int = Field(alias="SuperChlor-Timeout", default=24)
    orp_timeout: int = Field(alias="ORP-Timeout", default=24)
    dispenser_type: ChlorinatorDispenserType | str = Field(alias="Dispenser-Type", default=ChlorinatorDispenserType.SALT)
    cell_type: ChlorinatorCellType | str = Field(alias="Cell-Type", default=ChlorinatorCellType.T15)
    chlorinator_equipment: list[MSPChlorinatorEquip] | None = Field(default_factory=list)

class MSPCSAD(OmniBase):
    omni_type: OmniType = OmniType.CSAD
    enabled: Literal["yes", "no"] = Field(alias="Enabled", default="yes")
    type: CSADType | str = Field(alias="Type")
    target_value: float = Field(alias="TargetValue", default=7.5)
    calibration_value: float = Field(alias="CalibrationValue", default=0.0)
    ph_low_alarm_value: float = Field(alias="PHLowAlarmLevel", default=7.0)
    ph_high_alarm_value: float = Field(alias="PHHighAlarmLevel", default=8.0)

class MSPColorLogicLight(OmniBase):
    omni_type: OmniType = OmniType.CL_LIGHT
    type: ColorLogicLightType | str = Field(alias="Type")
    v2_active: Literal["yes", "no"] | None = Field(alias="V2-Active", default="no")
    effects: list[ColorLogicShow] | None = Field(default_factory=list)

class MSPBoW(OmniBase):
    omni_type: OmniType = OmniType.BOW
    type: BodyOfWaterType | str = Field(alias="Type")
    supports_spillover: Literal["yes", "no"] = Field(alias="Supports-Spillover", default="no")
    filter: list[MSPFilter] | None = Field(alias="Filter", default_factory=list)
    relay: list[MSPRelay] | None = Field(alias="Relay", default_factory=list)
    heater: MSPVirtualHeater | None = Field(alias="Heater", default=None)
    sensor: list[MSPSensor] | None = Field(alias="Sensor", default_factory=list)
    colorlogic_light: list[MSPColorLogicLight] | None = Field(alias="ColorLogic-Light", default_factory=list)
    pump: list[MSPPump] | None = Field(alias="Pump", default_factory=list)
    chlorinator: MSPChlorinator | None = Field(alias="Chlorinator", default=None)
    csad: list[MSPCSAD] | None = Field(alias="CSAD", default_factory=list)

class MSPBackyard(OmniBase):
    omni_type: OmniType = OmniType.BACKYARD
    sensor: list[MSPSensor] | None = Field(alias="Sensor", default_factory=list)
    bow: list[MSPBoW] | None = Field(alias="Body-of-water", default_factory=list)
    relay: list[MSPRelay] | None = Field(alias="Relay", default_factory=list)
    colorlogic_light: list[MSPColorLogicLight] | None = Field(alias="ColorLogic-Light", default_factory=list)

class MSPSchedule(OmniBase):
    omni_type: OmniType = OmniType.SCHEDULE
    system_id: int = Field(alias="schedule-system-id")
    bow_id: int = Field(alias="bow-system-id")
    equipment_id: int = Field(alias="equipment-id")
    enabled: bool = Field(default=True)

MSPConfigType: TypeAlias = (
    MSPSystem | MSPSchedule | MSPBackyard | MSPBoW | MSPVirtualHeater | MSPHeaterEquip | MSPRelay | MSPFilter | MSPSensor | MSPColorLogicLight | MSPChlorinator | MSPCSAD
)

class MSPConfig(BaseModel):
    system: MSPSystem = Field(alias="System", default_factory=MSPSystem)
    backyard: MSPBackyard = Field(alias="Backyard", default_factory=MSPBackyard)

    class Config:
        allow_population_by_field_name = True

    @staticmethod
    def load_xml(xml: str) -> MSPConfig:
        return MSPConfig.construct()
