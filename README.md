# ha-solax-installateur-settings

[Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md)

Custom Home Assistant integration to manage installer settings on SolaX inverters via the local HTTP API. It allows changing installer parameters without leaving Home Assistant.

## Prerequisites

- A working Home Assistant installation
- Access to the inverter's local network
- The inverter's installer password

## Installation

### Via HACS

1. In HACS add the **Custom Repository** `https://github.com/404GamerNotFound/ha-solax-installateur-settings` as type *Integration*.
2. After adding, search for `Solax Installer Settings` in HACS and install it.
3. Restart Home Assistant.

### Manual Installation

1. Copy the directory `custom_components/solax_installateur_settings` into the `custom_components` directory of your Home Assistant installation.
2. Restart Home Assistant.

## Configuration

1. In Home Assistant go to **Settings → Devices & Services → Add Integration**.
2. Select `Solax Installer Settings` and enter the IP address/hostname and the inverter's installer password.
3. After setup, the host or password can be updated via **Configure** in the integration. The available installer parameters are loaded directly from the inverter and shown in a dropdown with the current value, allowing changes without knowing the key. By default the integration runs in *view-only* mode to avoid accidental changes. Disable this option in the integration settings to allow modifications.

## Services

The integration provides services to retrieve and set installer parameters:

```yaml
service: solax_installateur_settings.set_installer_setting
data:
  setting: feed_in_limit
  value: 50
  confirm: true
  # host: 192.168.1.100  # optional, required when using multiple inverters
```
`confirm: true` is required as a safety measure; calls without it are rejected.

```yaml
service: solax_installateur_settings.get_installer_settings
data:
  # host: 192.168.1.100  # optional, required when using multiple inverters
```

Both services support multiple inverters; in that case the `host` field must be set so the correct client is selected.

## Implementation

Communication with the inverter is handled by the internal `SolaxInstallerClient` defined in `custom_components/solax_installateur_settings/api.py`. The HTTP API may vary by inverter model; adjust `api.py` if needed.

