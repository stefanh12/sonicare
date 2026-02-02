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
        _LOGGER.warning("Initializing SonicareBLETB for device: %s", ble_device.address)
        self._ble_device = ble_device
        self._parser = OralBBluetoothDeviceData()
        self._callbacks: list[Callable[[SensorUpdate], None]] = []
        self._disconnect_callbacks: list[Callable[[], None]] = []

        # Initialize sensor attributes with None
        self.brushing_time: int | None = None
        self.battery_level: int | None = None
        self.routine_length: int | None = None
        self.handle_state: str | None = None
        self.available_brushing_routine: str | None = None
        self.intensity: str | None = None
        self.loaded_session_id: str | None = None
        self.handle_time: int | None = None
        self.brushing_session_id: str | None = None
        self.last_session_id: str | None = None
        _LOGGER.warning("Initialized sensor attributes for %s", ble_device.address)

    @property
    def address(self) -> str:
        """Return the address of the device."""
        return self._ble_device.address

    async def initialise(self) -> None:
        """Initialize the device (no-op for passive monitoring)."""
        _LOGGER.warning("initialise() called for device: %s", self._ble_device.address)
        # For passive monitoring, no initialization needed
        # Set initial values
        self.battery_level = 100
        self.brushing_time = 0
        _LOGGER.warning("Set initial values: battery_level=100, brushing_time=0")
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
        _LOGGER.warning("Updated BLE device and advertisement data for %s", ble_device.address)

        # Log advertisement data details
        if hasattr(advertisement_data, 'manufacturer_data'):
            _LOGGER.warning("Manufacturer data: %s", advertisement_data.manufacturer_data)

        # Parser is called directly from __init__.py with the proper service_info
        # Just set some default values to make sensors available
        if self.battery_level is None:
            self.battery_level = 100
        if self.brushing_time is None:
            self.brushing_time = 0

        # Notify callbacks with update
        update = SensorUpdate(
            title=f"Sonicare {ble_device.address[-5:]}",
            devices={}
        )
        self._notify_callbacks(update)

    def register_callback(
        self, callback: Callable[[SensorUpdate], None]
    ) -> Callable[[], None]:
        """Register a callback to be called when data is updated."""
        _LOGGER.warning("Registering callback, total callbacks: %d", len(self._callbacks) + 1)
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
        _LOGGER.warning("_notify_callbacks called with %d callbacks", len(self._callbacks))
        for i, callback in enumerate(self._callbacks):
            _LOGGER.warning("Calling callback %d", i)
            try:
                callback(update)
            except Exception as err:
                _LOGGER.error("Error in callback %d: %s", i, err, exc_info=True)

    def _notify_disconnect_callbacks(self) -> None:
        """Notify all disconnect callbacks."""
        for callback in self._disconnect_callbacks:
            callback()
