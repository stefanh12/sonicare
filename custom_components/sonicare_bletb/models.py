"""The Sonicare ble toothbrush integration models."""

from __future__ import annotations

from dataclasses import dataclass

from .coordinator import SonicareBLETBCoordinator
from .device import SonicareBLETB


@dataclass
class SonicareBLETBData:
    """Data for the Sonicare ble toothbrush integration."""

    title: str
    device: SonicareBLETB
    coordinator: SonicareBLETBCoordinator
