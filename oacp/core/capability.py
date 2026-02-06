"""
Capability: Permission Tokens for Sandboxed Execution
======================================================

Implements capability-based security for OACP.
Capabilities are unforgeable tokens representing permissions.
"""

from enum import Enum, auto
from typing import Set, Optional, Iterable, Union


class Capability(Enum):
    """Available capabilities for sandboxed execution.
    
    Capabilities are granted to sandboxes and checked at execution time.
    """
    # File operations
    FILE_READ = auto()      # Read files from allowed paths
    FILE_WRITE = auto()     # Write files to allowed paths
    
    # Network operations
    NETWORK = auto()        # Make network requests
    NETWORK_OUTBOUND = auto()  # Outbound connections only
    
    # Compute operations
    GPU = auto()           # Access GPU for computation
    SUBPROCESS = auto()    # Spawn subprocesses
    
    # AI/ML operations
    MODEL_LOAD = auto()    # Load ML models
    MODEL_INFERENCE = auto()  # Run model inference
    
    # System operations
    ENV_READ = auto()      # Read environment variables
    ENV_WRITE = auto()     # Write environment variables
    
    # Communication
    IPC = auto()          # Inter-process communication
    
    def __repr__(self) -> str:
        return f"Capability.{self.name}"
    
    def __str__(self) -> str:
        return self.name.lower().replace("_", ".")


class CapabilitySet:
    """A set of capabilities with convenient operations.
    
    Example:
        >>> caps = CapabilitySet([Capability.FILE_READ, Capability.NETWORK])
        >>> caps.add(Capability.GPU)
        >>> Capability.FILE_READ in caps
        True
        >>> caps.covers(CapabilitySet([Capability.FILE_READ]))
        True
    """
    
    def __init__(self, capabilities: Optional[Iterable[Capability]] = None):
        self._caps: Set[Capability] = set(capabilities) if capabilities else set()
    
    def add(self, capability: Capability) -> "CapabilitySet":
        """Add a capability. Returns self for chaining."""
        self._caps.add(capability)
        return self
    
    def remove(self, capability: Capability) -> "CapabilitySet":
        """Remove a capability. Returns self for chaining."""
        self._caps.discard(capability)
        return self
    
    def __contains__(self, capability: Capability) -> bool:
        """Check if capability is in set."""
        return capability in self._caps
    
    def __iter__(self):
        """Iterate over capabilities."""
        return iter(self._caps)
    
    def __len__(self) -> int:
        """Number of capabilities."""
        return len(self._caps)
    
    def __eq__(self, other) -> bool:
        """Check equality with another set."""
        if isinstance(other, CapabilitySet):
            return self._caps == other._caps
        return False
    
    def __repr__(self) -> str:
        caps = sorted([c.name for c in self._caps])
        return f"CapabilitySet({caps})"
    
    def covers(self, other: "CapabilitySet") -> bool:
        """Check if this set covers all capabilities in other.
        
        Returns True if other requires no capabilities not in self.
        """
        return other._caps.issubset(self._caps)
    
    def union(self, other: "CapabilitySet") -> "CapabilitySet":
        """Return union of two capability sets."""
        return CapabilitySet(self._caps | other._caps)
    
    def intersection(self, other: "CapabilitySet") -> "CapabilitySet":
        """Return intersection of two capability sets."""
        return CapabilitySet(self._caps & other._caps)
    
    def difference(self, other: "CapabilitySet") -> "CapabilitySet":
        """Return capabilities in self but not in other."""
        return CapabilitySet(self._caps - other._caps)
    
    def to_list(self) -> List[str]:
        """Convert to list of string names."""
        return sorted([str(c) for c in self._caps])
    
    @classmethod
    def from_list(cls, names: List[str]) -> "CapabilitySet":
        """Create from list of capability names."""
        caps = []
        for name in names:
            # Normalize name
            name = name.upper().replace(".", "_")
            if hasattr(Capability, name):
                caps.append(Capability[name])
        return cls(caps)
    
    @classmethod
    def all(cls) -> "CapabilitySet":
        """Create set with all capabilities."""
        return cls(Capability)
    
    @classmethod
    def none(cls) -> "CapabilitySet":
        """Create empty capability set."""
        return cls()
    
    @classmethod
    def minimal(cls) -> "CapabilitySet":
        """Create set with minimal safe capabilities."""
        return cls([Capability.FILE_READ])
