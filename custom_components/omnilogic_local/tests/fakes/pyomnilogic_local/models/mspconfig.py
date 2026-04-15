from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from ..omnitypes import (
    BodyOfWaterType,
    CSADType,
    FilterType,
    HeaterType,
    OmniType,
    RelayType,
    SensorType,
)
from ..utils import DiscoveryDict


class OmniBase(BaseModel):
    """Base class for all OmniLogic models."""

    model_config = ConfigDict(populate_by_name=True)

    @property
    def is_ready(self) -> bool:
        """Mock is_ready property."""
        return True


class MSPBaseModel(OmniBase):
    """Base model for all MSP configuration objects."""

    system_id: Optional[int] = Field(None, alias="System-Id")
    name: Optional[str] = Field(None, alias="Name")
    omni_type: Optional[OmniType] = Field(None, alias="Type")
    bow_id: Optional[int] = Field(None, alias="BOW-ID")
    type: Optional[Any] = Field(None, alias="Type")  # Used for specialized types (e.g. RelayType, BoWType)
    function: Optional[Any] = Field(None, alias="Function")

    def without_subdevices(self):
        """Return a copy of the model without subdevices to avoid recursion during walks."""
        exclude = {
            "sensor",
            "bow",
            "filter",
            "heater",
            "heater_equipment",
            "chlorinator",
            "chlorinator_equipment",
            "color_logic_light",
            "relay",
            "csad",
            "valve_actuator",
            "virtual_heater",
            "schedule",
            "favorites",
            "group",
        }
        # In V2, model_copy() doesn't support exclude.
        # We manually clear the fields after copy.
        new_obj = self.model_copy()
        for field in exclude:
            if hasattr(new_obj, field):
                setattr(new_obj, field, [])
        return new_obj


class MSPSystem(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.SYSTEM, alias="Type")
    vsp_speed_format: str = Field("Percent", alias="VSP-Speed-Format")
    units: str = Field("Standard", alias="Units")


class MSPSensor(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.SENSOR, alias="Type")
    equip_type: Optional[SensorType] = Field(None, alias="Type")
    units: Optional[str] = Field(None, alias="Units")


class MSPCSAD(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.CSAD, alias="Type")
    equip_type: Optional[CSADType] = Field(None, alias="Type")


class MSPFilter(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.FILTER, alias="Type")
    filter_type: Optional[FilterType] = Field(None, alias="Type")


class MSPHeater(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.HEATER, alias="Type")


class MSPHeaterEquip(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.HEATER_EQUIP, alias="Type")
    heater_type: Optional[HeaterType] = Field(None, alias="Type")


class MSPRelay(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.RELAY, alias="Type")
    relay_type: Optional[RelayType] = Field(None, alias="Type")


class MSPPump(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.PUMP, alias="Type")


class MSPSchedule(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.SCHEDULE, alias="Type")


class MSPFavorites(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.FAVORITES, alias="Type")


class MSPGroup(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.GROUP, alias="Type")


class MSPValveActuator(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.VALVE_ACTUATOR, alias="Type")


class MSPVirtualHeater(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.VIRT_HEATER, alias="Type")
    min_temp: Optional[int] = Field(None, alias="Min-Temp")
    max_temp: Optional[int] = Field(None, alias="Max-Temp")


class MSPChlorinator(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.CHLORINATOR, alias="Type")
    dispenser_type: Optional[str] = Field(None, alias="Dispenser-Type")


class MSPChlorinatorEquip(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.CHLORINATOR_EQUIP, alias="Type")


class MSPColorLogicLight(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.CL_LIGHT, alias="Type")
    light_type: Optional[str] = Field(None, alias="Light-Type")


class MSPBackyard(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.BACKYARD, alias="Type")
    sensor: DiscoveryDict = Field(default_factory=DiscoveryDict)
    bow: DiscoveryDict = Field(default_factory=DiscoveryDict)
    csad: DiscoveryDict = Field(default_factory=DiscoveryDict)


class MSPBoW(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.BOW, alias="Type")
    bow_type: Optional[BodyOfWaterType] = Field(None, alias="Type")
    filter: DiscoveryDict = Field(default_factory=DiscoveryDict)
    heater: DiscoveryDict = Field(default_factory=DiscoveryDict)
    heater_equipment: DiscoveryDict = Field(default_factory=DiscoveryDict)
    sensor: DiscoveryDict = Field(default_factory=DiscoveryDict)
    chlorinator: DiscoveryDict = Field(default_factory=DiscoveryDict)
    chlorinator_equipment: DiscoveryDict = Field(default_factory=DiscoveryDict)
    color_logic_light: DiscoveryDict = Field(default_factory=DiscoveryDict)
    relay: DiscoveryDict = Field(default_factory=DiscoveryDict)
    csad: DiscoveryDict = Field(default_factory=DiscoveryDict)
    supports_spillover: Optional[str] = Field("no", alias="Supports-Spillover")


class MSPConfig(MSPBaseModel):
    system: MSPSystem
    backyard: MSPBackyard

    @classmethod
    def load_xml(cls, xml: str):
        """Mock load_xml that returns a pre-configured model."""
        # This is patched in conftest.py
        return


# Required for forward refs in V2
MSPBackyard.model_rebuild()
MSPBoW.model_rebuild()
MSPConfig.model_rebuild()
