#!/usr/bin/env python3
"""
Generate analysis reports from hyperbolic chamber simulation data.

This module provides functions to parse simulation output logs and produce
statistical summaries, plots, and visualizations of chamber behavior.
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict

from .config import OUTPUT_DIR

def load_simulation_log(log_path: str) -> pd.DataFrame:
    """
    Load and parse a simulation log file.

    Parameters
    ----------
    log_path : str
        Path to the log file (plain text).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: step, time, point_x, point_y, point_z
    """
    rows = []
    with open(log_path, 'r') as f:
        for line in f:
            if line.startswith('Step'):
                parts = line.split()
                step = int(parts[1].strip(':'))
                # Parse point values after 'point ='
                point_str = line.split('point =')[1].strip()
                # Expect format like '(x, y, z)'
                coords = [float(v) for v in point_str.strip('()').split(',')]
                point_x, point_y, point_z = coords[0], coords[1], coords[2]
                # Simple time based on step * TIME_STEP
                time = step * TIME_STEP
                rows.append([step, time, point_x, point_y, point_z])
    df = pd.DataFrame(rows, columns=['step', 'time', 'point_x', 'point_y', 'point_z'])
    return df

def plot_trajectory(df: pd.DataFrame, output_path: str = None):
    """
    Plot the trajectory of the simulated point in 3D space.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing simulation data.
    output_path : str, optional
        Path to save the figure. If None, shows the plot.
    """
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(df['point_x'], df['point_y'], df['point_z'], '-o', label='Trajectory')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Hyperbolic Chamber Trajectory')
    ax.legend()
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def generate_summary_report(df: pd.DataFrame, report_path: str):
    """
    Generate a textual summary report of the simulation.

    Parameters
    ----------
    df : pd.DataFrame
        Simulation data.
    report_path : str
        Destination file path for the report.
    """
    summary = [
        "=== Hyperbolic Chamber Simulation Summary ===",
        f"Total steps: {len(df)}",
        f"Final point: ({df['point_x'].iloc[-1]:.4f}, {df['point_y'].iloc[-1]:.4f}, {df['point_z'].iloc[-1]:.4f})",
        f"Total simulated time: {df['time'].iloc[-1]:.4f} seconds",
        f"Average speed: {df['point_x'].abs().mean():.4f} units/step"
    ]
    with open(report_path, 'w') as f:
        f.write('\n'.join(summary))
    print(f"Summary report saved to {report_path}")

if __name__ == "__main__":
    # Example usage when run directly
    # Find the most recent log file in OUTPUT_DIR
    log_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "*.log")))
    if not log_files:
        print("No log files found in output directory.")
        exit(1)
    latest_log = log_files[-1]
    df = load_simulation_log(latest_log)
    generate_summary_report(df, os.path.join(OUTPUT_DIR, "summary_report.txt"))
    plot_trajectory(df, os.path.join(OUTPUT_DIR, "trajectory.png"))