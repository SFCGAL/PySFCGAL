"""Material for surface simplification.

This module contains a definition of surface simplification strategies, defined as an
integer Enum.

"""

from __future__ import annotations

from enum import IntEnum
from typing import Type

__all__ = ["SimplificationStrategy"]


class SimplificationStrategy(IntEnum):
    """Edge collapsing strategies.

    The geometry simplification may be done following several strategies, which give
    the possible Enum values:

        - EDGE_LENGTH: the default one uses edge length as cost function and midpoint
          placement for vertex positioning. This strategy is compatible with exact
          kernels and provides good simplification results while maintaining geometric
          accuracy.

        - GARLAND_HECKBERT: the Garland-Heckbert strategy uses quadric error metrics
          for cost calculation and optimal vertex placement. This strategy requires
          Eigen support and uses inexact constructions for improved performance on
          large meshes.

        - LINDSTROM_TURK: the Lindstrom-Turk strategy uses cost and placement policies
          optimized for preserving volume and boundary features. This strategy requires
          Eigen support and uses inexact constructions for improved performance on
          complex meshes.

    Attributes
    ----------
    label : str
        Printed name of the simplification strategy.

    """
    label: str

    EDGE_LENGTH = 0, "EdgeLength"
    GARLAND_HECKBERT = 1, "GarlandHeckbert"
    LINDSTROM_TURK = 2, "LindstromTurk"

    def __new__(
        cls: Type["SimplificationStrategy"], value: int, label: str
    ) -> "SimplificationStrategy":
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self) -> str:
        return f"{self.label} ({self.value})"
