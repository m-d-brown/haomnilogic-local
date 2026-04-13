"""OmniLogic Local Fixture Generator.

This module provides a programmatic way to generate MSPConfig and Telemetry XML
fixtures for testing the OmniLogic integration.
"""

from __future__ import annotations

from typing import Any
import xml.etree.ElementTree as ET
from xml.dom import minidom


class OmniLogicFixtureGenerator:
    """Builder for OmniLogic XML fixtures."""

    def __init__(self) -> None:
        self.system_id_counter = 1
        self.node_id_counter = 2050
        self.backyard_id = 0
        
        self.msp_root = ET.Element("MSPConfig")
        self.telemetry_root = ET.Element("STATUS", version="1.11")
        
        self.telemetry_backyard = None
        self.telemetry_bows = {}
        self.telemetry_filters = {}
        self.telemetry_sensors = {}
        
        self._setup_defaults()

    def _setup_defaults(self) -> None:
        """Initialize base structure."""
        # System section
        sys = ET.SubElement(self.msp_root, "System")
        ET.SubElement(sys, "Units").text = "Metric"
        ET.SubElement(sys, "Msp-Vsp-Speed-Format").text = "Percent"
        
        # Backyard section
        self.backyard = ET.SubElement(self.msp_root, "Backyard")
        ET.SubElement(self.backyard, "System-Id").text = str(self.backyard_id)
        ET.SubElement(self.backyard, "Name").text = "Backyard"
        
        # DMT section (Device Mapping Table)
        self.dmt = ET.SubElement(self.msp_root, "DMT")
        self.mp = ET.SubElement(self.dmt, "Device")
        ET.SubElement(self.mp, "Device-Name").text = "MP"
        ET.SubElement(self.mp, "Type").text = "MP"
        ET.SubElement(self.mp, "Node-ID").text = "2048"
        self.dmt_devices = ET.SubElement(self.mp, "Devices")
        
        # Telemetry Backyard
        self.telemetry_backyard = ET.SubElement(
            self.telemetry_root, 
            "Backyard", 
            systemId=str(self.backyard_id), 
            airTemp="75", 
            ConfigChksum="0"
        )

    def _get_next_system_id(self) -> int:
        sid = self.system_id_counter
        self.system_id_counter += 1
        return sid

    def _get_next_node_id(self) -> int:
        nid = self.node_id_counter
        self.node_id_counter += 1
        return nid

    def add_air_sensor(self, name: str = "AirSensor", temp: int = 75) -> OmniLogicFixtureGenerator:
        """Add an air temperature sensor to the backyard."""
        sid = self._get_next_system_id()
        nid = self._get_next_node_id()
        
        sensor = ET.SubElement(self.backyard, "Sensor")
        ET.SubElement(sensor, "System-Id").text = str(sid)
        ET.SubElement(sensor, "Name").text = name
        ET.SubElement(sensor, "Type").text = "SENSOR_AIR_TEMP"
        ET.SubElement(sensor, "Units").text = "UNITS_FAHRENHEIT"
        
        # Update telemetry
        self.telemetry_backyard.set("airTemp", str(temp))
        
        return self

    def add_pool(self, name: str = "Pool", gallons: int = 15000, water_temp: int = 80) -> OmniLogicFixtureGenerator:
        """Add a Body of Water (Pool)."""
        sid = self._get_next_system_id()
        
        bow = ET.SubElement(self.backyard, "Body-of-water")
        ET.SubElement(bow, "System-Id").text = str(sid)
        ET.SubElement(bow, "Name").text = name
        ET.SubElement(bow, "Type").text = "BOW_POOL"
        ET.SubElement(bow, "Size-In-Gallons").text = str(gallons)
        
        # Telemetry
        ET.SubElement(self.telemetry_root, "BodyOfWater", systemId=str(sid), waterTemp=str(water_temp), flow="1")
        
        # Store for future children (pumps, heaters, etc.)
        self.current_bow_sid = sid
        self.current_bow_el = bow
        return self

    def add_filter_pump(self, name: str = "Filter Pump", speed: int = 50) -> OmniLogicFixtureGenerator:
        """Add a variable speed filter pump to the current BOW."""
        if not hasattr(self, "current_bow_sid"):
             raise ValueError("Must add a Body of Water before adding equipment.")
             
        sid = self._get_next_system_id()
        nid = self._get_next_node_id()
        
        flt = ET.SubElement(self.current_bow_el, "Filter")
        ET.SubElement(flt, "System-Id").text = str(sid)
        ET.SubElement(flt, "Name").text = name
        ET.SubElement(flt, "Filter-Type").text = "FMT_VARIABLE_SPEED_PUMP"
        
        # Telemetry
        ET.SubElement(
            self.telemetry_root, 
            "Filter", 
            systemId=str(sid), 
            filterState="1" if speed > 0 else "0", 
            filterSpeed=str(speed),
            power="500" if speed > 0 else "0"
        )
        
        return self

    def add_chlorinator(self, name: str = "Chlorinator", timed_percent: int = 50) -> OmniLogicFixtureGenerator:
        """Add a chlorinator to the current BOW."""
        if not hasattr(self, "current_bow_sid"):
             raise ValueError("Must add a Body of Water before adding equipment.")
             
        sid = self._get_next_system_id()
        nid = self._get_next_node_id()
        
        chlor = ET.SubElement(self.current_bow_el, "Chlorinator")
        ET.SubElement(chlor, "System-Id").text = str(sid)
        ET.SubElement(chlor, "Name").text = name
        ET.SubElement(chlor, "Enabled").text = "yes"
        ET.SubElement(chlor, "Timed-Percent").text = str(timed_percent)
        
        # Telemetry
        ET.SubElement(
            self.telemetry_root, 
            "Chlorinator", 
            systemId=str(sid), 
            status="72",
            instantSaltLevel="3200",
            avgSaltLevel="3200",
            enable="1"
        )
        
        return self

    def add_heater(self, name: str = "Heater", current_temp: int = 80, set_point: int = 85) -> OmniLogicFixtureGenerator:
        """Add a heater to the current BOW."""
        if not hasattr(self, "current_bow_sid"):
             raise ValueError("Must add a Body of Water before adding equipment.")
             
        sid = self._get_next_system_id()
        
        heater = ET.SubElement(self.current_bow_el, "Heater")
        ET.SubElement(heater, "System-Id").text = str(sid)
        ET.SubElement(heater, "Enabled").text = "yes"
        ET.SubElement(heater, "Current-Set-Point").text = str(set_point)
        
        # Telemetry
        ET.SubElement(
            self.telemetry_root, 
            "Heater", 
            systemId=str(sid), 
            heaterState="1",
            temp=str(current_temp),
            enable="1"
        )
        # Virtual heater is also needed for some logic
        ET.SubElement(
            self.telemetry_root,
            "VirtualHeater",
            systemId=str(sid+1), # Simulating a virtual heater ID
            enable="1",
            Current_Set_Point=str(set_point)
        )
        
        return self

    def dump_msp_config(self) -> str:
        """Return pretty-printed MSPConfig XML."""
        xml_str = ET.tostring(self.msp_root, encoding="utf-8")
        reparsed = minidom.parseString(xml_str)
        return reparsed.toprettyxml(indent="    ")

    def dump_telemetry(self) -> str:
        """Return pretty-printed Telemetry XML."""
        xml_str = ET.tostring(self.telemetry_root, encoding="utf-8")
        reparsed = minidom.parseString(xml_str)
        return reparsed.toprettyxml(indent="    ")
