"""Data coordinator for receiving SonicareBLETB updates."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from sensor_state_data import SensorUpdate

from .const import DOMAIN
from .device import SonicareBLETB

_LOGGER = logging.getLogger(__name__)

# Update interval for polling data
UPDATE_INTERVAL = timedelta(seconds=60)


class SonicareBLETBCoordinator(DataUpdateCoordinator[None]):
    """Data coordinator for receiving SonicareBLETB updates."""

    def __init__(self, hass: HomeAssistant, sonicare_ble: SonicareBLETB) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self._sonicare_ble = sonicare_ble
        sonicare_ble.register_callback(self._async_handle_update)
        sonicare_ble.register_disconnected_callback(self._async_handle_disconnect)
        self.connected = True

    async def _async_update_data(self) -> None:
        """Fetch data from the device."""
        _LOGGER.debug("Coordinator polling for data update")
        try:
            await self._sonicare_ble.update_data()
        except Exception as err:
            _LOGGER.error("Error updating data: %s", err, exc_info=True)
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    @callback
    def _async_handle_update(self, state: SensorUpdate) -> None:
        """Just trigger the callbacks."""
        _LOGGER.debug("_async_handle_update")
        self.connected = True
        self.async_set_updated_data(None)

    @callback
    def _async_handle_disconnect(self) -> None:
        """Trigger the callbacks for disconnected."""
        _LOGGER.info("_async_handle_disconnect")
        self.connected = False
        self.async_update_listeners()
