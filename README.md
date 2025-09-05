# ha-solax-installateur-settings

Custom Home Assistant integration to manage installer settings on Solax inverters.

## Installation

Copy the `custom_components/solax_installateur_settings` folder to your Home Assistant `custom_components` directory or install via HACS.

## Configuration

Use the Home Assistant UI to add the **Solax Installer Settings** integration and provide the inverter host and installer password.

## Services

The integration exposes a service to change an installer parameter:

```yaml
service: solax_installateur_settings.set_installer_setting
data:
  setting: feed_in_limit
  value: 50
```

The underlying HTTP API may differ between inverter models; adjust `api.py` if needed.

## Implementation

Communication with the inverter is handled by the internal `SolaxInstallerClient` defined in `custom_components/solax_installateur_settings/api.py`.
