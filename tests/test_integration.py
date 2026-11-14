"""Integration tests with a real Home Assistant core against a fake inverter.

Requires ``pip install pytest-homeassistant-custom-component``; skipped otherwise.
"""

import asyncio
from pathlib import Path

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")
from unittest.mock import patch
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .test_modbus import FakeInverter

DOMAIN = "solax_installateur_settings"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    import custom_components

    repo_dir = str(Path(__file__).resolve().parent.parent / "custom_components")
    if repo_dir not in custom_components.__path__:
        custom_components.__path__.append(repo_dir)
    yield


@pytest.fixture
async def fake(socket_enabled):
    inv = FakeInverter()
    server = await asyncio.start_server(inv.handle, "127.0.0.1", 0)
    inv.port = server.sockets[0].getsockname()[1]
    yield inv
    server.close()
    await server.wait_closed()


def base(fake, pw="6868"):
    return {"host": "127.0.0.1", "port": fake.port, "unit_id": 1, "password": pw}


async def test_flow_wrong_then_right_password(hass, fake):
    r = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    r = await hass.config_entries.flow.async_configure(
        r["flow_id"], {**base(fake, "1111"), "view_only": False}
    )
    assert r["errors"] == {"base": "invalid_auth"}
    r = await hass.config_entries.flow.async_configure(
        r["flow_id"], {**base(fake), "view_only": False}
    )
    assert r["type"] is FlowResultType.CREATE_ENTRY, r
    assert r["result"].unique_id == "H35A12ABCDEF01"
    await hass.async_block_till_done()
    st = hass.states.get("sensor.solax_installer_settings_lock_state")
    assert st.state == "unlocked_advanced", hass.states.async_entity_ids()
    # write number via entity
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.solax_installer_settings_feed_in_limit", "value": 4500},
        blocking=True,
    )
    assert (0x42, 450) in fake.writes
    await hass.async_block_till_done()
    assert (
        hass.states.get("number.solax_installer_settings_feed_in_limit").state == "4500"
    )
    await hass.services.async_call(
        "select",
        "select_option",
        {
            "entity_id": "select.solax_installer_settings_meter_1_direction",
            "option": "negative",
        },
        blocking=True,
    )
    assert (0xA4, 1) in fake.writes
    resp = await hass.services.async_call(
        DOMAIN, "get_installer_settings", {}, blocking=True, return_response=True
    )
    assert resp["settings"]["Meter 1 Direction"] == "Negative"
    from homeassistant.exceptions import ServiceValidationError

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "set_installer_setting",
            {"setting": "Feed-in Limit", "value": 1, "confirm": False},
            blocking=True,
        )
    resp = await hass.services.async_call(
        DOMAIN,
        "set_installer_setting",
        {"setting": "Grid Bias Direction", "value": "Grid", "confirm": True},
        blocking=True,
        return_response=True,
    )
    assert resp == {"setting": "Grid Bias Direction", "value": "Grid"}


async def test_view_only_blocks(hass, fake):
    e = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="x",
        data=base(fake),
        options={"view_only": True},
    )
    e.add_to_hass(hass)
    assert await hass.config_entries.async_setup(e.entry_id)
    await hass.async_block_till_done()
    from homeassistant.exceptions import HomeAssistantError

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "number",
            "set_value",
            {
                "entity_id": "number.solax_installer_settings_feed_in_limit",
                "value": 100,
            },
            blocking=True,
        )
    assert fake.writes == []


async def test_wrong_stored_password_triggers_reauth(hass, fake):
    e = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="x",
        data=base(fake, "9999"),
        options={"view_only": False},
    )
    e.add_to_hass(hass)
    assert await hass.config_entries.async_setup(e.entry_id)
    await hass.async_block_till_done()
    from homeassistant.exceptions import HomeAssistantError

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "button",
            "press",
            {
                "entity_id": "button.solax_installer_settings_unlock_with_installer_password"
            },
            blocking=True,
        )
    await hass.async_block_till_done()
    flows = hass.config_entries.flow.async_progress()
    assert any(f["context"]["source"] == "reauth" for f in flows)
    f = [f for f in flows if f["context"]["source"] == "reauth"][0]
    r = await hass.config_entries.flow.async_configure(
        f["flow_id"], {"password": "2014"}
    )
    assert r["reason"] == "reauth_successful"
    assert e.data["password"] == "2014"


async def test_migration_v1(hass, fake):
    e = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        unique_id="old",
        data={"host": "http://127.0.0.1:80", "password": "6868", "view_only": True},
    )
    e.add_to_hass(hass)
    with patch("custom_components.solax_installateur_settings.DEFAULT_PORT", fake.port):
        assert await hass.config_entries.async_setup(e.entry_id)
    assert (
        e.version == 2
        and e.data["host"] == "127.0.0.1"
        and e.options["view_only"] is True
    )


async def test_options_flow(hass, fake):
    e = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="x",
        data=base(fake),
        options={"view_only": True},
    )
    e.add_to_hass(hass)
    assert await hass.config_entries.async_setup(e.entry_id)
    r = await hass.config_entries.options.async_init(e.entry_id)
    r = await hass.config_entries.options.async_configure(
        r["flow_id"],
        {"view_only": False, "relock_after_write": True, "scan_interval": 30},
    )
    assert r["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert (
        e.runtime_data.client.view_only is False
        and e.runtime_data.client.relock_after_write
    )
