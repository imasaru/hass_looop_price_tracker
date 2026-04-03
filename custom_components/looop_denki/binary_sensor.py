"""Binary sensor platform for the Looop Denki integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LooopDenkiConfigEntry
from .const import ATTR_CURRENT_LEVEL, ATTR_STATUS, DOMAIN
from .coordinator import LooopDenkiCoordinator

# Price status values used by the API client
_STATUS_GOOD = "でんき日和"
_STATUS_WARNING = "でんき注意報"
_STATUS_ALERT = "でんき警報"


@dataclass(frozen=True, kw_only=True)
class LooopDenkiBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Looop Denki binary sensor entity."""

    is_on_fn: Callable[[LooopDenkiBinarySensor], bool | None]
    extra_fn: Callable[[LooopDenkiBinarySensor], dict[str, Any] | None] | None = None


BINARY_SENSOR_TYPES: tuple[LooopDenkiBinarySensorEntityDescription, ...] = (
    LooopDenkiBinarySensorEntityDescription(
        key="cheap_now",
        translation_key="cheap_now",
        name="Cheap Now",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda sensor: (
            _is_cheap(sensor.coordinator.data.get("current_info", {}))
            if sensor.coordinator.data
            else None
        ),
        extra_fn=lambda sensor: (
            {
                ATTR_STATUS: sensor.coordinator.data.get("current_info", {}).get(
                    "status"
                ),
                ATTR_CURRENT_LEVEL: sensor.coordinator.data.get(
                    "current_info", {}
                ).get("current_level"),
            }
            if sensor.coordinator.data
            and sensor.coordinator.data.get("current_info")
            else None
        ),
    ),
    LooopDenkiBinarySensorEntityDescription(
        key="price_alert",
        translation_key="price_alert",
        name="Price Alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda sensor: (
            _is_alert(sensor.coordinator.data.get("current_info", {}))
            if sensor.coordinator.data
            else None
        ),
        extra_fn=lambda sensor: (
            {
                ATTR_STATUS: sensor.coordinator.data.get("current_info", {}).get(
                    "status"
                ),
                ATTR_CURRENT_LEVEL: sensor.coordinator.data.get(
                    "current_info", {}
                ).get("current_level"),
            }
            if sensor.coordinator.data
            and sensor.coordinator.data.get("current_info")
            else None
        ),
    ),
)


def _is_cheap(current_info: dict[str, Any]) -> bool | None:
    """Return True when current price is in the cheap (でんき日和) range."""
    if not current_info:
        return None
    status = current_info.get("status")
    if status is not None:
        return status == _STATUS_GOOD
    level = current_info.get("current_level")
    if level is not None:
        return float(level) < 0
    return None


def _is_alert(current_info: dict[str, Any]) -> bool | None:
    """Return True when current price is elevated (でんき注意報 or でんき警報)."""
    if not current_info:
        return None
    status = current_info.get("status")
    if status is not None:
        return status in {_STATUS_WARNING, _STATUS_ALERT}
    level = current_info.get("current_level")
    if level is not None:
        return float(level) > 0
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LooopDenkiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Looop Denki binary sensor entities."""
    coordinator = entry.runtime_data

    entities = [
        LooopDenkiBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSOR_TYPES
    ]

    async_add_entities(entities)


class LooopDenkiBinarySensor(
    CoordinatorEntity[LooopDenkiCoordinator], BinarySensorEntity
):
    """Binary sensor for Looop Denki electricity pricing state."""

    entity_description: LooopDenkiBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: LooopDenkiCoordinator,
        entry: LooopDenkiConfigEntry,
        description: LooopDenkiBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        self._area_code = entry.data["area_code"]
        area_names = coordinator.client.get_area_codes()
        area_name = area_names.get(self._area_code, f"Area {self._area_code}")

        self._attr_unique_id = f"{DOMAIN}_{self._area_code}_{description.key}"
        self._attr_translation_key = description.translation_key

        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._area_code)},
            "name": f"Looop でんき - {area_name}",
            "manufacturer": "株式会社Looop",
            "model": "でんき予報",
            "sw_version": "1.0",
        }

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        return self.entity_description.is_on_fn(self)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if self.entity_description.extra_fn:
            return self.entity_description.extra_fn(self)
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.last_update_success or not self.coordinator.data:
            return False
        return bool(self.coordinator.data.get("current_info"))
