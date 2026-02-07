#!/usr/bin/env python3
"""
Agent Capabilities - WARP_REGENT Evolved Functions
==================================================

Integration of WARP_REGENT's 6 evolved capabilities:
1. track_performance - timing decorator
2. with_retry - automatic retry logic  
3. health_check - system health validation
4. diagnose - error diagnostics
5. perf_metrics - performance tracking
6. circuit_breaker - failure protection

Integrated into Unified Agent Core.
Iteration 2 of collaborative build.
"""

import time
import functools
import logging
from typing import Callable, Any, Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class PerformanceMetrics:
    """Track performance of function calls"""
    function_name: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    errors: int = 0
    last_called: Optional[datetime] = None
    
    @property
    def avg_time(self) -> float:
        if self.call_count == 0:
            return 0.0
        return self.total_time / self.call_count
        
    def record_call(self, duration: float, error: bool = False):
        """Record a function call"""
        self.call_count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.last_called = datetime.now()
        if error:
            self.errors += 1


class CapabilityRegistry:
    """Registry for agent capabilities with metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
        
    def get_metrics(self, function_name: str) -> PerformanceMetrics:
        """Get or create metrics for a function"""
        if function_name not in self.metrics:
            self.metrics[function_name] = PerformanceMetrics(function_name)
        return self.metrics[function_name]
        
    def get_circuit_breaker(self, name: str, failure_threshold: int = 5,
                           recovery_timeout: float = 30.0) -> 'CircuitBreaker':
        """Get or create circuit breaker"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                name, failure_threshold, recovery_timeout
            )
        return self.circuit_breakers[name]


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.
    
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing fast, requests rejected immediately
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, name: str, failure_threshold: int = 5,
                 recovery_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit {self.name} entering HALF_OPEN state")
                    return True
            return False
            
        if self.state == CircuitState.HALF_OPEN:
            return True
            
        return True
        
    def record_success(self):
        """Record successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info(f"Circuit {self.name} CLOSED (recovered)")
        else:
            self.failure_count = 0
            
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit {self.name} OPENED after {self.failure_count} failures")
                
    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply circuit breaker"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.can_execute():
                raise CircuitBreakerOpen(f"Circuit {self.name} is OPEN")
                
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise
                
        return wrapper


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open"""
    pass


# Global registry
_registry = CapabilityRegistry()


