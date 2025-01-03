from homeassistant.components.lock import LockEntity
from .securitas_api import SecuritasDirectAPI

class SecuritasDirectLock(LockEntity):
    def __init__(self, api: SecuritasDirectAPI, device_id: str, name: str):
        self._api = api
        self._device_id = device_id
        self._name = name
        self._is_locked = None

    @property
    def name(self):
        return self._name

    @property
    def is_locked(self):
        return self._is_locked

    async def async_lock(self, **kwargs):
        await self._api.lock(self._device_id)
        self._is_locked = True
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs):
        await self._api.unlock(self._device_id)
        self._is_locked = False
        self.async_write_ha_state()

    async def async_update(self):
        self._is_locked = await self._api.get_lock_status(self._device_id)
