"""
OACP Protocol Module
====================

Adapters for protocol integration:
- MCP Bridge: Run MCP servers in OACP sandboxes
- A2A Adapter: Add attestation to A2A agents
"""

from .mcp_bridge import OACPMCPServer
from .a2a_adapter import A2AAttestationAdapter

__all__ = ["OACPMCPServer", "A2AAttestationAdapter"]