def track_performance(func: Callable) -> Callable:
    """
    Decorator to track function performance metrics.
    
    Records:
    - Call count
    - Total execution time
    - Min/max/average time
    - Error count
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        metrics = _registry.get_metrics(func.__name__)
        start_time = time.time()
        error = False
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error = True
            raise
        finally:
            duration = time.time() - start_time
            metrics.record_call(duration, error)
            logger.debug(f"{func.__name__}: {duration:.3f}s")
            
    return wrapper


def with_retry(max_attempts: int = 3, delay: float = 1.0,
               backoff: float = 2.0, exceptions: tuple = (Exception,)) -> Callable:
    """
    Decorator to add automatic retry logic.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(f"{func.__name__} attempt {attempt} failed: {e}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
                        
            raise last_exception
            
        return wrapper
    return decorator


def health_check(check_func: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Perform health check on system components.
    
    Returns dict with:
    - status: 'healthy', 'degraded', or 'unhealthy'
    - checks: list of individual check results
    - timestamp: when check was performed
    """
    results = {
        'status': 'healthy',
        'checks': [],
        'timestamp': datetime.now().isoformat()
    }
    
    # Check circuit breakers
    for name, cb in _registry.circuit_breakers.items():
        check = {
            'component': f'circuit_breaker:{name}',
            'status': 'healthy' if cb.state == CircuitState.CLOSED else 'degraded',
            'state': cb.state.value,
            'failure_count': cb.failure_count
        }
        results['checks'].append(check)
        if cb.state != CircuitState.CLOSED:
            results['status'] = 'degraded'
            
    # Check metrics for errors
    for name, metrics in _registry.metrics.items():
        if metrics.call_count > 0:
            error_rate = metrics.errors / metrics.call_count
            check = {
                'component': f'function:{name}',
                'status': 'healthy' if error_rate < 0.1 else 'degraded',
                'call_count': metrics.call_count,
                'error_rate': error_rate,
                'avg_time': metrics.avg_time
            }
            results['checks'].append(check)
            if error_rate >= 0.1:
                results['status'] = 'degraded'
                
    # Run custom check if provided
    if check_func:
        try:
            custom_result = check_func()
            results['checks'].append({
                'component': 'custom',
                'status': 'healthy',
                'result': custom_result
            })
        except Exception as e:
            results['checks'].append({
                'component': 'custom',
                'status': 'unhealthy',
                'error': str(e)
            })
            results['status'] = 'unhealthy'
            
    return results


def diagnose(error: Exception, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Perform diagnostic analysis on an error.
    
    Returns dict with:
    - error_type: type of exception
    - error_message: error message
    - suggestions: list of potential fixes
    - context: any additional context provided
    """
    diagnosis = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': datetime.now().isoformat(),
        'suggestions': [],
        'context': context or {}
    }
    
    # Type-specific suggestions
    if isinstance(error, CircuitBreakerOpen):
        diagnosis['suggestions'].append("Circuit breaker is open - service may be down or experiencing high error rate")
        diagnosis['suggestions'].append("Wait for recovery timeout or manually reset circuit breaker")
        diagnosis['severity'] = 'high'
        
    elif isinstance(error, ConnectionError):
        diagnosis['suggestions'].append("Check network connectivity")
        diagnosis['suggestions'].append("Verify service endpoint is accessible")
        diagnosis['severity'] = 'high'
        
    elif isinstance(error, TimeoutError):
        diagnosis['suggestions'].append("Consider increasing timeout values")
        diagnosis['suggestions'].append("Check if service is overloaded")
        diagnosis['severity'] = 'medium'
        
    elif isinstance(error, ValueError):
        diagnosis['suggestions'].append("Verify input parameters are correct")
        diagnosis['suggestions'].append("Check data format and types")
        diagnosis['severity'] = 'low'
        
    else:
        diagnosis['suggestions'].append("Check logs for more details")
        diagnosis['suggestions'].append("Consider adding more specific error handling")
        diagnosis['severity'] = 'medium'
        
    return diagnosis


def get_perf_metrics() -> Dict[str, Dict]:
    """
    Get performance metrics for all tracked functions.
    
    Returns dict mapping function names to their metrics.
    """
    return {
        name: {
            'call_count': m.call_count,
            'avg_time': m.avg_time,
            'min_time': m.min_time if m.min_time != float('inf') else 0,
            'max_time': m.max_time,
            'total_time': m.total_time,
            'errors': m.errors,
            'error_rate': m.errors / m.call_count if m.call_count > 0 else 0,
            'last_called': m.last_called.isoformat() if m.last_called else None
        }
        for name, m in _registry.metrics.items()
    }


def get_circuit_breaker(name: str, failure_threshold: int = 5,
                        recovery_timeout: float = 30.0) -> CircuitBreaker:
    """Get or create a circuit breaker"""
    return _registry.get_circuit_breaker(name, failure_threshold, recovery_timeout)


# Convenience decorators
with_circuit_breaker = get_circuit_breaker


# Example usage and demo
def demo():
    """Demonstrate the capabilities"""
    print("=" * 60)
    print("🔧 AGENT CAPABILITIES - WARP_REGENT Integration Demo")
    print("=" * 60)
    
    # 1. track_performance
    @track_performance
    def slow_function():
        time.sleep(0.1)
        return "done"
        
    print("\n1. track_performance demo:")
    for _ in range(3):
        slow_function()
    
    metrics = get_perf_metrics()
    print(f"   slow_function calls: {metrics['slow_function']['call_count']}")
    print(f"   avg time: {metrics['slow_function']['avg_time']:.3f}s")
    
    # 2. with_retry
    attempt_count = 0
    
    @with_retry(max_attempts=3, delay=0.1)
    def flaky_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("Simulated failure")
        return "success after retries"
        
    print("\n2. with_retry demo:")
    result = flaky_function()
    print(f"   Result: {result}")
    print(f"   Attempts: {attempt_count}")
    
    # 3. health_check
    print("\n3. health_check demo:")
    health = health_check()
    print(f"   Status: {health['status']}")
    print(f"   Checks: {len(health['checks'])}")
    
    # 4. diagnose
    print("\n4. diagnose demo:")
    try:
        raise ValueError("Invalid input format")
    except Exception as e:
        diagnosis = diagnose(e, {'input': 'test_data'})
        print(f"   Error type: {diagnosis['error_type']}")
        print(f"   Suggestions: {len(diagnosis['suggestions'])}")
        for s in diagnosis['suggestions']:
            print(f"      - {s}")
    
    # 5. circuit_breaker
    print("\n5. circuit_breaker demo:")
    cb = get_circuit_breaker("test_service", failure_threshold=2)
    
    @cb
    def failing_function():
        raise ConnectionError("Service down")
        
    for i in range(3):
        try:
            failing_function()
        except Exception as e:
            print(f"   Call {i+1}: {type(e).__name__}")
            
    print(f"   Circuit state: {cb.state.value}")
    print(f"   Failure count: {cb.failure_count}")
    
    print("\n✅ All capabilities demonstrated")
    print("   Ready for integration into UnifiedAgent")


if __name__ == "__main__":
    demo()
