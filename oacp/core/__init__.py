"""
OACP Core Module
================

Core primitives for sandboxed execution:
- Sandbox: Isolated execution environment
- Capability: Permission tokens
- Attestation: Cryptographic proof of execution
"""

from .sandbox import Sandbox, SandboxConfig, SandboxResult
from .capability import Capability, CapabilitySet
from .attestation import Attestation, AttestationVerifier

__all__ = [
    "Sandbox",
    "SandboxConfig",
    "SandboxResult", 
    "Capability",
    "CapabilitySet",
    "Attestation",
    "AttestationVerifier",
]
