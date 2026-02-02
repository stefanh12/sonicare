"""Sonicare BLE device wrapper."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from bleak import BleakClient, BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import establish_connection
from sensor_state_data import SensorUpdate

_LOGGER = logging.getLogger(__name__)
_LOGGER.warning("Loading device.py module")

# Sonicare service UUID
SONICARE_SERVICE_UUID = "477ea600-a260-11e4-ae37-0002a5d50001"


class SonicareBLETB:
    """Wrapper for Sonicare BLE toothbrush with active connection."""

    def __init__(self, ble_device: BLEDevice) -> None:
        """Initialize the Sonicare BLE device."""
        _LOGGER.warning("Initializing SonicareBLETB for device: %s", ble_device.address)
        self._ble_device = ble_device
        self._client: BleakClient | None = None
        self._callbacks: list[Callable[[SensorUpdate], None]] = []
        self._disconnect_callbacks: list[Callable[[], None]] = []
        self._connect_lock = asyncio.Lock()
        self._is_connected = False

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

        # Discovered characteristics
        self._characteristics: dict[str, str] = {}
        _LOGGER.warning("Initialized sensor attributes for %s", ble_device.address)

    @property
    def address(self) -> str:
        """Return the address of the device."""
        return self._ble_device.address

    async def initialise(self) -> None:
        """Initialize the device and discover characteristics."""
        _LOGGER.warning("initialise() called for device: %s", self._ble_device.address)
        await self._connect()
        await self._discover_characteristics()

        # Try to read initial data
        await self.update_data()

    async def stop(self) -> None:
        """Stop the device and disconnect."""
        _LOGGER.warning("Stopping Sonicare BLE device: %s", self._ble_device.address)
        await self._disconnect()

    async def _connect(self) -> None:
        """Connect to the BLE device."""
        async with self._connect_lock:
            if self._is_connected and self._client and self._client.is_connected:
                return

            _LOGGER.warning("Connecting to device: %s", self._ble_device.address)
            try:
                self._client = await establish_connection(
                    BleakClient,
                    self._ble_device,
                    self._ble_device.address,
                )
                self._is_connected = True
                _LOGGER.warning("Successfully connected to %s", self._ble_device.address)
            except BleakError as err:
                _LOGGER.error("Failed to connect to %s: %s", self._ble_device.address, err)
                self._is_connected = False
                raise

    async def _disconnect(self) -> None:
        """Disconnect from the BLE device."""
        async with self._connect_lock:
            if self._client and self._client.is_connected:
                _LOGGER.warning("Disconnecting from device: %s", self._ble_device.address)
                try:
                    await self._client.disconnect()
                except BleakError as err:
                    _LOGGER.error("Error disconnecting from %s: %s", self._ble_device.address, err)
                finally:
                    self._is_connected = False
                    self._notify_disconnect_callbacks()

    async def _discover_characteristics(self) -> None:
        """Discover all services and characteristics."""
        if not self._client or not self._client.is_connected:
            await self._connect()

        _LOGGER.warning("Discovering services and characteristics for %s", self._ble_device.address)

        try:
            services = self._client.services
            for service in services:
                _LOGGER.warning("Service: %s - %s", service.uuid, service.description)
                for char in service.characteristics:
                    _LOGGER.warning("  Characteristic: %s - Properties: %s",
                                  char.uuid, char.properties)
                    self._characteristics[char.uuid] = service.uuid

                    # Try to read characteristic if readable
                    if "read" in char.properties:
                        try:
                            value = await self._client.read_gatt_char(char.uuid)
                            _LOGGER.warning("    Value: %s (hex: %s)", value, value.hex())
                        except Exception as err:
                            _LOGGER.warning("    Could not read: %s", err)
        except Exception as err:
            _LOGGER.error("Error discovering characteristics: %s", err, exc_info=True)

    async def update_data(self) -> None:
        """Read data from the device characteristics."""
        if not self._is_connected:
            try:
                await self._connect()
            except BleakError:
                _LOGGER.warning("Could not connect to update data")
                return

        if not self._client or not self._client.is_connected:
            return

        _LOGGER.warning("Updating data from device: %s", self._ble_device.address)

        # Read all readable characteristics
        for char_uuid, service_uuid in self._characteristics.items():
            try:
                value = await self._client.read_gatt_char(char_uuid)
                _LOGGER.warning("Read %s: %s (hex: %s)", char_uuid, value, value.hex())
                self._parse_characteristic(char_uuid, value)
            except Exception as err:
                _LOGGER.debug("Could not read %s: %s", char_uuid, err)

        # Notify callbacks with update
        update = SensorUpdate(
            title=f"Sonicare {self._ble_device.address[-5:]}",
            devices={}
        )
        self._notify_callbacks(update)

    def _parse_characteristic(self, uuid: str, value: bytes) -> None:
        """Parse characteristic value and update sensor attributes."""
        # This is where we'll parse the characteristic data
        # For now, just log what we receive
        _LOGGER.warning("Parsing characteristic %s with value: %s", uuid, value.hex())

        # Common GATT characteristics
        if uuid.lower() == "00002a19-0000-1000-8000-00805f9b34fb":  # Battery Level
            if len(value) > 0:
                self.battery_level = value[0]
                _LOGGER.warning("Battery level: %d%%", self.battery_level)

    def set_ble_device_and_advertisement_data(
        self, ble_device: BLEDevice, advertisement_data: Any
    ) -> None:
        """Update BLE device reference (for advertisement tracking)."""
        self._ble_device = ble_device
        _LOGGER.debug("Updated BLE device reference for %s", ble_device.address)

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
