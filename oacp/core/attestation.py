"""
Attestation: Cryptographic Proof of Execution
===============================================

Provides cryptographic attestation that code executed correctly
within a sandbox with specific configuration.
"""

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class Attestation:
    """Cryptographic attestation of sandboxed execution.
    
    Contains a hash of the execution (code, inputs, config, output)
    that can be verified by third parties.
    
    Attributes:
        hash: SHA256 hash of execution
        timestamp: Unix timestamp of execution
        config: Sandbox configuration used
        metrics: Performance metrics
        signature: Optional signature (for TEE integration)
    """
    hash: str
    timestamp: float
    config: Dict[str, Any]
    metrics: Dict[str, float]
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "hash": self.hash,
            "timestamp": self.timestamp,
            "config": self.config,
            "metrics": self.metrics,
            "signature": self.signature,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attestation":
        """Create from dictionary."""
        return cls(
            hash=data["hash"],
            timestamp=data["timestamp"],
            config=data["config"],
            metrics=data["metrics"],
            signature=data.get("signature"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Attestation":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def verify(self) -> bool:
        """Verify attestation integrity.
        
        Checks that the hash format is valid and timestamp
        is within reasonable bounds.
        
        Returns:
            True if attestation appears valid
        """
        # Check hash format (64 hex chars for SHA256)
        if not isinstance(self.hash, str) or len(self.hash) != 64:
            return False
        
        try:
            int(self.hash, 16)
        except ValueError:
            return False
        
        # Check timestamp is reasonable (not in future, not too old)
        now = time.time()
        if self.timestamp > now + 60:  # Allow 60s clock skew
            return False
        if self.timestamp < now - 86400 * 365:  # Not older than 1 year
            return False
        
        # Check signature if present
        if self.signature:
            return self._verify_signature()
        
        return True
    
    def _verify_signature(self) -> bool:
        """Verify signature if present."""
        # Placeholder for actual signature verification
        # Would integrate with TEE or key management
        return True
    
    @property
    def age_seconds(self) -> float:
        """Get age of attestation in seconds."""
        return time.time() - self.timestamp
    
    def __repr__(self) -> str:
        return f"Attestation(hash={self.hash[:16]}..., timestamp={self.timestamp})"


class AttestationVerifier:
    """Verifier for attestations from multiple sources.
    
    Can verify attestations from different OACP runtimes
    and optionally check against a registry of trusted sources.
    
    Example:
        >>> verifier = AttestationVerifier()
        >>> verifier.add_trusted_key("prod-cluster-1", public_key)
        >>> assert verifier.verify(attestation, source="prod-cluster-1")
    """
    
    def __init__(self):
        self._trusted_keys: Dict[str, str] = {}
        self._verified_count = 0
        self._failed_count = 0
    
    def add_trusted_key(self, source_id: str, public_key: str) -> None:
        """Add a trusted public key for a source.
        
        Args:
            source_id: Identifier for the source
            public_key: PEM-encoded public key or key ID
        """
        self._trusted_keys[source_id] = public_key
    
    def remove_trusted_key(self, source_id: str) -> None:
        """Remove a trusted source."""
        self._trusted_keys.pop(source_id, None)
    
    def verify(
        self, 
        attestation: Attestation, 
        source: Optional[str] = None,
        max_age_seconds: Optional[float] = None
    ) -> bool:
        """Verify an attestation.
        
        Args:
            attestation: Attestation to verify
            source: Optional source identifier for key lookup
            max_age_seconds: Maximum acceptable age
            
        Returns:
            True if attestation is valid
        """
        # Basic verification
        if not attestation.verify():
            self._failed_count += 1
            return False
        
        # Check age
        if max_age_seconds and attestation.age_seconds > max_age_seconds:
            self._failed_count += 1
            return False
        
        # Verify signature if source known
        if source and source in self._trusted_keys:
            if attestation.signature is None:
                self._failed_count += 1
                return False
            # Would do actual signature verification here
        
        self._verified_count += 1
        return True
    
    def batch_verify(
        self, 
        attestations: list, 
        source: Optional[str] = None
    ) -> Dict[str, bool]:
        """Verify multiple attestations.
        
        Returns dict mapping attestation hash to verification result.
        """
        results = {}
        for att in attestations:
            results[att.hash] = self.verify(att, source)
        return results
    
    @property
    def stats(self) -> Dict[str, int]:
        """Get verification statistics."""
        return {
            "verified": self._verified_count,
            "failed": self._failed_count,
            "trusted_sources": len(self._trusted_keys),
        }
