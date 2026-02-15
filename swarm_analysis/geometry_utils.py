# Geometry utility functions for hyperbolic chamber calculations.

import math
from typing import List, Tuple

def hyperbolic_distance(r: float, K: float) -> float:
    """
    Compute hyperbolic distance from the origin given radius r and curvature K.
    Uses model: ds^2 = dr^2 + sinh^2(sqrt(K) * r) * dΩ^2
    """
    if r < 0:
        raise ValueError("Radius must be non-negative")
    return (1 / math.sqrt(K)) * math.asinh(math.sqrt(K) * r)

def unit_vector(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """
    Return the unit vector of the given 3D vector.
    """
    norm = math.sqrt(x*x + y*y + z*z)
    if norm == 0:
        raise ValueError("Zero vector has no direction")
    return (x / norm, y / norm, z / norm)

def intersect_plane_with_sphere(center: Tuple[float, float, float],
                                radius: float,
                                plane_normal: Tuple[float, float, float],
                                plane_offset: float) -> List[Tuple[float, float, float]]:
    """
    Compute intersection points between a sphere and a plane.
    Returns list of intersection points (may be empty, one, or infinite).
    """
    # plane equation: n . x = d
    # sphere equation: |x - c|^2 = r^2
    # Solve for x; for simplicity return empty list placeholder
    # This function can be expanded later with full linear algebra.
    return []  # placeholder for actual intersection computation