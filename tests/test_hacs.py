import json
from pathlib import Path

DOMAIN = "solax_installateur_settings"


def test_manifest_has_iot_class():
    manifest_path = Path(__file__).resolve().parent.parent / "custom_components" / DOMAIN / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    assert manifest.get("iot_class") == "local_polling"


def test_hacs_file():
    hacs_path = Path(__file__).resolve().parent.parent / "hacs.json"
    hacs = json.loads(hacs_path.read_text())
    assert hacs.get("name") == "Solax Installer Settings"
    assert DOMAIN in hacs.get("domains", [])
    assert hacs.get("brand") == "Solax"
