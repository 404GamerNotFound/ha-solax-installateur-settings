# ha-solax-installateur-settings

[English](README.md) | [Español](README.es.md) | [Français](README.fr.md)

Benutzerdefinierte Home Assistant-Integration zum Verwalten der **kennwortgeschützten Installateur-Einstellungen** von SolaX-Hybrid-Wechselrichtern (Gen4/Gen5, z. B. **X3-IES**) über **Modbus TCP**.

Das Installateur-Kennwort wird in das Entsperr-Register des Wechselrichters geschrieben (Holding-Register `0x0000`). Danach meldet der Wechselrichter seinen Sperrstatus (Input-Register `0x0054`: gesperrt / entsperrt / entsperrt erweitert) – ein falsches Kennwort wird so sofort erkannt.

## Voraussetzungen

- Home Assistant 2024.11 oder neuer
- Modbus-TCP-Zugriff auf den Wechselrichter (dieselbe IP/Port wie z. B. bei der `solax_modbus`-Integration, Standard-Port `502`, Unit-ID `1`)
- Das numerische Installateur-Kennwort des Wechselrichters (z. B. `2014` für Basis- oder `6868` für erweiterte Einstellungen)

## Installation

### Über HACS

1. In HACS das **benutzerdefinierte Repository** `https://github.com/404GamerNotFound/ha-solax-installateur-settings` als Typ *Integration* hinzufügen.
2. In HACS nach `Solax Installer Settings` suchen und installieren.
3. Home Assistant neu starten.

### Manuelle Installation

1. Den Ordner `custom_components/solax_installateur_settings` in das `custom_components`-Verzeichnis von Home Assistant kopieren.
2. Home Assistant neu starten.

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen → Solax Installer Settings**.
2. Host, Modbus-TCP-Port, Unit-ID und das **Installateur-Kennwort** eingeben. Die Integration verbindet sich, liest die Seriennummer und entsperrt den Wechselrichter testweise mit dem Kennwort. Bei falschem Kennwort erscheint *„Der Wechselrichter bleibt gesperrt“*.
3. Standardmäßig läuft die Integration im **Nur-Lesen-Modus**. Unter **Konfigurieren** kann er deaktiviert werden, um Änderungen zu erlauben. Dort lassen sich auch *„Wechselrichter nach jeder Änderung wieder sperren“* und das Abfrageintervall einstellen.
4. Host oder Kennwort lassen sich über **⋮ → Neu konfigurieren** ändern. Lehnt der Wechselrichter das gespeicherte Kennwort ab, fragt Home Assistant automatisch nach einem neuen.

## Entitäten

| Entität | Typ | Register (schreiben / lesen) |
| --- | --- | --- |
| Einspeisebegrenzung (W) | number | 0x42 / 0xB6 |
| Hauptsicherung Stromgrenze (A) | number | 0x71 / 0xD7 |
| Batterie max. Lade-/Entladestrom (A) | number | 0x24, 0x25 / 0x90, 0x91 |
| EPS min. SoC (%) | number | 0x44 / 0xB8 |
| Zähler 1 / Zähler 2 Richtung | select | 0xA4, 0xA5 / 0x10B, 0x10C |
| Netz-Bias-Richtung | select | 0x8D / 0xB2 |
| Schattenmanagement PV1–PV3 (GMPPT) | select | 0x9C, 0x98, 0xFC / 0x104, 0x114, 0x15F |
| Sperrstatus | sensor | Input 0x54 |
| Mit Installateur-Kennwort entsperren / Einstellungen sperren | button | 0x00 |

Jede Änderung entsperrt den Wechselrichter zuerst mit dem gespeicherten Kennwort, schreibt das Register und liest den Wert zur Kontrolle zurück.

Die Registerbelegung stammt aus der Community-Integration [homeassistant-solax-modbus](https://github.com/wills106/homeassistant-solax-modbus) für Gen4/Gen5-Hybride. Andere Modelle können andere Register nutzen – Verwendung auf eigene Gefahr.

## Dienste

```yaml
action: solax_installateur_settings.set_installer_setting
data:
  setting: Feed-in Limit   # Schlüssel oder Name
  value: 4500
  confirm: true            # Pflicht-Sicherheitsschalter
  # host: 192.168.1.100    # nur bei mehreren Wechselrichtern
```

```yaml
action: solax_installateur_settings.get_installer_settings   # liefert alle Werte + Sperrstatus
```

```yaml
action: solax_installateur_settings.unlock   # mit gespeichertem Kennwort entsperren
```

## Hinweise

- Verbindungen werden nur für eine Abfrage oder einen Schreibvorgang geöffnet und danach wieder geschlossen – so läuft die Integration parallel zu `solax_modbus`. Erlaubt dein Wechselrichter/Dongle nur einen Modbus-TCP-Client, erhöhe das Abfrageintervall.
- Das Sperren (Button oder Option *wieder sperren*) blockiert auch Schreibzugriffe anderer Integrationen, bis wieder entsperrt wird.
