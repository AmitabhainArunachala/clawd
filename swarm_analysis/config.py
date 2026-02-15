# Configuration for Hyperbolic Chamber Analysis
# This file defines global constants and settings used across the project.

import os

# Physical constants
HYPERBOLIC_RADIUS = 5.0  # units
CURVATURE_K = 0.8        # Gaussian curvature parameter
TIME_STEP = 0.01         # simulation time step

# Simulation parameters
MAX_ITERATIONS = 10000
OUTPUT_DIR = "/Users/dhyana/clawd/swarm_analysis/output"
RESOLUTION = 0.001       # spatial resolution

# Output settings
PLOT_ENABLED = True
LOG_LEVEL = "INFO"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)