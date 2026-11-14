"""Minimal asyncio Modbus TCP client.

Only the function codes needed by this integration are implemented:
03 (read holding registers), 04 (read input registers) and
06 (write single register). The module has no Home Assistant or pymodbus
dependency, so it can be unit tested in isolation and does not clash with the
pymodbus version used by other integrations (e.g. solax_modbus).
"""

from __future__ import annotations

import asyncio
import struct

FC_READ_HOLDING = 0x03
FC_READ_INPUT = 0x04
FC_WRITE_SINGLE = 0x06

EXCEPTION_MESSAGES = {
    1: "illegal function",
    2: "illegal data address",
    3: "illegal data value",
    4: "server device failure",
    5: "acknowledge",
    6: "server device busy",
}


class ModbusError(Exception):
    """Base error for Modbus communication problems."""


class ModbusConnectionError(ModbusError):
    """Raised when the TCP connection fails or times out."""


class ModbusExceptionResponse(ModbusError):
    """Raised when the device answers with a Modbus exception."""

    def __init__(self, function_code: int, exception_code: int) -> None:
        self.function_code = function_code
        self.exception_code = exception_code
        msg = EXCEPTION_MESSAGES.get(exception_code, "unknown exception")
        super().__init__(
            f"Modbus exception {exception_code} ({msg}) for function 0x{function_code:02x}"
        )


class ModbusTcpClient:
    """Very small Modbus TCP client (one request at a time)."""

    def __init__(
        self, host: str, port: int = 502, unit_id: int = 1, timeout: float = 5.0
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._transaction_id = 0

    @property
    def connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def connect(self) -> None:
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), self.timeout
            )
        except (OSError, asyncio.TimeoutError) as err:
            raise ModbusConnectionError(
                f"Cannot connect to {self.host}:{self.port}: {err}"
            ) from err

    async def close(self) -> None:
        writer, self._writer, self._reader = self._writer, None, None
        if writer is None:
            return
        writer.close()
        try:
            await asyncio.wait_for(writer.wait_closed(), self.timeout)
        except (OSError, asyncio.TimeoutError):
            pass

    async def __aenter__(self) -> "ModbusTcpClient":
        await self.connect()
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    async def _request(self, pdu: bytes) -> bytes:
        if not self.connected or self._reader is None or self._writer is None:
            raise ModbusConnectionError("Not connected")
        self._transaction_id = (self._transaction_id + 1) & 0xFFFF
        tid = self._transaction_id
        header = struct.pack(">HHHB", tid, 0, len(pdu) + 1, self.unit_id)
        try:
            self._writer.write(header + pdu)
            await self._writer.drain()
            while True:
                mbap = await asyncio.wait_for(
                    self._reader.readexactly(7), self.timeout
                )
                r_tid, r_pid, r_len, _unit = struct.unpack(">HHHB", mbap)
                if r_len < 2:
                    raise ModbusError("Invalid Modbus frame length")
                body = await asyncio.wait_for(
                    self._reader.readexactly(r_len - 1), self.timeout
                )
                if r_pid != 0:
                    raise ModbusError("Invalid Modbus protocol id")
                if r_tid == tid:
                    break
                # Stale answer from an earlier request: skip it.
        except (OSError, asyncio.TimeoutError, asyncio.IncompleteReadError) as err:
            await self.close()
            raise ModbusConnectionError(f"Communication error: {err!r}") from err

        function_code = pdu[0]
        if body[0] == function_code | 0x80:
            raise ModbusExceptionResponse(function_code, body[1])
        if body[0] != function_code:
            raise ModbusError(
                f"Unexpected function code 0x{body[0]:02x} (expected 0x{function_code:02x})"
            )
        return body

    async def _read(self, function_code: int, address: int, count: int) -> list[int]:
        if not 1 <= count <= 125:
            raise ValueError("count must be between 1 and 125")
        body = await self._request(struct.pack(">BHH", function_code, address, count))
        byte_count = body[1]
        data = body[2 : 2 + byte_count]
        if byte_count != 2 * count or len(data) != byte_count:
            raise ModbusError("Unexpected register count in response")
        return list(struct.unpack(f">{count}H", data))

    async def read_holding_registers(self, address: int, count: int = 1) -> list[int]:
        return await self._read(FC_READ_HOLDING, address, count)

    async def read_input_registers(self, address: int, count: int = 1) -> list[int]:
        return await self._read(FC_READ_INPUT, address, count)

    async def write_register(self, address: int, value: int) -> None:
        if not 0 <= value <= 0xFFFF:
            raise ValueError("register value must be between 0 and 65535")
        pdu = struct.pack(">BHH", FC_WRITE_SINGLE, address, value)
        body = await self._request(pdu)
        if body != pdu:
            raise ModbusError("Write echo does not match request")


def registers_to_string(registers: list[int]) -> str:
    """Decode big-endian registers to an ASCII string."""
    raw = b"".join(struct.pack(">H", reg) for reg in registers)
    return raw.decode("ascii", errors="ignore").strip("\x00 ").strip()
