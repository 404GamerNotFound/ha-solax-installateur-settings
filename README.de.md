# ha-solax-installateur-settings

Benutzerdefinierte Home Assistant-Integration zum Verwalten von Installateur-Einstellungen auf SolaX-Wechselrichtern über die lokale HTTP-API. Sie ermöglicht das Ändern von Installateurparametern, ohne Home Assistant zu verlassen.

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
3. Nach der Einrichtung kann über **Konfigurieren** in der Integration der Host oder das Passwort angepasst werden. Die verfügbaren Installateur-Parameter werden direkt vom Wechselrichter geladen und in einer Auswahlliste inklusive des aktuellen Wertes angezeigt, sodass Einstellungen geändert werden können, ohne den Schlüssel zu kennen. Standardmäßig läuft die Integration im *Nur-Lesen*-Modus, um unbeabsichtigte Änderungen zu vermeiden. Dieser Modus kann in den Integrationsoptionen deaktiviert werden, um Änderungen zu ermöglichen.

## Dienste

Die Integration stellt Dienste bereit, um Installateur-Parameter abzurufen und zu setzen:

```yaml
service: solax_installateur_settings.set_installer_setting
data:
  setting: feed_in_limit
  value: 50
  confirm: true
  # host: 192.168.1.100  # optional, notwendig bei mehreren Wechselrichtern
```
`confirm: true` ist als Sicherheitsmaßnahme erforderlich; Aufrufe ohne diese Bestätigung werden abgelehnt.

```yaml
service: solax_installateur_settings.get_installer_settings
data:
  # host: 192.168.1.100  # optional, notwendig bei mehreren Wechselrichtern
```

Beide Dienste unterstützen mehrere Wechselrichter; in diesem Fall muss das Feld `host` gesetzt werden, damit der richtige Client ausgewählt wird.

## Implementierung

Die Kommunikation mit dem Wechselrichter wird vom internen `SolaxInstallerClient` in `custom_components/solax_installateur_settings/api.py` übernommen. Die HTTP-API kann je nach Wechselrichtermodell variieren; bei Bedarf `api.py` anpassen.

