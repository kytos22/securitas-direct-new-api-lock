"""Locks for Securitas Direct."""

import logging
from homeassistant.components.lock import LockEntity
from .apimanager import APIManager

_LOGGER = logging.getLogger(__name__)


class SecuritasLock(LockEntity):
    """Representation of a Securitas Direct Smart Lock."""

    def __init__(self, installation, api: APIManager):
        """Initialize the smart lock."""
        self._installation = installation
        self._api = api
        self._is_locked = None  # Will be updated by the state check

    async def async_lock(self, **kwargs):
        """Lock the smart lock."""
        try:
            response = await self._api._change_lock_mode(self._installation, lock=True)
            if response.get("res") == "OK":
                self._is_locked = True
                self.async_write_ha_state()
            else:
                _LOGGER.error("Failed to lock the smart lock: %s", response.get("msg"))
        except Exception as e:
            _LOGGER.error("Error locking the smart lock: %s", e)

    async def async_unlock(self, **kwargs):
        """Unlock the smart lock."""
        try:
            response = await self._api._change_lock_mode(self._installation, lock=False)
            if response.get("res") == "OK":
                self._is_locked = False
                self.async_write_ha_state()
            else:
                _LOGGER.error("Failed to unlock the smart lock: %s", response.get("msg"))
        except Exception as e:
            _LOGGER.error("Error unlocking the smart lock: %s", e)

    @property
    def is_locked(self):
        """Return true if the lock is locked."""
        return self._is_locked

    async def async_update(self):
        """Fetch the latest state of the lock."""
        try:
            status = await self._api.get_lock_current_mode(self._installation)
            if status == "locked":
                self._is_locked = True
            elif status == "unlocked":
                self._is_locked = False
            else:
                _LOGGER.warning("Unknown lock status: %s", status)
        except Exception as e:
            _LOGGER.error("Error fetching lock status: %s", e)
