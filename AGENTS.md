# AGENTS.md – ha-solax-installateur-settings

Projektwissen für KI-Agenten. **Vor jedem Projekt-Scan zuerst diese Datei lesen.**

## Zweck
HACS-Custom-Integration (`custom_components/solax_installateur_settings`, Domain `solax_installateur_settings`) zum Lesen/Ändern der kennwortgeschützten Installateur-Einstellungen von SolaX-Hybrid-Wechselrichtern (Gen4/Gen5, Zielgerät des Maintainers: **X3-IES-12kW**, angebunden in HA zusätzlich über `solax_modbus`).

## Architektur
- `modbus.py` – eigener, abhängigkeitsfreier asyncio-Modbus-TCP-Client (FC03/FC04/FC06). Bewusst **kein pymodbus**, um Versionskonflikte mit `solax_modbus` zu vermeiden. Kein HA-Import.
- `settings.py` – Registerkarte (`InstallerSetting`: write_register, read_register, scale, min/max, options). Native = raw × scale. Kein HA-Import.
- `api.py` – `SolaxInstallerClient`: Passwort → Holding `0x0000`, Sperrstatus ← Input `0x0054` (0 gesperrt, 1 entsperrt, 2 erweitert). Seriennummer ← Holding `0x0000`–`0x0006` (ASCII). Verbindung pro Vorgang öffnen/schließen, asyncio.Lock serialisiert. Kein HA-Import.
- `coordinator.py` – DataUpdateCoordinator (Polling, Schreiben, Reauth bei `InvalidPassword`).
- Plattformen: `number.py`, `select.py`, `sensor.py` (Sperrstatus), `button.py` (Entsperren/Sperren). Basis: `entity.py`.
- `config_flow.py` – VERSION 2: user (Kennwort wird beim Einrichten geprüft), reauth, reconfigure, Options (view_only, relock_after_write, scan_interval). Migration v1→v2 in `__init__.py`.
- Services (`__init__.py`, `services.yaml`): `set_installer_setting` (confirm: true Pflicht), `get_installer_settings` (Response), `unlock`.
- Texte: `strings.json`, `translations/en.json`, `translations/de.json` (werden aus den Settings generiert – bei neuen Settings Namen + Select-States ergänzen).

## Registerquelle
Gen4/Gen5-Hybrid-Map aus wills106/homeassistant-solax-modbus (`plugin_solax.py`). Neue Settings nur mit dort belegter Schreib- **und** Rücklese-Adresse aufnehmen.

## Tests
- `pytest tests` – reine Tests (Fake-Modbus-Server in `tests/test_modbus.py`), laufen ohne HA.
- Mit `pip install pytest-homeassistant-custom-component` zusätzlich `tests/test_integration.py` (echter HA-Core: Config Flow, Entities, Services, Reauth, Migration); Aufruf `pytest tests -o asyncio_mode=auto`.
- CI (`.github/workflows/validate.yaml`): hassfest + HACS-Validierung.

## Konventionen
- Sicherheitsstandard: view_only = True, Services brauchen `confirm: true`.
- READMEs in EN/DE (ausführlich) sowie ES/FR (Kurzfassung) synchron halten.
- Version in `manifest.json` pflegen.
