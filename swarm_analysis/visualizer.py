#!/usr/bin/env python3
"""
Visualization utilities for hyperbolic chamber simulation results.

Provides high-level plotting wrappers around matplotlib to display
geometric properties, curvature effects, and time evolution.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np
from typing import Tuple

def plot_sphere_section(ax: plt.Axes, center: Tuple[float, float, float],
                        radius: float, color: str = "skyblue", alpha: float = 0.3):
    """
    Plot a spherical surface segment on a 3D axis.
    This is useful for visualizing the boundary of a hyperbolic chamber.
    """
    # Generate spherical coordinates
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color=color, alpha=alpha, linewidth=0)

def plot_geodesic(ax: plt.Axes, start: Tuple[float, float, float],
                  end: Tuple[float, float, float], color: str = "red", linewidth: float = 2):
    """
    Plot a geodesic segment between two points in the simulated space.
    """
    xs, ys, zs = [start[i], end[i]] for i in range(3)
    ax.plot([xs[0], xs[1]], [ys[0], ys[1]], [zs[0], zs[1]], color=color, linewidth=linewidth)

def configure_3d_ax(ax: plt.Axes, title: str = "3D View"):
    """
    Apply standard configuration to a 3D matplotlib axis.
    """
    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.grid(False)
    ax.set_box_aspect([1,1,1])  # equal aspect ratio