"""Platform for sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the Ally binary_sensor platform."""
    _LOGGER.info("Setting up GEN2 Wallbox numbers")
    gen2 = hass.data[DOMAIN][entry.entry_id]

    entities = [WallBoxChargingSwitch(gen2)]

    async_add_entities(entities, True)


class WallBoxChargingSwitch(SwitchEntity):
    """Representation actual output current of the Wallbox."""

    _attr_has_entity_name = True
    _attr_name = "Charging switch"
    _attr_unique_id = "wallbox_charging_switch"
    _attr_device_class = SwitchDeviceClass.OUTLET

    def __init__(self, device) -> None:
        super().__init__()
        self.device = device

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self.device.device_info

    @property
    def is_on(self) -> bool | None:
        """Return the state of the number entity."""
        data = self.device.get_value("DeviceState")
        if data == None:
            self._attr_available = False
            return False
        else:
            self._attr_available = True
            if data == "charing":
                return True

        return False

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        self.device.start_charging()
        await self.device.async_update()

    async def async_turn_off(self, **kwargs):
        """Turn the entity on."""
        self.device.stop_charging()
        await self.device.async_update()
