"""Installer settings of SolaX Gen4/Gen5 hybrid inverters (e.g. X3-IES).

Register map taken from the community integration
https://github.com/wills106/homeassistant-solax-modbus (plugin_solax.py,
HYBRID | GEN4 | GEN5). Settings are written to one holding register and read
back from another holding register.

Native value = raw register value * ``scale``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Writing the installer password to this holding register unlocks the settings.
REG_UNLOCK = 0x0000
# Holding registers 0x0000..0x0006 contain the serial number (ASCII).
REG_SERIAL = 0x0000
SERIAL_LENGTH = 7
# Input register with the current lock state.
REG_LOCK_STATE = 0x0054

LOCK_STATES = {
    0: "locked",
    1: "unlocked",
    2: "unlocked_advanced",
}

KIND_NUMBER = "number"
KIND_SELECT = "select"


@dataclass(frozen=True)
class InstallerSetting:
    """Description of a single installer setting."""

    key: str
    name: str
    kind: str
    write_register: int
    read_register: int
    scale: float = 1
    min_value: float = 0
    max_value: float = 65535
    step: float = 1
    unit: str | None = None
    options: dict[int, str] = field(default_factory=dict)
    icon: str | None = None

    def raw_to_native(self, raw: int) -> float | str | None:
        if self.kind == KIND_SELECT:
            return self.options.get(raw)
        value = raw * self.scale
        return int(value) if float(value).is_integer() else round(value, 3)

    def native_to_raw(self, value) -> int:
        """Convert a user value (number, option label or raw int) to raw."""
        if self.kind == KIND_SELECT:
            if isinstance(value, str):
                reverse = {label.lower(): raw for raw, label in self.options.items()}
                if value.strip().lower() in reverse:
                    return reverse[value.strip().lower()]
                if value.strip().isdigit():
                    value = int(value.strip())
                else:
                    raise ValueError(
                        f"Invalid option '{value}' for {self.name}. "
                        f"Allowed: {', '.join(self.options.values())}"
                    )
            raw = int(value)
            if raw not in self.options:
                raise ValueError(f"Invalid option {raw} for {self.name}")
            return raw

        number = float(value)
        if not self.min_value <= number <= self.max_value:
            raise ValueError(
                f"{self.name}: {number} outside {self.min_value}..{self.max_value}"
            )
        raw = int(round(number / self.scale))
        if not 0 <= raw <= 0xFFFF:
            raise ValueError(f"{self.name}: value out of register range")
        return raw


SHADOW_FIX = {0: "Off", 1: "Low", 2: "Middle", 3: "High"}
METER_DIRECTION = {0: "Positive", 1: "Negative"}

SETTINGS: tuple[InstallerSetting, ...] = (
    InstallerSetting(
        key="export_control_user_limit",
        name="Feed-in Limit",
        kind=KIND_NUMBER,
        write_register=0x42,
        read_register=0xB6,
        scale=10,
        min_value=0,
        max_value=30000,
        step=10,
        unit="W",
        icon="mdi:transmission-tower-export",
    ),
    InstallerSetting(
        key="main_breaker_current_limit",
        name="Main Breaker Current Limit",
        kind=KIND_NUMBER,
        write_register=0x71,
        read_register=0xD7,
        min_value=10,
        max_value=250,
        unit="A",
        icon="mdi:fuse",
    ),
    InstallerSetting(
        key="battery_charge_max_current",
        name="Battery Charge Max Current",
        kind=KIND_NUMBER,
        write_register=0x24,
        read_register=0x90,
        scale=0.1,
        min_value=0,
        max_value=30,
        step=0.1,
        unit="A",
        icon="mdi:battery-charging",
    ),
    InstallerSetting(
        key="battery_discharge_max_current",
        name="Battery Discharge Max Current",
        kind=KIND_NUMBER,
        write_register=0x25,
        read_register=0x91,
        scale=0.1,
        min_value=0,
        max_value=30,
        step=0.1,
        unit="A",
        icon="mdi:battery-arrow-down",
    ),
    InstallerSetting(
        key="eps_min_soc",
        name="EPS Min SoC",
        kind=KIND_NUMBER,
        write_register=0x44,
        read_register=0xB8,
        min_value=10,
        max_value=25,
        unit="%",
        icon="mdi:battery-lock",
    ),
    InstallerSetting(
        key="meter_1_direction",
        name="Meter 1 Direction",
        kind=KIND_SELECT,
        write_register=0xA4,
        read_register=0x10B,
        options=METER_DIRECTION,
        icon="mdi:swap-horizontal",
    ),
    InstallerSetting(
        key="meter_2_direction",
        name="Meter 2 Direction",
        kind=KIND_SELECT,
        write_register=0xA5,
        read_register=0x10C,
        options=METER_DIRECTION,
        icon="mdi:swap-horizontal",
    ),
    InstallerSetting(
        key="pgrid_bias",
        name="Grid Bias Direction",
        kind=KIND_SELECT,
        write_register=0x8D,
        read_register=0xB2,
        options={0: "Disabled", 1: "Grid", 2: "Inverter"},
        icon="mdi:scale-balance",
    ),
    InstallerSetting(
        key="shadow_fix_pv1",
        name="Shadow Fix Level PV1 (GMPPT)",
        kind=KIND_SELECT,
        write_register=0x9C,
        read_register=0x104,
        options=SHADOW_FIX,
        icon="mdi:solar-panel",
    ),
    InstallerSetting(
        key="shadow_fix_pv2",
        name="Shadow Fix Level PV2 (GMPPT)",
        kind=KIND_SELECT,
        write_register=0x98,
        read_register=0x114,
        options=SHADOW_FIX,
        icon="mdi:solar-panel",
    ),
    InstallerSetting(
        key="shadow_fix_pv3",
        name="Shadow Fix Level PV3 (GMPPT)",
        kind=KIND_SELECT,
        write_register=0xFC,
        read_register=0x15F,
        options=SHADOW_FIX,
        icon="mdi:solar-panel",
    ),
)

SETTINGS_BY_KEY = {s.key: s for s in SETTINGS}


def find_setting(name_or_key: str) -> InstallerSetting:
    """Look up a setting by key or (case-insensitive) friendly name."""
    if name_or_key in SETTINGS_BY_KEY:
        return SETTINGS_BY_KEY[name_or_key]
    lowered = name_or_key.strip().lower()
    for setting in SETTINGS:
        if setting.name.lower() == lowered:
            return setting
    raise KeyError(f"Unknown installer setting: {name_or_key}")


def option_key(label: str) -> str:
    """Translation-friendly key for an option label ("Middle" -> "middle")."""
    return label.lower().replace(" ", "_")
