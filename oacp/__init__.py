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
    >>> from oacp.core import AgentIdentity
    >>> identity = AgentIdentity.create("agent-001")

Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "OACP Team"
__license__ = "MIT"

# Import key components for convenient access
# These will be uncommented as modules are implemented:

# from oacp.core import AgentIdentity, Attestation
# from oacp.protocol import ProtocolVersion, Message
# from oacp.runtime import RuntimeEnvironment

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    # "AgentIdentity",
    # "Attestation", 
    # "ProtocolVersion",
    # "Message",
    # "RuntimeEnvironment",
]
