"""The Sonicare BLE toothbrush integration."""

from __future__ import annotations

import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from sonicare_bletb import BLEAK_EXCEPTIONS, SonicareBLETB

from .const import DOMAIN
from .coordinator import SonicareBLETBCoordinator
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
