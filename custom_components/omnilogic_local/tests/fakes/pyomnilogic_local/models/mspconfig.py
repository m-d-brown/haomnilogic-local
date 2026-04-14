"""MSP Config models for the shadow library."""

from pydantic.v1 import BaseModel, Field
from typing import List, Optional, Any
from ..omnitypes import OmniType

class OmniBase(BaseModel):
    """Base class for all OmniLogic models."""
    class Config:
        allow_population_by_field_name = True

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
            "sensor", "bow", "filter", "heater", "chlorinator", 
            "color_logic_light", "relay", "valve_actuator", "virtual_heater",
            "schedule", "favorites", "group"
        }
        return self.copy(exclude=exclude)

class MSPSystem(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.SYSTEM, alias="Type")
    vsp_speed_format: str = Field("Percent", alias="VSP-Speed-Format")
    units: str = Field("Standard", alias="Units")

class MSPSensor(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.SENSOR, alias="Type")
    units: Optional[str] = Field(None, alias="Units")

class MSPCSAD(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.CSAD, alias="Type")

class MSPFilter(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.FILTER, alias="Type")
    filter_type: Optional[str] = Field(None, alias="Filter-Type")

class MSPHeater(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.HEATER, alias="Type")

class MSPHeaterEquip(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.HEATER_EQUIP, alias="Type")

class MSPRelay(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.RELAY, alias="Type")

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
    sensor: List[MSPSensor] = []
    bow: List["MSPBoW"] = []

class MSPBoW(MSPBaseModel):
    omni_type: OmniType = Field(OmniType.BOW, alias="Type")
    filter: List[MSPFilter] = []
    heater: List[MSPHeater] = []
    sensor: List[MSPSensor] = []
    chlorinator: List[MSPChlorinator] = []
    color_logic_light: List[MSPColorLogicLight] = []
    relay: List[MSPRelay] = []
    supports_spillover: Optional[str] = Field("no", alias="Supports-Spillover")

class MSPConfig(MSPBaseModel):
    system: MSPSystem
    backyard: MSPBackyard

    @classmethod
    def load_xml(cls, xml: str):
        """Mock load_xml that returns a pre-configured model."""
        # This is patched in conftest.py
        return None

# Required for forward refs
MSPBackyard.update_forward_refs()
