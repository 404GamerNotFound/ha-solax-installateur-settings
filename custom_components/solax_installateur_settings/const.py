DOMAIN = "solax_installateur_settings"
CONF_HOST = "host"
CONF_PASSWORD = "password"
CONF_SETTING = "setting"
CONF_VALUE = "value"
CONF_VIEW_ONLY = "view_only"
CONF_CONFIRM = "confirm"

# Mapping of inverter setting keys to human-friendly names. This allows the
# integration to present readable labels instead of raw keys, so users don't
# need to know or provide the internal key names themselves.
# Only a small subset of settings is known; unknown keys fall back to the raw
# key string.
SETTING_NAMES = {
    "feed_in_limit": "Feed-in Limit",
}
