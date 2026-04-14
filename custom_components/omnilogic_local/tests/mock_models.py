"""Mock models for OmniLogic Local integration tests."""

from __future__ import annotations
from typing import Any
from pyomnilogic_local.omnitypes import CSADType, SensorType
from pyomnilogic_local.models.mspconfig import (
    MSPRelay,
    MSPSensor,
    MSPCSAD,
    MSPVirtualHeater,
    MSPColorLogicLight,
    MSPFilter,
    MSPChlorinator,
    MSPBoW,
    MSPBackyard,
)
from pyomnilogic_local.models.telemetry import (
    TelemetryRelay,
    TelemetryFilter,
    TelemetryHeater,
    TelemetryVirtualHeater,
    TelemetryColorLogicLight,
    TelemetryChlorinator,
    TelemetryBoW,
    TelemetryBackyard,
    TelemetrySensor,
    TelemetryCSAD,
)
from ..types.entity_index import EntityIndexData

def create_mock_backyard(system_id: int = 0, name: str = "Backyard", **kwargs: Any) -> EntityIndexData:
    return EntityIndexData(
        msp_config=MSPBackyard(system_id=system_id, name=name, **kwargs),
        telemetry=TelemetryBackyard(system_id=system_id)
    )

def create_mock_bow(system_id: int = 3, name: str = "Pool", **kwargs: Any) -> EntityIndexData:
    return EntityIndexData(
        msp_config=MSPBoW(system_id=system_id, name=name, **kwargs),
        telemetry=TelemetryBoW(system_id=system_id)
    )

def create_mock_filter(system_id: int = 4, name: str = "Filter", bow_id: int = 3, **kwargs: Any) -> EntityIndexData:
    return EntityIndexData(
        msp_config=MSPFilter(system_id=system_id, name=name, bow_id=bow_id, **kwargs),
        telemetry=TelemetryFilter(system_id=system_id)
    )

def create_mock_relay(system_id: int = 5, name: str = "Relay", bow_id: int = 3, **kwargs: Any) -> EntityIndexData:
    return EntityIndexData(
        msp_config=MSPRelay(system_id=system_id, name=name, bow_id=bow_id, **kwargs),
        telemetry=TelemetryRelay(system_id=system_id)
    )

def create_mock_sensor(system_id: int = 6, name: str = "Sensor", bow_id: int = 3, **kwargs: Any) -> EntityIndexData:
    sensor_type = kwargs.get("type")
    
    # Determine the correct model based on the sensor type
    if sensor_type in [CSADType.ACID, CSADType.CO2]:
        msp_config = MSPCSAD(system_id=system_id, name=name, bow_id=bow_id, **kwargs)
        telemetry = TelemetryCSAD(system_id=system_id)
    elif sensor_type in [SensorType.AIR_TEMP, SensorType.SOLAR_TEMP, SensorType.WATER_TEMP]:
        msp_config = MSPSensor(system_id=system_id, name=name, bow_id=bow_id, **kwargs)
        telemetry = TelemetrySensor(system_id=system_id)
    else:
        # Default to generic sensor/telemetry
        msp_config = MSPSensor(system_id=system_id, name=name, bow_id=bow_id, **kwargs)
        telemetry = TelemetryBoW(system_id=system_id) # Using BoW telemetry as a generic placeholder if needed, but usually it should be TelemetrySensor
        
    return EntityIndexData(msp_config=msp_config, telemetry=telemetry)

def create_mock_heater(system_id: int = 7, name: str = "Heater", bow_id: int = 3, **kwargs: Any) -> EntityIndexData:
    return EntityIndexData(
        msp_config=MSPVirtualHeater(system_id=system_id, name=name, bow_id=bow_id, **kwargs),
        telemetry=TelemetryVirtualHeater(system_id=system_id)
    )

def create_mock_light(system_id: int = 9, name: str = "Light", bow_id: int = 3, **kwargs: Any) -> EntityIndexData:
    return EntityIndexData(
        msp_config=MSPColorLogicLight(system_id=system_id, name=name, bow_id=bow_id, **kwargs),
        telemetry=TelemetryColorLogicLight(system_id=system_id)
    )

def create_mock_chlorinator(system_id: int = 10, name: str = "Chlorinator", bow_id: int = 3, **kwargs: Any) -> EntityIndexData:
    return EntityIndexData(
        msp_config=MSPChlorinator(system_id=system_id, name=name, bow_id=bow_id, **kwargs),
        telemetry=TelemetryChlorinator(system_id=system_id)
    )
