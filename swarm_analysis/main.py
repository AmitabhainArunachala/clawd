#!/usr/bin/env python3
"""
Entry point for the Hyperbolic Chamber Analysis application.
"""
import sys
import logging
from .config import LOG_LEVEL
from .simulation import run_simulation, HyperbolicChamber

# Setup logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Hyperbolic Chamber simulation...")
    chamber = HyperbolicChamber(radius=HYPERBOLIC_RADIUS, curvature=CURVATURE_K)
    run_simulation(chamber, steps=100)
    logger.info("Simulation completed.")

if __name__ == "__main__":
    main()