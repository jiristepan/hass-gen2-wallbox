"""Platform for sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ELECTRIC_CURRENT_AMPERE, POWER_KILO_WATT, TEMP_CELSIUS, ENERGY_KILO_WATT_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the GEN2 sensors platform."""

    gen2 = hass.data[DOMAIN][entry.entry_id]

    entities = [
        WallBoxState(gen2),
        WallBoxTemperature(gen2),
        WallBoxDevicePower(gen2),
        WallBoxDeviceEnergy(gen2),
        WallBoxOutCurrent(gen2),
        WallBoxDevicePowerEstimated(gen2)
    ]

    async_add_entities(entities, True)


class WallBoxState(SensorEntity):
    """Representation State of the Wallbox."""

    _attr_has_entity_name = True
    _attr_name = "State"
    _attr_unique_id = "wallbox_state"
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, device) -> None:
        super().__init__()
        self.device = device
        self._attr_available = False

    @property
    def available(self) -> bool | None:
        return self.device.is_available()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self.device.device_info

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        data = self.device.get_value("DeviceState")
        if data == None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._attr_native_value = data


class WallBoxOutCurrent(SensorEntity):
    """Representation actual output current of the Wallbox."""

    _attr_has_entity_name = True
    _attr_name = "Charging current"
    _attr_unique_id = "wallbox_charging_current"
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_device_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    def __init__(self, device) -> None:
        super().__init__()
        self.device = device
        self._attr_available = False

    @property
    def available(self) -> bool | None:
        return self.device.is_available()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self.device.device_info

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        data = self.device.get_value("OutCurrent")
        if data == None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._attr_native_value = int(data) / 10.0


class WallBoxTemperature(SensorEntity):
    """Representation temperature of the Wallbox."""

    _attr_has_entity_name = True
    _attr_name = "Temperature"
    _attr_unique_id = "wallbox_temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_device_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = TEMP_CELSIUS

    def __init__(self, data) -> None:
        super().__init__()
        self.device = data
        self._attr_available = False

    @property
    def available(self) -> bool | None:
        return self.device.is_available()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self.device.device_info

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        # self._state = await self.device.async_update()
        data = self.device.get_value("DeviceTemp")
        if data == None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._attr_native_value = int(data) / 10.0


class WallBoxDevicePower(SensorEntity):
    """Representation actual output kW."""

    _attr_has_entity_name = True
    _attr_name = "Power"
    _attr_unique_id = "wallbox_power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_device_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = POWER_KILO_WATT

    def __init__(self, data) -> None:
        super().__init__()
        self.device = data
        self._attr_available = False

    @property
    def available(self) -> bool | None:
        return self.device.is_available()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self.device.device_info

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        data = self.device.get_value("DeviceKw")
        if data is None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._attr_native_value = int(data) / 10.0

class WallBoxDeviceEnergy(SensorEntity):
    """Representation actual cumulative output in kWh."""

    _attr_has_entity_name = True
    _attr_name = "Compsumption"
    _attr_unique_id = "wallbox_compsumption"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_device_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    def __init__(self, data) -> None:
        super().__init__()
        self.device = data
        self._attr_available = False

    @property
    def available(self) -> bool | None:
        return self.device.is_available()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self.device.device_info

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        data = self.device.get_value("DeviceKwh")
        if data is None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._attr_native_value = int(data) / 10.0


class WallBoxDevicePowerEstimated(SensorEntity):
    """Representation actual output kW."""

    _attr_has_entity_name = True
    _attr_name = "Power Estimated"
    _attr_unique_id = "wallbox_power_estimated"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_device_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = POWER_KILO_WATT

    def __init__(self, data) -> None:
        super().__init__()
        self.device = data
        self._attr_available = False

    @property
    def available(self) -> bool | None:
        return self.device.is_available()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self.device.device_info

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        data = self.device.get_value("OutCurrent")
        if data is None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._attr_native_value = int(data) / 10 * 230 * self.device.car_phases
