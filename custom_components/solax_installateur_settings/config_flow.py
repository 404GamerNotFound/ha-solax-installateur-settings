"""Config flow for Solax installer integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_HOST, CONF_PASSWORD, DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PASSWORD): str,
})


class SolaxInstallerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the integration."""

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Solax Installer", data=user_input)
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
