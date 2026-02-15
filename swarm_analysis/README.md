# Hyperbolic Chamber Analysis

This repository implements a simulation and analysis toolkit for hyperbolic chamber geometries.

## Overview
- **Goal**: Model and simulate hyperbolic spaces with configurable curvature and radius.
- **Features**: 
  - Geometric utility functions (distance, vector normalization, plane-sphere intersection)
  - Time-stepped dynamics simulation
  - logging and output generation
  - Unit test suite

## Directory Structure
```
/hyperbolic_chamber/
│
├── config.py          # Global constants and settings
├── geometry_utils.py  # Core geometry functions
├── simulation.py      # Simulation loop and chamber class
├── main.py            # Application entry point
├── tests/
│   └── test_hyperbolic_chamber.py  # Unit tests
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Simulation
```bash
python -m swarm_analysis.main
```

## Testing
```bash
python -m pytest tests/
```

## License
MIT License
