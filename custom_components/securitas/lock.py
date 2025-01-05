"""Locks for Securitas Direct."""

import logging
from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .apimanager import ApiManager
from .const import DOMAIN
from .coordinator import SecuritasDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: dict,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Securitas Direct locks."""
    coordinator: SecuritasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    api: ApiManager = coordinator.api

    entities = []
    devices = coordinator.data.get("devices", [])

    for device in devices:
        if device.get("type") == "Smart Lock":
            entities.append(
                SecuritasLock(
                    api=api,
                    coordinator=coordinator,
                    device_id=device["id"],
                    name=device["name"],
                )
            )
            _LOGGER.debug(
                "Added lock entity with ID: %s and name: %s",
                device["id"],
                device["name"],
            )

    async_add_entities(entities)


class SecuritasLock(LockEntity):
    """Representation of a Securitas Direct smart lock."""

    def __init__(
        self,
        api: ApiManager,
        coordinator: SecuritasDataUpdateCoordinator,
        device_id: str,
        name: str,
    ) -> None:
        """Initialize the lock with API and device info."""
        self._api = api
        self._coordinator = coordinator
        self._device_id = device_id
        self._name = name
        self._is_locked = None

    @property
    def name(self) -> str:
        """Return the name of the lock."""
        return self._name

    @property
    def is_locked(self) -> bool:
        """Return true if the lock is locked."""
        device = self._coordinator.data["devices"].get(self._device_id)
        if device:
            status = device.get("lock_status")
            _LOGGER.debug("Lock %s status: %s", self._device_id, status)
            return status == "locked"
        _LOGGER.warning("No status found for lock %s", self._device_id)
        return False

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the device."""
        _LOGGER.debug("Locking lock %s", self._device_id)
        response = await self._api._change_lock_mode(
            installation=self._coordinator.installation,
            device_id=self._device_id,
            lock=True,
        )
        if response.get("success"):
            await self._coordinator.async_request_refresh()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the device."""
        _LOGGER.debug("Unlocking lock %s", self._device_id)
        response = await self._api._change_lock_mode(
            installation=self._coordinator.installation,
            device_id=self._device_id,
            lock=False,
        )
        if response.get("success"):
            await self._coordinator.async_request_refresh()

    async def async_update(self) -> None:
        """Fetch the latest status from the API."""
        status = await self._api._get_lock_status(
            installation=self._coordinator.installation,
            device_id=self._device_id,
        )
        self._is_locked = status["is_locked"]
