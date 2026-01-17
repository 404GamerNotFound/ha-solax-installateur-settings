"""Client for interacting with Solax inverter installer settings."""

from __future__ import annotations

from urllib.parse import urlparse

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession


class SolaxInstallerClient:
    """Simple HTTP client for Solax installer settings."""

    def __init__(
        self, hass: HomeAssistant, host: str, password: str, view_only: bool
    ) -> None:
        """Initialize client with Home Assistant session."""
        self._session = async_get_clientsession(hass)
        self._host = host
        self._password = password
        self._view_only = view_only

    @property
    def host(self) -> str:
        """Return the inverter host."""
        return self._host

    @property
    def _base_url(self) -> str:
        """Return the base URL for the inverter API."""
        parsed = urlparse(self._host)
        if parsed.scheme and parsed.netloc:
            return self._host.rstrip("/")
        return f"http://{self._host}"

    @property
    def view_only(self) -> bool:
        """Return if the client operates in view-only mode."""
        return self._view_only

    async def async_set_parameter(self, key: str, value: str) -> dict:
        """Set a parameter on the inverter via its HTTP API."""
        if self._view_only:
            raise PermissionError("Client is in view-only mode")
        url = f"{self._base_url}/api/installer/set"
        params = {"pwd": self._password, "key": key, "value": value}
        async with self._session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def async_get_all_settings(self) -> dict:
        """Return all installer settings from the inverter."""
        url = f"{self._base_url}/api/installer/getall"
        params = {"pwd": self._password}
        async with self._session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()
