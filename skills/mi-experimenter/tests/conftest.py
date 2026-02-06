"""
conftest.py - pytest configuration
==================================

Adds the skills directory to Python path for testing.
"""

import sys
import os

# Add the parent directory (skills) to path so mi_experimenter can be imported
skills_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, skills_dir)

# Also add the rv_toolkit for R_V imports
rv_toolkit_dir = os.path.join(os.path.dirname(skills_dir), 'rv_toolkit')
if os.path.exists(rv_toolkit_dir):
    sys.path.insert(0, rv_toolkit_dir)
