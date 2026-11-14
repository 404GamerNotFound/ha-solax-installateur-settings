# ha-solax-installateur-settings

[![Stars](https://img.shields.io/github/stars/404GamerNotFound/ha-solax-installateur-settings?style=for-the-badge&logo=github&logoColor=white&label=Stars&color=blue)](https://github.com/404GamerNotFound/ha-solax-installateur-settings/stargazers)
[![Sponsors](https://img.shields.io/github/sponsors/404GamerNotFound?style=for-the-badge&logo=github&logoColor=white&label=Sponsors&color=blue)](https://github.com/sponsors/404GamerNotFound)
[![PayPal](https://img.shields.io/badge/PayPal-ME-blue?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/TonyBrueser)
[![Revolut](https://img.shields.io/badge/Revolut-ME-blue?style=for-the-badge&logo=revolut&logoColor=white)](https://revolut.me/tony1995)

[Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md)

Custom Home Assistant integration to manage the **password-protected installer settings** of SolaX hybrid inverters (Gen4/Gen5, e.g. **X3-IES**) via **Modbus TCP**.

The installer password is written to the inverter's unlock register (holding register `0x0000`). The inverter then reports its lock state (input register `0x0054`: locked / unlocked / unlocked advanced), so a wrong password is detected immediately.

## Prerequisites

- Home Assistant 2024.11 or newer
- Modbus TCP access to the inverter (the same IP/port that e.g. the `solax_modbus` integration uses, default port `502`, unit ID `1`)
- The numeric installer password of the inverter (e.g. `2014` for basic or `6868` for advanced settings)

## Installation

### Via HACS

1. In HACS add the **Custom Repository** `https://github.com/404GamerNotFound/ha-solax-installateur-settings` as type *Integration*.
2. Search for `Solax Installer Settings` in HACS and install it.
3. Restart Home Assistant.

### Manual Installation

1. Copy `custom_components/solax_installateur_settings` into the `custom_components` directory of your Home Assistant installation.
2. Restart Home Assistant.

## Configuration

1. **Settings → Devices & Services → Add Integration → Solax Installer Settings**.
2. Enter host, Modbus TCP port, unit ID and the **installer password**. The integration connects, reads the serial number and unlocks the inverter with the password to verify it. A wrong password shows *"The inverter stayed locked"*.
3. By default the integration runs in **view-only mode**. Disable it under **Configure** to allow changes. There you can also enable *"Lock the inverter again after each change"* and set the polling interval.
4. Host or password can be changed via **⋮ → Reconfigure**. If the inverter rejects the stored password, Home Assistant asks for a new one (re-authentication).

## Entities

| Entity | Type | Register (write / read) |
| --- | --- | --- |
| Feed-in Limit (W) | number | 0x42 / 0xB6 |
| Main Breaker Current Limit (A) | number | 0x71 / 0xD7 |
| Battery Charge / Discharge Max Current (A) | number | 0x24, 0x25 / 0x90, 0x91 |
| EPS Min SoC (%) | number | 0x44 / 0xB8 |
| Meter 1 / Meter 2 Direction | select | 0xA4, 0xA5 / 0x10B, 0x10C |
| Grid Bias Direction | select | 0x8D / 0xB2 |
| Shadow Fix Level PV1–PV3 (GMPPT) | select | 0x9C, 0x98, 0xFC / 0x104, 0x114, 0x15F |
| Lock state | sensor | input 0x54 |
| Unlock with installer password / Lock settings | button | 0x00 |

Every change first unlocks the inverter with the stored password, writes the register and reads the value back.

The register map follows the community integration [homeassistant-solax-modbus](https://github.com/wills106/homeassistant-solax-modbus) for Gen4/Gen5 hybrids. Other models may use different registers – use at your own risk.

## Services

```yaml
action: solax_installateur_settings.set_installer_setting
data:
  setting: Feed-in Limit   # key or name
  value: 4500
  confirm: true            # required safety switch
  # host: 192.168.1.100    # only needed with multiple inverters
```

```yaml
action: solax_installateur_settings.get_installer_settings   # returns all values + lock state
```

```yaml
action: solax_installateur_settings.unlock   # unlock with the stored password
```

## Notes

- Connections are opened only for a poll or a write and closed again, so the integration can run next to `solax_modbus`. If your inverter/dongle allows only one Modbus TCP client, increase the polling interval.
- Locking the inverter (button or *relock* option) also blocks writes from other integrations until it is unlocked again.

## Support

If you find this project helpful, you can support it via PayPal: [paypal.me/TonyBrueser](https://www.paypal.com/paypalme/TonyBrueser)
