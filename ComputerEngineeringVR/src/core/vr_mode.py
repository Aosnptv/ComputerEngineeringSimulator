"""Dependency-free optional VR startup boundary.

This module deliberately does not initialize OpenXR.  It keeps desktop startup
independent from third-party VR packages while exposing a guarded adapter seam
for a future, hardware-validated backend.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class VRReadiness:
    requested: bool
    desktop_fallback: bool
    runtime_manifest: str | None
    runtime_name: str | None
    integration_module_available: bool
    classification: str
    detail: str


class VRAdapter(Protocol):
    """Interface a verified OpenXR implementation must satisfy."""

    active: bool

    def start(self, app) -> None: ...

    def stop(self) -> None: ...


class DesktopFallbackAdapter:
    """No-op adapter used when VR was not requested or cannot start safely."""

    active = False

    def __init__(self, readiness: VRReadiness):
        self.readiness = readiness

    def start(self, app) -> None:
        return None

    def stop(self) -> None:
        return None


def _active_runtime_manifest() -> str | None:
    if sys.platform != "win32":
        return None
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Khronos\OpenXR\1"
        ) as key:
            value, _ = winreg.QueryValueEx(key, "ActiveRuntime")
            return str(value) if value else None
    except (FileNotFoundError, OSError):
        return None


def _runtime_name(manifest: str | None) -> str | None:
    if not manifest or not Path(manifest).is_file():
        return None
    try:
        data = json.loads(Path(manifest).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    name = data.get("runtime", {}).get("name")
    return str(name) if name else None


def inspect_vr_readiness(requested: bool) -> VRReadiness:
    manifest = _active_runtime_manifest()
    runtime_name = _runtime_name(manifest)
    module_available = importlib.util.find_spec("p3dopenxr") is not None

    if not requested:
        classification = "NOT VERIFIED"
        detail = "Desktop mode selected; no VR initialization was attempted."
    elif not manifest or not Path(manifest).is_file():
        classification = "NOT AVAILABLE"
        detail = "No usable Windows OpenXR active-runtime manifest was found."
    elif not module_available:
        classification = "INSTALLED BUT NOT TESTED"
        detail = (
            f"{runtime_name or 'OpenXR runtime'} is installed, but the guarded "
            "Panda3D integration package is not installed; continuing in desktop mode."
        )
    else:
        classification = "INSTALLED BUT NOT TESTED"
        detail = (
            "Runtime and integration module are present, but this dependency-free "
            "boundary will not initialize an unverified backend or claim HMD support."
        )

    return VRReadiness(
        requested=requested,
        desktop_fallback=True,
        runtime_manifest=manifest,
        runtime_name=runtime_name,
        integration_module_available=module_available,
        classification=classification,
        detail=detail,
    )


def create_optional_vr_adapter(requested: bool) -> DesktopFallbackAdapter:
    """Return a safe adapter without importing optional VR dependencies."""
    return DesktopFallbackAdapter(inspect_vr_readiness(requested))

