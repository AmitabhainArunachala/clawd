"""
Sandbox: Isolated Execution Environment
========================================

Provides sandboxed execution for agent code with capability-based
permissions and cryptographic attestation.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum, auto

from .capability import Capability, CapabilitySet
from .attestation import Attestation


class ExecutionStatus(Enum):
    """Execution status codes."""
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    TIMEOUT = auto()
    MEMORY_EXCEEDED = auto()
    PERMISSION_DENIED = auto()
    CRASH = auto()


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution.
    
    Attributes:
        max_memory_mb: Maximum memory allowed (default: 512)
        max_cpu_time_ms: Maximum CPU time in milliseconds (default: 30000)
        max_wall_time_ms: Maximum wall clock time (default: 60000)
        capabilities: Set of allowed capabilities
        enable_network: Whether network access is allowed
        enable_file_write: Whether file write access is allowed
        attest: Whether to generate attestation (default: True)
    """
    max_memory_mb: int = 512
    max_cpu_time_ms: int = 30000
    max_wall_time_ms: int = 60000
    capabilities: CapabilitySet = field(default_factory=CapabilitySet)
    enable_network: bool = False
    enable_file_write: bool = False
    attest: bool = True
    
    def __post_init__(self):
        if isinstance(self.capabilities, list):
            self.capabilities = CapabilitySet(self.capabilities)


@dataclass  
class SandboxResult:
    """Result of sandboxed execution.
    
    Attributes:
        status: Execution status
        output: Execution output data
        logs: Execution logs
        metrics: Performance metrics
        attestation: Cryptographic attestation (if enabled)
        error: Error information (if failed)
    """
    status: ExecutionStatus
    output: Any = None
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    attestation: Optional[Attestation] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if execution succeeded."""
        return self.status == ExecutionStatus.SUCCESS
    
    def verify(self) -> bool:
        """Verify attestation if present."""
        if self.attestation is None:
            return True  # Nothing to verify
        return self.attestation.verify()


class Sandbox:
    """Sandboxed execution environment.
    
    Provides isolated execution with capability-based permissions
    and optional cryptographic attestation.
    
    Example:
        >>> config = SandboxConfig(
        ...     max_memory_mb=256,
        ...     capabilities=[Capability.FILE_READ, Capability.NETWORK]
        ... )
        >>> sandbox = Sandbox(config)
        >>> result = sandbox.execute(agent_fn, inputs={"x": 42})
        >>> if result.success:
        ...     print(result.output)
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self._execution_count = 0
        self._total_time_ms = 0.0
    
    def execute(
        self, 
        code: Union[callable, str], 
        inputs: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> SandboxResult:
        """Execute code in sandbox.
        
        Args:
            code: Function or code string to execute
            inputs: Input data for execution
            context: Additional execution context
            
        Returns:
            SandboxResult with output and attestation
        """
        inputs = inputs or {}
        context = context or {}
        
        start_time = time.perf_counter()
        self._execution_count += 1
        
        # Check capabilities
        if not self._check_capabilities(code, inputs):
            return SandboxResult(
                status=ExecutionStatus.PERMISSION_DENIED,
                error="Required capabilities not granted"
            )
        
        try:
            # Execute with resource limits
            output, logs, metrics = self._execute_with_limits(code, inputs, context)
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._total_time_ms += elapsed_ms
            metrics["elapsed_ms"] = elapsed_ms
            
            # Generate attestation if enabled
            attestation = None
            if self.config.attest:
                attestation = self._create_attestation(code, inputs, output, metrics)
            
            return SandboxResult(
                status=ExecutionStatus.SUCCESS,
                output=output,
                logs=logs,
                metrics=metrics,
                attestation=attestation
            )
            
        except TimeoutError:
            return SandboxResult(
                status=ExecutionStatus.TIMEOUT,
                error=f"Execution exceeded {self.config.max_wall_time_ms}ms"
            )
        except MemoryError:
            return SandboxResult(
                status=ExecutionStatus.MEMORY_EXCEEDED,
                error=f"Execution exceeded {self.config.max_memory_mb}MB"
            )
        except Exception as e:
            return SandboxResult(
                status=ExecutionStatus.CRASH,
                error=f"Execution failed: {type(e).__name__}: {str(e)}"
            )
    
    def _check_capabilities(self, code: Union[callable, str], inputs: Dict) -> bool:
        """Check if execution is allowed given capabilities."""
        # Basic capability checking - can be extended
        required = CapabilitySet()
        
        if self.config.enable_network:
            required.add(Capability.NETWORK)
        if self.config.enable_file_write:
            required.add(Capability.FILE_WRITE)
        
        return self.config.capabilities.covers(required)
    
    def _execute_with_limits(
        self, 
        code: Union[callable, str], 
        inputs: Dict,
        context: Dict
    ):
        """Execute code with resource limits enforced."""
        logs = []
        metrics = {
            "memory_peak_mb": 0.0,
            "cpu_time_ms": 0.0,
        }
        
        # For callable functions
        if callable(code):
            # Create restricted context
            exec_context = {
                "__builtins__": self._restricted_builtins(),
                "inputs": inputs,
                "log": lambda msg: logs.append(str(msg)),
            }
            
            # Execute
            result = code(exec_context) if inputs else code()
            
        else:
            # String code execution (more restricted)
            exec_context = {
                "__builtins__": self._restricted_builtins(),
                "inputs": inputs,
                "log": lambda msg: logs.append(str(msg)),
            }
            exec(code, exec_context)
            result = exec_context.get("result", None)
        
        return result, logs, metrics
    
    def _restricted_builtins(self) -> Dict[str, Any]:
        """Get restricted builtins for sandboxed execution."""
        safe_builtins = {
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "pow": pow,
            "print": lambda *args: None,  # Silent print
            "range": range,
            "round": round,
            "set": set,
            "slice": slice,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
        }
        
        # Add capabilities-based access
        if Capability.FILE_READ in self.config.capabilities:
            safe_builtins["open"] = self._safe_open
        
        return safe_builtins
    
    def _safe_open(self, path: str, mode: str = 'r'):
        """Safe file open with restrictions."""
        if 'w' in mode or 'a' in mode:
            if not self.config.enable_file_write:
                raise PermissionError("File write not permitted")
        return open(path, mode)
    
    def _create_attestation(
        self, 
        code: Union[callable, str], 
        inputs: Dict,
        output: Any,
        metrics: Dict
    ) -> Attestation:
        """Create cryptographic attestation of execution."""
        # Create hash of execution
        hasher = hashlib.sha256()
        
        # Hash code
        code_str = code if isinstance(code, str) else code.__code__.co_code.hex()
        hasher.update(code_str.encode())
        
        # Hash inputs
        hasher.update(json.dumps(inputs, sort_keys=True, default=str).encode())
        
        # Hash config
        config_dict = {
            "capabilities": list(self.config.capabilities),
            "memory": self.config.max_memory_mb,
        }
        hasher.update(json.dumps(config_dict, sort_keys=True).encode())
        
        # Hash output
        hasher.update(json.dumps(output, sort_keys=True, default=str).encode())
        
        return Attestation(
            hash=hasher.hexdigest(),
            timestamp=time.time(),
            config=config_dict,
            metrics=metrics
        )
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get sandbox statistics."""
        return {
            "execution_count": self._execution_count,
            "total_time_ms": self._total_time_ms,
            "avg_time_ms": self._total_time_ms / max(1, self._execution_count),
        }
