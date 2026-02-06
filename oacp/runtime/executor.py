"""
Executor: High-Level Execution Interface
=========================================

Provides a simplified interface for executing agent code
with automatic sandbox management and result handling.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable, Union
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

from ..core.sandbox import Sandbox, SandboxConfig, SandboxResult, ExecutionStatus
from ..core.capability import Capability, CapabilitySet


@dataclass
class ExecutionContext:
    """Context passed to executed code.
    
    Provides safe access to inputs, logging, and limited
    system capabilities based on sandbox permissions.
    """
    inputs: Dict[str, Any]
    logs: List[str]
    capabilities: CapabilitySet
    
    def log(self, message: str) -> None:
        """Log a message."""
        self.logs.append(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get input value."""
        return self.inputs.get(key, default)
    
    def require(self, key: str) -> Any:
        """Get required input value, raises if missing."""
        if key not in self.inputs:
            raise KeyError(f"Required input '{key}' not provided")
        return self.inputs[key]
    
    def has_capability(self, cap: Capability) -> bool:
        """Check if capability is available."""
        return cap in self.capabilities


class Executor:
    """High-level executor for agent code.
    
    Manages sandbox lifecycle and provides convenient execution methods.
    
    Example:
        >>> executor = Executor(max_workers=4)
        >>> 
        >>> def agent_fn(ctx):
        ...     ctx.log("Starting processing")
        ...     return {"result": ctx.get("x", 0) * 2}
        >>>
        >>> result = executor.run(agent_fn, {"x": 21})
        >>> print(result.output)  # {"result": 42}
    """
    
    def __init__(
        self, 
        default_config: Optional[SandboxConfig] = None,
        max_workers: int = 4
    ):
        self.default_config = default_config or SandboxConfig()
        self._pool = ThreadPoolExecutor(max_workers=max_workers)
        self._sandboxes: List[Sandbox] = []
    
    def run(
        self,
        code: Union[Callable, str],
        inputs: Optional[Dict[str, Any]] = None,
        config: Optional[SandboxConfig] = None,
        timeout_ms: Optional[int] = None
    ) -> SandboxResult:
        """Execute code in sandbox.
        
        Args:
            code: Callable or code string to execute
            inputs: Input data
            config: Override default sandbox config
            timeout_ms: Override timeout
            
        Returns:
            SandboxResult with output or error
        """
        cfg = config or self.default_config
        if timeout_ms:
            cfg = SandboxConfig(
                max_wall_time_ms=timeout_ms,
                **{k: v for k, v in vars(cfg).items() if k != "max_wall_time_ms"}
            )
        
        sandbox = Sandbox(cfg)
        self._sandboxes.append(sandbox)
        
        return sandbox.execute(code, inputs)
    
    def run_async(
        self,
        code: Union[Callable, str],
        inputs: Optional[Dict[str, Any]] = None,
        config: Optional[SandboxConfig] = None
    ):
        """Submit execution to thread pool.
        
        Returns Future that resolves to SandboxResult.
        """
        return self._pool.submit(self.run, code, inputs, config)
    
    def run_batch(
        self,
        tasks: List[tuple],  # [(code, inputs), ...]
        config: Optional[SandboxConfig] = None
    ) -> List[SandboxResult]:
        """Execute multiple tasks in parallel.
        
        Args:
            tasks: List of (code, inputs) tuples
            config: Shared config for all tasks
            
        Returns:
            List of SandboxResults (same order as tasks)
        """
        futures = [
            self.run_async(code, inputs, config)
            for code, inputs in tasks
        ]
        return [f.result() for f in futures]
    
    def run_map(
        self,
        code: Callable,
        input_list: List[Dict[str, Any]],
        config: Optional[SandboxConfig] = None
    ) -> List[SandboxResult]:
        """Map a function over multiple inputs.
        
        Args:
            code: Function to execute
            input_list: List of input dicts
            config: Shared config
            
        Returns:
            List of results
        """
        tasks = [(code, inp) for inp in input_list]
        return self.run_batch(tasks, config)
    
    def close(self) -> None:
        """Clean up resources."""
        self._pool.shutdown(wait=True)
        self._sandboxes.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get aggregate statistics."""
        total_execs = sum(s.stats["execution_count"] for s in self._sandboxes)
        total_time = sum(s.stats["total_time_ms"] for s in self._sandboxes)
        return {
            "sandboxes_created": len(self._sandboxes),
            "total_executions": total_execs,
            "total_time_ms": total_time,
            "avg_time_ms": total_time / max(1, total_execs),
        }
