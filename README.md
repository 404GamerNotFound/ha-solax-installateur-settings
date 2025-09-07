# ha-solax-installateur-settings

Custom Home Assistant integration to manage installer settings on SolaX inverters via the local HTTP API. It allows changing installer parameters without leaving Home Assistant.

## Voraussetzungen

- Eine funktionierende Home Assistant Installation
- Zugriff auf das lokale Netzwerk des Wechselrichters
- Das Installateur-Passwort des Wechselrichters

## Installation

### Über HACS

1. In HACS das **Benutzerdefinierte Repository** `https://github.com/404GamerNotFound/ha-solax-installateur-settings` als Typ *Integration* hinzufügen.
2. Nach dem Hinzufügen in HACS nach `Solax Installer Settings` suchen und installieren.
3. Home Assistant neu starten.

### Manuelle Installation

1. Das Verzeichnis `custom_components/solax_installateur_settings` in das `custom_components` Verzeichnis der Home Assistant-Installation kopieren.
2. Home Assistant neu starten.

## Konfiguration

1. In Home Assistant **Einstellungen → Geräte & Dienste → Integration hinzufügen** wählen.
2. `Solax Installer Settings` auswählen und die IP-Adresse/den Hostnamen sowie das Installateur-Passwort des Wechselrichters eingeben.
3. Nach der Einrichtung kann über **Konfigurieren** in der Integration der Host oder das Passwort angepasst werden. Zusätzlich lässt sich dort über ein Formular sofort ein Parameter setzen (Schlüssel und Wert angeben).

## Services

Die Integration stellt einen Dienst bereit, um Installateur-Parameter zu setzen:

```yaml
service: solax_installateur_settings.set_installer_setting
data:
  setting: feed_in_limit
  value: 50
  # host: 192.168.1.100  # optional, notwendig bei mehreren Wechselrichtern
```

Wenn mehrere Wechselrichter eingebunden sind, muss das Feld `host` gesetzt werden, damit der richtige Client ausgewählt wird.

## Implementation

Communication with the inverter is handled by the internal `SolaxInstallerClient` defined in `custom_components/solax_installateur_settings/api.py`. Die HTTP-API kann je nach Wechselrichtermodell variieren; bei Bedarf `api.py` anpassen.
