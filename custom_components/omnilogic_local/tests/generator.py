"""OmniLogic fixture generator for testing."""

from __future__ import annotations

import xml.etree.ElementTree as ET


class OmniLogicFixtureGenerator:
    """Helper class to generate MSPConfig and Telemetry XMLs."""

    def __init__(self) -> None:
        """Initialize the generator with root elements."""
        self.msp_config = ET.Element("MSPConfig")
        self.backyard = ET.SubElement(self.msp_config, "Backyard")
        ET.SubElement(self.backyard, "System-Id").text = "0"

        self.telemetry = ET.Element("OmniLogic-Telemetry")
        self.tele_backyard = ET.SubElement(self.telemetry, "Backyard")
        ET.SubElement(self.tele_backyard, "System-Id").text = "0"
        ET.SubElement(self.tele_backyard, "State").text = "1"

        self._next_system_id = 1

    def _get_next_system_id(self) -> int:
        sid = self._next_system_id
        self._next_system_id += 1
        return sid

    def add_pool(self, system_id: int | None = None, name: str = "Pool", water_temp: int = 80) -> OmniLogicFixtureGenerator:
        """Add a pool Body of Water."""
        sid = system_id or self._get_next_system_id()
        bow = ET.SubElement(self.backyard, "Body-of-Water")
        ET.SubElement(bow, "System-Id").text = str(sid)
        ET.SubElement(bow, "Name").text = name
        ET.SubElement(bow, "Type").text = "BOW_POOL"

        tele = ET.SubElement(self.telemetry, "BoW")
        ET.SubElement(tele, "System-Id").text = str(sid)
        ET.SubElement(tele, "Water_Temp").text = str(water_temp)

        return self

    def add_filter(
        self,
        bow_id: int,
        system_id: int | None = None,
        name: str = "Filter",
        state: int = 1,
        speed: int = 50,
    ) -> OmniLogicFixtureGenerator:
        """Add a filter pump."""
        sid = system_id or self._get_next_system_id()
        filter_pump = ET.SubElement(self.backyard, "Filter")
        ET.SubElement(filter_pump, "System-Id").text = str(sid)
        ET.SubElement(filter_pump, "Name").text = name
        ET.SubElement(filter_pump, "Bow-Id").text = str(bow_id)
        ET.SubElement(filter_pump, "Type").text = "FMT_VARIABLE_SPEED_PUMP"
        ET.SubElement(filter_pump, "Max-RPM").text = "3450"
        ET.SubElement(filter_pump, "Min-RPM").text = "600"
        ET.SubElement(filter_pump, "Max-Percent").text = "100"
        ET.SubElement(filter_pump, "Min-Percent").text = "20"

        # Operations list is required by Pydantic model
        ops = ET.SubElement(filter_pump, "Operations")
        op = ET.SubElement(ops, "Operation")
        ET.SubElement(op, "Id").text = "1"

        tele = ET.SubElement(self.telemetry, "Filter")
        ET.SubElement(tele, "System-Id").text = str(sid)
        ET.SubElement(tele, "Filter-State").text = str(state)
        ET.SubElement(tele, "Filter-Speed").text = str(speed)

        return self

    def add_light(
        self,
        bow_id: int,
        system_id: int | None = None,
        name: str = "Light",
        state: int = 6,
    ) -> OmniLogicFixtureGenerator:
        """Add a ColorLogic light."""
        sid = system_id or self._get_next_system_id()
        light = ET.SubElement(self.backyard, "ColorLogic-Light")
        ET.SubElement(light, "System-Id").text = str(sid)
        ET.SubElement(light, "Name").text = name
        ET.SubElement(light, "Bow-Id").text = str(bow_id)
        ET.SubElement(light, "Type").text = "COLOR_LOGIC_UCL"
        ET.SubElement(light, "V2-Active").text = "yes"

        tele = ET.SubElement(self.telemetry, "ColorLogic-Light")
        ET.SubElement(tele, "System-Id").text = str(sid)
        ET.SubElement(tele, "State").text = str(state)
        ET.SubElement(tele, "Brightness").text = "4"
        ET.SubElement(tele, "Speed").text = "4"
        ET.SubElement(tele, "Show").text = "0"

        return self

    def add_relay(
        self,
        system_id: int | None = None,
        name: str = "Relay",
        bow_id: int | None = None,
        state: int = 1,
    ) -> OmniLogicFixtureGenerator:
        """Add a relay."""
        sid = system_id or self._get_next_system_id()
        relay = ET.SubElement(self.backyard, "Relay")
        ET.SubElement(relay, "System-Id").text = str(sid)
        ET.SubElement(relay, "Name").text = name
        ET.SubElement(relay, "Type").text = "RLY_HIGH_VOLTAGE_RELAY"
        ET.SubElement(relay, "Function").text = "RLY_WATER_FEATURE"
        if bow_id:
            ET.SubElement(relay, "Bow-Id").text = str(bow_id)

        tele = ET.SubElement(self.telemetry, "Relay")
        ET.SubElement(tele, "System-Id").text = str(sid)
        ET.SubElement(tele, "Relay-State").text = str(state)

        return self

    def add_air_sensor(self, system_id: int | None = None, name: str = "Air Temp", temp: int = 75) -> OmniLogicFixtureGenerator:
        """Add an air temperature sensor."""
        sid = system_id or self._get_next_system_id()
        sensor = ET.SubElement(self.backyard, "Sensor")
        ET.SubElement(sensor, "System-Id").text = str(sid)
        ET.SubElement(sensor, "Name").text = name
        ET.SubElement(sensor, "Type").text = "SENSOR_AIR_TEMP"
        ET.SubElement(sensor, "Units").text = "UNITS_FAHRENHEIT"

        tele = ET.SubElement(self.telemetry, "Sensor")
        ET.SubElement(tele, "System-Id").text = str(sid)
        ET.SubElement(tele, "Temp").text = str(temp)

        return self

    def generate_msp_config(self) -> str:
        """Return the generated MSPConfig XML."""
        return ET.tostring(self.msp_config, encoding="unicode")

    def generate_telemetry(self) -> str:
        """Return the generated Telemetry XML."""
        return ET.tostring(self.telemetry, encoding="unicode")
