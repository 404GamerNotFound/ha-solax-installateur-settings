"""Client for SolaX installer settings via Modbus TCP.

The installer password is written to holding register 0x0000. The inverter
then reports the lock state in input register 0x0054 (0 = locked,
1 = unlocked, 2 = unlocked advanced). A wrong password leaves the inverter
locked, which is how the password is validated.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from .modbus import ModbusError, ModbusTcpClient, registers_to_string
from .settings import (
    LOCK_STATES,
    REG_LOCK_STATE,
    REG_SERIAL,
    REG_UNLOCK,
    SERIAL_LENGTH,
    SETTINGS,
    InstallerSetting,
    find_setting,
)

_LOGGER = logging.getLogger(__name__)


class InvalidPassword(Exception):
    """Raised when the inverter stays locked after sending the password."""


class ViewOnlyError(PermissionError):
    """Raised when a write is attempted in view-only mode."""


def parse_password(password: str | int) -> int:
    """Validate the installer password (the inverter expects a number)."""
    text = str(password).strip()
    if not text.isdigit() or not 0 < int(text) <= 0xFFFF:
        raise InvalidPassword("The installer password must be a number (e.g. 6868)")
    return int(text)


class SolaxInstallerClient:
    """Read and write SolaX installer settings."""

    def __init__(
        self,
        host: str,
        port: int,
        unit_id: int,
        password: str,
        view_only: bool = True,
        relock_after_write: bool = False,
        timeout: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self._password = parse_password(password)
        self.view_only = view_only
        self.relock_after_write = relock_after_write
        self._timeout = timeout
        self._lock = asyncio.Lock()
        self.serial: str | None = None

    def _client(self) -> ModbusTcpClient:
        return ModbusTcpClient(self.host, self.port, self.unit_id, self._timeout)

    # -- helpers operating on an open connection -------------------------
    @staticmethod
    async def _read_lock_state(client: ModbusTcpClient) -> int:
        return (await client.read_input_registers(REG_LOCK_STATE, 1))[0]

    async def _unlock(self, client: ModbusTcpClient) -> int:
        await client.write_register(REG_UNLOCK, self._password)
        await asyncio.sleep(0.2)
        state = await self._read_lock_state(client)
        if state == 0:
            raise InvalidPassword("Inverter is still locked - wrong installer password?")
        return state

    @staticmethod
    async def _read_serial(client: ModbusTcpClient) -> str:
        return registers_to_string(
            await client.read_holding_registers(REG_SERIAL, SERIAL_LENGTH)
        )

    # -- public API ------------------------------------------------------
    async def async_validate(self) -> dict[str, Any]:
        """Connect, read the serial number and check the password."""
        async with self._lock, self._client() as client:
            self.serial = await self._read_serial(client)
            state = await self._unlock(client)
        return {"serial": self.serial, "lock_state": LOCK_STATES.get(state, state)}

    async def async_unlock(self) -> str:
        async with self._lock, self._client() as client:
            state = await self._unlock(client)
        return LOCK_STATES.get(state, str(state))

    async def async_lock(self) -> str:
        async with self._lock, self._client() as client:
            await client.write_register(REG_UNLOCK, 0)
            state = await self._read_lock_state(client)
        return LOCK_STATES.get(state, str(state))

    async def async_read_all(self) -> dict[str, Any]:
        """Return raw values of all settings plus lock state and serial."""
        data: dict[str, Any] = {"settings": {}}
        async with self._lock, self._client() as client:
            if self.serial is None:
                try:
                    self.serial = await self._read_serial(client)
                except ModbusError as err:
                    _LOGGER.debug("Reading serial number failed: %s", err)
            data["serial"] = self.serial
            data["lock_state"] = await self._read_lock_state(client)
            for setting in SETTINGS:
                try:
                    data["settings"][setting.key] = (
                        await client.read_holding_registers(setting.read_register, 1)
                    )[0]
                except ModbusError as err:
                    if not client.connected:
                        raise
                    _LOGGER.debug("Reading %s failed: %s", setting.key, err)
                    data["settings"][setting.key] = None
        return data

    async def async_get_all_settings(self) -> dict[str, Any]:
        """Return all settings as human readable values (service response)."""
        data = await self.async_read_all()
        result = {}
        for setting in SETTINGS:
            raw = data["settings"].get(setting.key)
            result[setting.name] = None if raw is None else setting.raw_to_native(raw)
        return {
            "serial": data.get("serial"),
            "lock_state": LOCK_STATES.get(data["lock_state"], data["lock_state"]),
            "settings": result,
        }

    async def async_set_setting(
        self, setting: InstallerSetting | str, value: Any
    ) -> float | str | None:
        """Unlock with the password, write the value and read it back."""
        if self.view_only:
            raise ViewOnlyError("Integration is in view-only mode")
        if isinstance(setting, str):
            setting = find_setting(setting)
        raw = setting.native_to_raw(value)
        async with self._lock, self._client() as client:
            await self._unlock(client)
            _LOGGER.info(
                "Writing %s (register 0x%04x) = %s (raw %s)",
                setting.key,
                setting.write_register,
                value,
                raw,
            )
            await client.write_register(setting.write_register, raw)
            await asyncio.sleep(0.5)
            readback = (await client.read_holding_registers(setting.read_register, 1))[0]
            if self.relock_after_write:
                await client.write_register(REG_UNLOCK, 0)
        if readback != raw:
            _LOGGER.warning(
                "%s: inverter reports %s after writing %s", setting.key, readback, raw
            )
        return setting.raw_to_native(readback)
