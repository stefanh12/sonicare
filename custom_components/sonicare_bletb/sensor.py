"""Sonicare BLE toothbrush integration sensor platform."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SonicareBLETB, SonicareBLETBCoordinator
from .const import DOMAIN
from .models import SonicareBLETBData

_LOGGER = logging.getLogger(__name__)

BRUSHING_TIME_DESCRIPTION = SensorEntityDescription(
    key="brushing_time",
    device_class=SensorDeviceClass.DURATION,
    has_entity_name=True,
    name="Brushing time",
    native_unit_of_measurement=UnitOfTime.SECONDS,
    state_class=SensorStateClass.MEASUREMENT,
)

BATTERY_LEVEL_DESCRIPTION = SensorEntityDescription(
    key="battery_level",
    device_class=SensorDeviceClass.BATTERY,
    has_entity_name=True,
    name="Battery level",
    native_unit_of_measurement=PERCENTAGE,
    state_class=SensorStateClass.MEASUREMENT,
)

ROUTINE_LENGTH_DESCRIPTION = SensorEntityDescription(
    key="routine_length",
    device_class=SensorDeviceClass.DURATION,
    has_entity_name=True,
    name="Routine length",
    native_unit_of_measurement=UnitOfTime.SECONDS,
    state_class=SensorStateClass.MEASUREMENT,
)

HANDLE_STATE_DESCRIPTION = SensorEntityDescription(
    key="handle_state",
    device_class=None,
    has_entity_name=True,
    name="Handle state",
)

AVAILABLE_BRUSHING_ROUTINE_DESCRIPTION = SensorEntityDescription(
    key="available_brushing_routine",
    device_class=None,
    has_entity_name=True,
    name="Available brushing routine",
)

INTENSITY_DESCRIPTION = SensorEntityDescription(
    key="intensity",
    has_entity_name=True,
    name="Intensity",
)

LOADED_SESSION_ID_DESCRIPTION = SensorEntityDescription(
    key="loaded_session_id",
    has_entity_name=True,
    name="Loaded session id",
)

HANDLE_TIME_DESCRIPTION = SensorEntityDescription(
    key="handle_time",
    has_entity_name=True,
    name="Handle time",
)

BRUSHING_SESSION_ID_DESCRIPTION = SensorEntityDescription(
    key="brushing_session_id",
    has_entity_name=True,
    name="Brushing session id",
)

LAST_SESSION_ID_DESCRIPTION = SensorEntityDescription(
    key="last_session_id",
    has_entity_name=True,
    name="Last session id",
)


SENSOR_DESCRIPTIONS = [
    BRUSHING_TIME_DESCRIPTION,
    BATTERY_LEVEL_DESCRIPTION,
    ROUTINE_LENGTH_DESCRIPTION,
    HANDLE_STATE_DESCRIPTION,
    AVAILABLE_BRUSHING_ROUTINE_DESCRIPTION,
    INTENSITY_DESCRIPTION,
    LOADED_SESSION_ID_DESCRIPTION,
    HANDLE_TIME_DESCRIPTION,
    BRUSHING_SESSION_ID_DESCRIPTION,
    LAST_SESSION_ID_DESCRIPTION,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform for SonicareBLETB."""
    data: SonicareBLETBData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SonicareBLETBSensor(
            data.coordinator,
            data.device,
            entry.title,
            description,
        )
        for description in SENSOR_DESCRIPTIONS
    )


class SonicareBLETBSensor(
    CoordinatorEntity[SonicareBLETBCoordinator], SensorEntity, RestoreEntity
):
    """Generic sensor for SonicareBLETB."""

    def __init__(
        self,
        coordinator: SonicareBLETBCoordinator,
        device: SonicareBLETB,
        name: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = device
        self._key = description.key
        self.entity_description = description
        self._attr_unique_id = f"{device.address}_{self._key}"
        self._attr_device_info = DeviceInfo(
            name=name,
            connections={(dr.CONNECTION_BLUETOOTH, device.address)},
        )

    async def async_added_to_hass(self) -> None:
        """Handle entity being added to hass."""
        await super().async_added_to_hass()
        
        if not (last_state := await self.async_get_last_state()):
            return
        
        # Validate and convert the restored state based on sensor type
        if last_state.state in (None, "unknown", "unavailable"):
            return
        
        # For numeric sensors, validate the value
        if self.entity_description.device_class in (
            SensorDeviceClass.BATTERY,
            SensorDeviceClass.DURATION,
        ):
            try:
                # Try to convert to appropriate numeric type
                if self.entity_description.device_class == SensorDeviceClass.BATTERY:
                    value = int(last_state.state)
                    if 0 <= value <= 100:
                        self._attr_native_value = value
                else:
                    # Duration sensors
                    value = int(last_state.state)
                    if value >= 0:
                        self._attr_native_value = value
            except (ValueError, TypeError):
                # If conversion fails, don't restore the state
                _LOGGER.debug(
                    "Could not restore state %s for %s",
                    last_state.state,
                    self.entity_id,
                )
        else:
            # For non-numeric sensors, just restore the string value
            self._attr_native_value = last_state.state

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = getattr(self._device, self._key)
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Unavailable if coordinator isn't connected."""
        return self._coordinator.connected

    @property
    def assumed_state(self) -> bool:
        return not self._coordinator.connected

    @property
    def native_value(self) -> str | int | None:
        return getattr(self._device, self._key)
