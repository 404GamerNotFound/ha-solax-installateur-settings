"""Client for interacting with Solax inverter installer settings."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession


class SolaxInstallerClient:
    """Simple HTTP client for Solax installer settings."""

    def __init__(self, hass: HomeAssistant, host: str, password: str) -> None:
        """Initialize client with Home Assistant session."""
        self._session = async_get_clientsession(hass)
        self._host = host
        self._password = password

    async def async_set_parameter(self, key: str, value: str) -> dict:
        """Set a parameter on the inverter via its HTTP API."""
        url = f"http://{self._host}/api/installer/set"
        params = {"pwd": self._password, "key": key, "value": value}
        async with self._session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()
