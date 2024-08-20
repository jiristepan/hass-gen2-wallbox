import time
import logging

import tinytuya

import asyncio
from concurrent.futures import ThreadPoolExecutor

import nest_asyncio

nest_asyncio.apply()

_LOGGER = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

_executor = ThreadPoolExecutor(1)

# tinytuya.set_debug(True)
# Connect to Device


class GEN2_Wallbox:
    """CLASS represoenting GEN2 WALLBOX using tinytuya local integrations."""

    UPDATE_INTERVAL = 5
    MAX_CURRENT = 16
    MIN_CURRENT = 8

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
        self.name = "GEN2"
        self.deviceid = deviceid
        self.ip = ip
        self.localkey = localkey
        self.car_phases = 3
        self.config = {}

        self.data = {}
        self.available = False

        self.device = tinytuya.OutletDevice(deviceid, ip, localkey)
        self.device.set_version(3.3)
        self.device.set_socketTimeout(3)
        self.device.set_socketRetryLimit(5)

        self.update()

    def is_available(self) -> bool:
        return self.available

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

    def fetch_status_from_device(self):
        try:
            data = self.device.status()
            if "Error" in data:
                self.status = {"connected": False, "message": data["Error"]}
                self.available = False
            else:
                self.status = {"connected": True, "message": ""}
                self.available = True

            _LOGGER.debug(self.available)
            _LOGGER.debug(data)
            if self.available:
                self._dps_data = data
                self._dps_data_timestamp = time.time()

        except Exception as e:
            self.status = {"connected": False, "message": str(e)}
            self.available = False
        return "ok"

    async def async_update(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(_executor, self.fetch_status_from_device)

    def update(self, ts=None):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.async_update())
        loop.close()

    ### set value
    def set_value(self, parameter, value):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.async_set_value(parameter, value))
        loop.close()

    async def async_set_value(self, parameter, value):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            _executor, lambda: self.send_value_to_device(parameter, value)
        )

    def send_value_to_device(self, parameter, value):
        res = self.device.set_value(self._dps_codes[parameter], value)
        _LOGGER.debug(f"Setting {parameter} to {value} - {res}")
        return res

    def start_charging(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.async_start_charging())
        loop.close()

    async def async_start_charging(self):
        await self.async_set_value("SwipeRfid", True)
        asyncio.sleep(1)
        await self.async_set_value("SwipeRfid", False)

    def stop_charging(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.async_stop_charging())
        loop.close()

    async def async_stop_charging(self):
        await self.async_set_value("SwipeRfid", True)
        asyncio.sleep(1)
        await self.async_set_value("SwipeRfid", False)


if __name__ == "__main__":
    DEVICE_ID = "bff43c83a43130ad07vf7v"
    LOCAL_KEY = "b1d93795cba6663e"  #'00ed6c23d3eb8ee5'
    IP_ADDRESS = "10.0.30.9"

    wb = GEN2_Wallbox(DEVICE_ID, IP_ADDRESS, LOCAL_KEY)
    print(wb._dps_data)
    print(wb.status)

    print("Setting 32A to 16")
    wb.set_value("Set32A", 8)

    print("Starting Charging")
    wb.stop_charging()
