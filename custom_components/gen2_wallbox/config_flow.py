"""Config flow for GEN2 Wallbox integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .gen2wallbox import GEN2_Wallbox

from homeassistant.helpers import config_validation as cv


_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional("name", default="GEN2 Wallbox"): cv.string,
        vol.Required("ip"): cv.string,
        vol.Required("deviceid"): cv.string,
        vol.Required("localkey"): cv.string,
        vol.Optional("car_phases", default=3): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=3)
        ),
        vol.Optional("test", default=False): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    _LOGGER.debug(f"(validate_input) data: {data}")
    wallbox = GEN2_Wallbox(data["deviceid"], data["ip"], data["localkey"])

    if data["name"]:
        wallbox.name = data["name"]

    if data["car_phases"]:
        wallbox.car_phases = int(data["car_phases"])

    if not data["test"]:
        _LOGGER.debug(f"testing conections")
        status = wallbox.update()
        _LOGGER.debug(status)

        if not wallbox.available:
            raise CannotConnect()

    # Return info that you want to store in the config entry.
    return {"title": f'GEN2WB-f{data["ip"]}'}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GEN2 Wallbox."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:

            await self.async_set_unique_id(user_input["deviceid"])
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
