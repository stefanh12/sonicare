"""Sonicare BLE device wrapper."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from bleak import BLEDevice
from sensor_state_data import SensorUpdate

from .oralb_ble.parser import OralBBluetoothDeviceData

_LOGGER = logging.getLogger(__name__)
_LOGGER.warning("Loading device.py module")


class SonicareBLETB:
    """Wrapper for Sonicare BLE toothbrush using OralB parser."""

    def __init__(self, ble_device: BLEDevice) -> None:
        """Initialize the Sonicare BLE device."""
        self._ble_device = ble_device
        self._parser = OralBBluetoothDeviceData()
        self._callbacks: list[Callable[[SensorUpdate], None]] = []
        self._disconnect_callbacks: list[Callable[[], None]] = []

    async def initialise(self) -> None:
        """Initialize the device (no-op for passive monitoring)."""
        _LOGGER.debug("Initializing Sonicare BLE device: %s", self._ble_device.address)
        # For passive monitoring, no initialization needed
        pass

    async def stop(self) -> None:
        """Stop the device (no-op for passive monitoring)."""
        _LOGGER.debug("Stopping Sonicare BLE device: %s", self._ble_device.address)
        # For passive monitoring, no cleanup needed
        pass

    def set_ble_device_and_advertisement_data(
        self, ble_device: BLEDevice, advertisement_data: Any
    ) -> None:
        """Update with new BLE device and advertisement data."""
        self._ble_device = ble_device
        # The parser would handle the advertisement data if needed
        _LOGGER.debug("Updated BLE device and advertisement data")

    def register_callback(
        self, callback: Callable[[SensorUpdate], None]
    ) -> Callable[[], None]:
        """Register a callback to be called when data is updated."""
        self._callbacks.append(callback)

        def remove_callback() -> None:
            """Remove the callback."""
            self._callbacks.remove(callback)

        return remove_callback

    def register_disconnected_callback(
        self, callback: Callable[[], None]
    ) -> Callable[[], None]:
        """Register a callback to be called when device is disconnected."""
        self._disconnect_callbacks.append(callback)

        def remove_callback() -> None:
            """Remove the callback."""
            self._disconnect_callbacks.remove(callback)

        return remove_callback

    def _notify_callbacks(self, update: SensorUpdate) -> None:
        """Notify all registered callbacks."""
        for callback in self._callbacks:
            callback(update)

    def _notify_disconnect_callbacks(self) -> None:
        """Notify all disconnect callbacks."""
        for callback in self._disconnect_callbacks:
            callback()
