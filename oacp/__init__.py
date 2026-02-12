"""
OACP - Open Agent Compute Protocol
====================================

A protocol for autonomous agent attestation, verification, and secure compute.

Modules:
    core: Core protocol implementations
    protocol: Protocol specifications and validators
    runtime: Runtime attestation and verification
    attestation: Attestation evidence and verification

Example:
    >>> import oacp
    >>> print(oacp.__version__)
    '0.1.0'

Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "OACP Team"
__license__ = "MIT"

# Import key components with graceful fallback
try:
    from oacp.core import AgentIdentity, Attestation
    __all__ = ["__version__", "__author__", "__license__", "AgentIdentity", "Attestation"]
except ImportError:
    # Modules not yet implemented - define __all__ without them
    __all__ = ["__version__", "__author__", "__license__"]
