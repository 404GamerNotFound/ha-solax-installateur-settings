"""Load the integration's pure-Python modules without Home Assistant."""

import importlib.util
import sys
import types
from pathlib import Path

PKG = "solax_installer_pure"
PKG_DIR = Path(__file__).resolve().parent.parent / "custom_components" / "solax_installateur_settings"

if PKG not in sys.modules:
    package = types.ModuleType(PKG)
    package.__path__ = [str(PKG_DIR)]
    sys.modules[PKG] = package
    for name in ("modbus", "settings", "api"):
        spec = importlib.util.spec_from_file_location(f"{PKG}.{name}", PKG_DIR / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"{PKG}.{name}"] = module
        spec.loader.exec_module(module)


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _allow_local_sockets(request):
    """The fake inverter needs localhost sockets (pytest-socket blocks them)."""
    try:
        request.getfixturevalue("socket_enabled")
    except pytest.FixtureLookupError:
        pass
    yield
