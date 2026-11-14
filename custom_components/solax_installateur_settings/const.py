"""Constants for the Solax installer settings integration."""

DOMAIN = "solax_installateur_settings"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_UNIT_ID = "unit_id"
CONF_PASSWORD = "password"
CONF_VIEW_ONLY = "view_only"
CONF_RELOCK = "relock_after_write"
CONF_SCAN_INTERVAL = "scan_interval"

CONF_SETTING = "setting"
CONF_VALUE = "value"
CONF_CONFIRM = "confirm"

DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 60  # seconds
DEFAULT_VIEW_ONLY = True
DEFAULT_RELOCK = False

SERVICE_SET = "set_installer_setting"
SERVICE_GET = "get_installer_settings"
SERVICE_UNLOCK = "unlock"

MANUFACTURER = "SolaX Power"
