"""
Pytest configuration and fixtures for OACP tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chaiwala_workspace"))

# Environment setup for tests
os.environ.setdefault("OACP_TESTING", "1")
