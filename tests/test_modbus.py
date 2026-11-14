"""Tests for the Modbus client and installer client against a fake inverter."""

import asyncio
import struct
import sys

import pytest

modbus = sys.modules["solax_installer_pure.modbus"]
api = sys.modules["solax_installer_pure.api"]
settings = sys.modules["solax_installer_pure.settings"]

PASSWORDS = {2014: 1, 6868: 2}


class FakeInverter:
    """Tiny Modbus TCP server emulating the SolaX unlock behaviour."""

    def __init__(self):
        serial = b"H35A12ABCDEF01"
        self.holding = {i: struct.unpack(">H", serial[2 * i : 2 * i + 2])[0] for i in range(7)}
        self.input = {settings.REG_LOCK_STATE: 0}
        for s in settings.SETTINGS:
            self.holding[s.read_register] = 0
        self.writes = []

    async def handle(self, reader, writer):
        try:
            while True:
                header = await reader.readexactly(7)
                tid, _pid, length, unit = struct.unpack(">HHHB", header)
                pdu = await reader.readexactly(length - 1)
                resp = self.process(pdu)
                writer.write(struct.pack(">HHHB", tid, 0, len(resp) + 1, unit) + resp)
                await writer.drain()
        except asyncio.IncompleteReadError:
            writer.close()

    def process(self, pdu):
        fc = pdu[0]
        addr, val = struct.unpack(">HH", pdu[1:5])
        if fc in (3, 4):
            table = self.holding if fc == 3 else self.input
            regs = [table.get(addr + i, 0) for i in range(val)]
            return bytes([fc, 2 * val]) + struct.pack(f">{val}H", *regs)
        if fc == 6:
            self.writes.append((addr, val))
            if addr == settings.REG_UNLOCK:
                self.input[settings.REG_LOCK_STATE] = PASSWORDS.get(val, 0)
                return pdu
            if self.input[settings.REG_LOCK_STATE] == 0:
                return bytes([fc | 0x80, 4])
            for s in settings.SETTINGS:
                if s.write_register == addr:
                    self.holding[s.read_register] = val
            return pdu
        return bytes([fc | 0x80, 1])


@pytest.fixture
def run():
    loop = asyncio.new_event_loop()
    yield loop.run_until_complete
    loop.close()


async def _with_server(coro_factory):
    fake = FakeInverter()
    server = await asyncio.start_server(fake.handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    try:
        return fake, await coro_factory(port)
    finally:
        server.close()
        await server.wait_closed()


def test_validate_with_correct_password(run):
    async def go(port):
        client = api.SolaxInstallerClient("127.0.0.1", port, 1, "6868")
        return await client.async_validate()

    fake, result = run(_with_server(go))
    assert result == {"serial": "H35A12ABCDEF01", "lock_state": "unlocked_advanced"}
    assert fake.writes == [(0, 6868)]


def test_wrong_password_is_rejected(run):
    async def go(port):
        client = api.SolaxInstallerClient("127.0.0.1", port, 1, "1234")
        with pytest.raises(api.InvalidPassword):
            await client.async_validate()

    run(_with_server(go))


def test_password_must_be_numeric():
    with pytest.raises(api.InvalidPassword):
        api.parse_password("abc")


def test_set_number_with_scale(run):
    async def go(port):
        client = api.SolaxInstallerClient("127.0.0.1", port, 1, "2014", view_only=False)
        return await client.async_set_setting("Feed-in Limit", 4500)

    fake, value = run(_with_server(go))
    assert value == 4500
    assert fake.writes == [(0, 2014), (0x42, 450)]


def test_set_select_by_label_and_relock(run):
    async def go(port):
        client = api.SolaxInstallerClient(
            "127.0.0.1", port, 1, "2014", view_only=False, relock_after_write=True
        )
        value = await client.async_set_setting("meter_1_direction", "negative")
        return value, await client.async_get_all_settings()

    fake, (value, data) = run(_with_server(go))
    assert value == "Negative"
    assert fake.writes[-1] == (0, 0)
    assert data["lock_state"] == "locked"
    assert data["settings"]["Meter 1 Direction"] == "Negative"


def test_view_only_blocks_writes(run):
    async def go(port):
        client = api.SolaxInstallerClient("127.0.0.1", port, 1, "2014")
        with pytest.raises(api.ViewOnlyError):
            await client.async_set_setting("Feed-in Limit", 100)

    fake, _ = run(_with_server(go))
    assert fake.writes == []


def test_out_of_range_rejected():
    s = settings.find_setting("eps_min_soc")
    with pytest.raises(ValueError):
        s.native_to_raw(50)


def test_exception_response(run):
    async def go(port):
        async with modbus.ModbusTcpClient("127.0.0.1", port) as client:
            with pytest.raises(modbus.ModbusExceptionResponse) as err:
                await client.write_register(0x42, 1)
            return err.value.exception_code

    _, code = run(_with_server(go))
    assert code == 4


def test_connection_error(run):
    async def go():
        client = modbus.ModbusTcpClient("127.0.0.1", 1, timeout=1)
        with pytest.raises(modbus.ModbusConnectionError):
            await client.connect()

    run(go())
