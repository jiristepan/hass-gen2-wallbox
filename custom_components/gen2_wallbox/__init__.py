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

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GEN2 Wallbox from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    wallbox = GEN2_Wallbox(
        entry.data["deviceid"], entry.data["ip"], entry.data["localkey"]
    )

    # register device info for all entities
    wallbox.device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.data["ip"])},
        name=f"Wallbox Gen 2 [{entry.data['ip']}]",
        manufacturer="GEN2",
        model="EcoCharge GEN2",
        sw_version="1.0.0",
    )

    # periodical update of the state
    async_track_time_interval(hass, wallbox.update, timedelta(seconds=10))

    hass.data[DOMAIN][entry.entry_id] = wallbox

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
