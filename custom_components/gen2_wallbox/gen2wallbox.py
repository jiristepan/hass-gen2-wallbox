"""Module GEN2_WALLBOX """

import time
import tinytuya
import logging
from .async_helper import *

_LOGGER = logging.getLogger(__name__)


class GEN2_Wallbox:
    """CLASS represoenting GEN2 WALLBOX using tinytuya local integrations."""

    UPDATE_INTERVAL = 5

    status = None
    available = False

    # last cached data
    _dps_data = None
    _dps_data_timestamp = 0

    _dps_codes = {
        "DeviceState": 101,
        "DeviceKwh": 106,
        "InputVoltage": 107,
        "OutCurrent": 108,
        "DeviceKw": 109,
        "DeviceTemp": 110,
        "SwipeRfid": 112,
        "Set32A": 111,
    }

    def __init__(self, deviceid, ip, localkey) -> None:
        self.deviceid = deviceid
        self.ip = ip
        self.localkey = localkey

        self.device = tinytuya.OutletDevice(deviceid, ip, localkey)
        self.device.set_version(3.3)
        self.device.set_socketTimeout(5)
        self.device.set_socketRetryLimit(3)

        self.update()

    def update(self, hass=None):
        """update status of the device"""
        _LOGGER.info("Sync update start")

        data = self.device.status()

        if "Error" in data:
            self.status = {"connected": False, "message": data["Error"]}
            self.available = False
        else:
            self.status = {"connected": True, "message": ""}
            self.available = True

        if not self.available:
            return "failed"

        self._dps_data = data
        self._dps_data_timestamp = time.time()

        return "updated"

    async def async_update(self):
        """update status of the device"""
        _LOGGER.info("Async update start")

        # if time.time() - self._dps_data_timestamp < self.UPDATE_INTERVAL:
        #     out = {
        #         "mode": "cached",
        #         "last_update": self._dps_data_timestamp,
        #         "data": self._dps_data,
        #     }
        #     _LOGGER.info(out)
        #     return out

        data = self.device.status()
        if "Error" in data:
            self.status = {"connected": False, "message": data["Error"]}
            self.available = False
        else:
            self.status = {"connected": True, "message": ""}
            self.available = True

        if (
            not self.available
            and time.time() - self._dps_data_timestamp > 3 * self.UPDATE_INTERVAL
        ):
            _LOGGER.info("Device not available")
            return None

        self._dps_data = data
        self._dps_data_timestamp = time.time()

        out = {
            "mode": "updated",
            "last_update": self._dps_data_timestamp,
            "data": self._dps_data,
        }
        _LOGGER.info(out)
        return out

    def get_data(self):
        if self.available:
            return self._dps_data
        else:
            return None

    def get_value(self, parameter):
        if self.available:
            return self._dps_data["dps"][f"{self._dps_codes[parameter]}"]
        else:
            return None

    def set_value(self, parameter, value):
        res = self.device.set_value(self._dps_codes[parameter], value)
        return res

    def start_charging(self):
        state = self.get_value("DeviceState")
        if state != "charing":
            self.device.set_value(112, True)
            time.sleep(1)
            self.device.set_value(112, False)

    def stop_charging(self):
        state = self.get_value("DeviceState")
        if state == "charing":
            self.device.set_value(112, True)
            time.sleep(1)
            self.device.set_value(112, False)
