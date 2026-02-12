"""
OACP Test Suite
===============

This package contains all tests for the OACP project.

Structure:
    conftest.py         - pytest fixtures and configuration
    test_core.py        - Core functionality tests
    test_protocol.py    - Protocol specification tests
    test_attestation.py - Attestation verification tests

Run with:
    pytest tests/ -v

Or use the deployment guardian:
    python scripts/deploy_guardian.py
"""

__version__ = "0.1.0"

# Make test utilities available
__all__ = ["__version__"]
