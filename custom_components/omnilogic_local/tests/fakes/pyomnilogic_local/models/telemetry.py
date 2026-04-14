"""Telemetry models for the shadow library."""

from pydantic.v1 import BaseModel, Field
from typing import List, Optional, Any, Union

class TelemetryBaseModel(BaseModel):
    """Base model for all telemetry objects."""
    system_id: Optional[int] = Field(None, alias="System-Id")
    state: Optional[Any] = Field(None, alias="State")
    why_on: Optional[Any] = Field(None, alias="Why-On")

class TelemetryBackyard(TelemetryBaseModel):
    air_temp: Optional[int] = Field(None, alias="Air-Temp")

class TelemetryBoW(TelemetryBaseModel):
    water_temp: Optional[int] = Field(None, alias="Water-Temp")
    flow: Optional[int] = Field(0, alias="Flow")

class TelemetryFilter(TelemetryBaseModel):
    speed: Optional[int] = Field(0, alias="Speed")
    last_speed: Optional[int] = Field(0, alias="Last-Speed")
    valve_position: Optional[Any] = Field(None, alias="Valve-Position")

class TelemetryHeater(TelemetryBaseModel):
    temp: Optional[int] = Field(None, alias="Temp")

class TelemetryPump(TelemetryBaseModel):
    speed: Optional[int] = Field(0, alias="Speed")
    last_speed: Optional[int] = Field(0, alias="Last-Speed")

class TelemetryRelay(TelemetryBaseModel):
    pass

class TelemetryValveActuator(TelemetryBaseModel):
    pass

class TelemetryVirtualHeater(TelemetryBaseModel):
    pass

class TelemetryChlorinator(TelemetryBaseModel):
    operating_mode: Optional[int] = Field(0, alias="Operating-Mode")
    output_percentage: Optional[int] = Field(0, alias="Output-Percentage")
    enable: Optional[bool] = Field(True, alias="Enable")

class TelemetryColorLogicLight(TelemetryBaseModel):
    show: Optional[int] = Field(0, alias="Show")

class TelemetrySensor(TelemetryBaseModel):
    temp: Optional[int] = Field(None, alias="Temp")

class TelemetryCSAD(TelemetryBaseModel):
    ph: Optional[float] = Field(None, alias="PH")
    orp: Optional[float] = Field(None, alias="ORP")

class TelemetryGroup(TelemetryBaseModel):
    pass

# Type hint for all telemetry objects
TelemetryType = Union[
    TelemetryBackyard,
    TelemetryBoW,
    TelemetryFilter,
    TelemetryHeater,
    TelemetryPump,
    TelemetryRelay,
    TelemetryValveActuator,
    TelemetryVirtualHeater,
    TelemetryChlorinator,
    TelemetryColorLogicLight,
    TelemetrySensor,
    TelemetryCSAD,
    TelemetryGroup,
]

class Telemetry(BaseModel):
    """Root telemetry model."""
    backyard: Optional[TelemetryBackyard] = None
    bow: List[TelemetryBoW] = []
    filter: List[TelemetryFilter] = []
    heater: List[TelemetryHeater] = []
    pump: List[TelemetryPump] = []
    relay: List[TelemetryRelay] = []
    valve_actuator: List[TelemetryValveActuator] = []
    virtual_heater: List[TelemetryVirtualHeater] = []
    chlorinator: List[TelemetryChlorinator] = []
    color_logic_light: List[TelemetryColorLogicLight] = []
    sensor: List[TelemetrySensor] = []
    group: List[TelemetryGroup] = []

    def get_telem_by_systemid(self, system_id: int) -> Optional[Any]:
        """Helper to find telemetry for a specific system ID."""
        if self.backyard and self.backyard.system_id == system_id:
            return self.backyard
        
        # Search through all lists
        for attr in [
            "bow", "filter", "heater", "pump", "relay", "valve_actuator", 
            "virtual_heater", "chlorinator", "color_logic_light", "sensor", "group"
        ]:
            items = getattr(self, attr)
            for item in items:
                if item.system_id == system_id:
                    return item
        return None

    @classmethod
    def load_xml(cls, xml: str):
        """Mock load_xml that returns a pre-configured model."""
        # This is patched in conftest.py
        return None
