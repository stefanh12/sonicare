"""Parser for OralB BLE advertisements.

This code is based on the oralb-ble library:
https://github.com/Bluetooth-Devices/oralb-ble

Original Authors:
- J. Nick Koston (@bdraco)
- Contributors from Bluetooth-Devices organization

MIT License applies.

Original parser was shamelessly copied from:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/oral_b.py
"""

from __future__ import annotations

from sensor_state_data import (BinarySensorDeviceClass, BinarySensorValue,
                               DeviceKey, SensorDescription, SensorDeviceClass,
                               SensorDeviceInfo, SensorUpdate, SensorValue,
                               Units)

from .parser import OralBBinarySensor, OralBBluetoothDeviceData, OralBSensor

__version__ = "1.0.2"

__all__ = [
    "OralBSensor",
    "OralBBinarySensor",
    "OralBBluetoothDeviceData",
    "BinarySensorDeviceClass",
    "BinarySensorValue",
    "SensorDescription",
    "SensorDeviceInfo",
    "DeviceKey",
    "SensorUpdate",
    "SensorDeviceClass",
    "SensorDeviceInfo",
    "SensorValue",
    "Units",
]
