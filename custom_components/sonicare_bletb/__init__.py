"""The Sonicare BLE toothbrush integration."""

from __future__ import annotations

import logging

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.match import ADDRESS, BluetoothCallbackMatcher
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from bleak_retry_connector import BLEAK_EXCEPTIONS

from .const import DOMAIN
from .coordinator import SonicareBLETBCoordinator
from .device import SonicareBLETB
from .models import SonicareBLETBData

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

__all__ = ["SonicareBLETB", "SonicareBLETBCoordinator"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sonicare BLE toothbrush from a config entry."""
    address: str = entry.data[CONF_ADDRESS]

    ble_device = bluetooth.async_ble_device_from_address(
        hass, address.upper(), connectable=True
    )
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find Sonicare BLE device with address {address}"
        )

    device = SonicareBLETB(ble_device)

    try:
        await device.initialise()
    except BLEAK_EXCEPTIONS as ex:
        raise ConfigEntryNotReady(
            f"Could not connect to Sonicare BLE device with address {address}"
        ) from ex

    coordinator = SonicareBLETBCoordinator(hass, device)

    @callback
    def _async_update_ble(
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Update from a ble callback."""
        _LOGGER.warning(
            "_async_update_ble callback triggered - address: %s, change: %s, name: %s",
            service_info.address,
            change,
            service_info.name
        )
        _LOGGER.warning("Calling set_ble_device_and_advertisement_data")
        device.set_ble_device_and_advertisement_data(
            service_info.device, service_info.advertisement
        )

    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            _async_update_ble,
            BluetoothCallbackMatcher({ADDRESS: address}),
            bluetooth.BluetoothScanningMode.ACTIVE,
        )
    )
    _LOGGER.warning("Registered BLE callback for address: %s", address)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = SonicareBLETBData(
        title=entry.title,
        device=device,
        coordinator=coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data: SonicareBLETBData = hass.data[DOMAIN].pop(entry.entry_id)
        await data.device.stop()

    return unload_ok
