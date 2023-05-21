"""The GEN2 Wallbox integration."""
from __future__ import annotations
from datetime import timedelta

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .gen2wallbox import GEN2_Wallbox

import voluptuous as vol
from homeassistant.helpers import config_validation as cv


_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH]
config = {}

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(
                    "update_interval"
                ): int
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config) -> bool:
    """Set up the GEN2 Wallbox platform platform."""
    if DOMAIN in config:
        conf = config[DOMAIN]
    else:
        conf = {}

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["CONFIG"] = conf

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GEN2 Wallbox from a config entry."""

    _LOGGER.debug("Setting up Wallbox entry")
    _LOGGER.debug(hass.data[DOMAIN])
    wallbox = GEN2_Wallbox(
        entry.data["deviceid"], entry.data["ip"], entry.data["localkey"]
    )
    if (entry.data["car_phases"]):
        wallbox.car_phases = int(entry.data["car_phases"])

    wallbox.config = hass.data[DOMAIN]["CONFIG"]

    # register device info for all entities
    wallbox.device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.data["ip"])},
        name=f"Wallbox Gen 2 [{entry.data['ip']}]",
        manufacturer="GEN2",
        model="EcoCharge GEN2",
        sw_version="1.0.0",
    )

    update_interval = 10
    if "update_interval" in wallbox.config:
        update_interval = int(wallbox.config["update_interval"])

    # periodical update of the state
    _LOGGER.debug(f"Starting async update task with interval {update_interval} sec")
    async_track_time_interval(hass, wallbox.update, timedelta(seconds=update_interval))

    hass.data[DOMAIN][entry.entry_id] = wallbox

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:

        new = {**config_entry.data}
        # TODO: modify Config Entry data

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.debug("Migration to version %s successful", config_entry.version)

    return True


class GEN2_wallbox_platform:
    """wraper for global configuration"""
    def __init__(self, hass, config):
        self.hass = hass
        self.config = config