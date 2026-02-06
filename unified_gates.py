"""
Unified Gates - Integrated Security Gateway

A unified entry point that enforces security policies across all system entry points.
Combines injection detection, capability tokens, and audit logging into a cohesive
security layer.

Concept: Think of it as the castle gate - every request must pass through here.
"""

import functools
import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union
from contextlib import contextmanager
import threading

from dharmic_security import (
    SecurityLevel, ThreatType, SecurityEvent, AuditLogger,
    InjectionDetector, CapabilityToken, CapabilityManager,
    SecurityError, InjectionDetectedError, CapabilityError,
    audit_logger, scan_input, sanitize_input
)


T = TypeVar('T')


class GateAction(Enum):
    """Actions the gate can take on requests"""
    ALLOW = auto()
    BLOCK = auto()
    SANITIZE = auto()
    QUARANTINE = auto()
    LOG_ONLY = auto()


class RequestType(Enum):
    """Types of requests that pass through gates"""
    USER_INPUT = "user_input"
    SYSTEM_COMMAND = "system_command"
    FILE_ACCESS = "file_access"
    NETWORK_REQUEST = "network_request"
    CODE_EXECUTION = "code_execution"
    MESSAGE_SEND = "message_send"
    BROWSER_ACTION = "browser_action"
    API_CALL = "api_call"
    TOOL_INVOCATION = "tool_invocation"


@dataclass
class GateContext:
    """Context passed through the security gate"""
    request_type: RequestType
    source: str
    session_id: str
    user_id: Optional[str] = None
    capability_token: Optional[CapabilityToken] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    entry_time: float = field(default_factory=time.time)
    processing_history: List[str] = field(default_factory=list)
    
    def log_step(self, step: str):
        """Log a processing step"""
        self.processing_history.append(f"{time.time():.3f}:{step}")


@dataclass
class GateDecision:
    """Decision made by the security gate"""
    action: GateAction
    allowed: bool
    reason: str
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)
    sanitizations_applied: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'action': self.action.name,
            'allowed': self.allowed,
            'reason': self.reason,
            'confidence': self.confidence,
            'details': self.details
        }


class UnifiedGate:
    """
    The main security gateway that all requests must pass through.
    
    Combines multiple security layers:
    1. Input validation and sanitization
    2. Injection detection
    3. Capability verification
    4. Rate limiting
    5. Audit logging
    """
    
    def __init__(self):
        self.injection_detector = InjectionDetector()
        self.capability_manager = CapabilityManager()
        
        # Rate limiting
        self._rate_limits: Dict[str, List[float]] = {}
        self._rate_limit_lock = threading.Lock()
        
        # Quarantine for suspicious requests
        self._quarantine: List[Dict] = []
        self._quarantine_lock = threading.Lock()
        
        # Gate policies
        self._policies: Dict[RequestType, Dict] = {}
        self._setup_default_policies()
        
    def _setup_default_policies(self):
        """Setup default security policies for each request type"""
        self._policies = {
            RequestType.USER_INPUT: {
                'scan_injection': True,
                'sanitize': True,
                'required_level': SecurityLevel.PUBLIC,
                'rate_limit': 100,  # per minute
            },
            RequestType.SYSTEM_COMMAND: {
                'scan_injection': True,
                'sanitize': False,  # Don't sanitize - reject instead
                'required_capability': 'sys.exec',
                'required_level': SecurityLevel.TRUSTED,
                'rate_limit': 10,
            },
            RequestType.FILE_ACCESS: {
                'scan_injection': True,
                'sanitize': True,
                'required_capability': 'fs.read',
                'required_level': SecurityLevel.USER,
                'rate_limit': 100,
            },
            RequestType.NETWORK_REQUEST: {
                'scan_injection': True,
                'sanitize': True,
                'required_capability': 'net.http',
                'required_level': SecurityLevel.USER,
                'rate_limit': 50,
            },
            RequestType.CODE_EXECUTION: {
                'scan_injection': True,
                'sanitize': False,
                'required_capability': 'code.exec',
                'required_level': SecurityLevel.TRUSTED,
                'rate_limit': 5,
            },
            RequestType.MESSAGE_SEND: {
                'scan_injection': True,
                'sanitize': True,
                'required_capability': 'msg.send',
                'required_level': SecurityLevel.USER,
                'rate_limit': 30,
            },
            RequestType.BROWSER_ACTION: {
                'scan_injection': True,
                'sanitize': True,
                'required_capability': 'browser.control',
                'required_level': SecurityLevel.USER,
                'rate_limit': 60,
            },
            RequestType.TOOL_INVOCATION: {
                'scan_injection': True,
                'sanitize': True,
                'required_capability': None,  # Depends on tool
                'required_level': SecurityLevel.USER,
                'rate_limit': 100,
            },
        }
        
    def check_rate_limit(self, key: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Check if rate limit is exceeded.
        
        Returns:
            (allowed, remaining_requests)
        """
        now = time.time()
        
        with self._rate_limit_lock:
            if key not in self._rate_limits:
                self._rate_limits[key] = []
                
            # Clean old entries
            self._rate_limits[key] = [
                t for t in self._rate_limits[key]
                if now - t < window_seconds
            ]
            
            if len(self._rate_limits[key]) >= limit:
                return False, 0
                
            self._rate_limits[key].append(now)
            remaining = limit - len(self._rate_limits[key])
            
        return True, remaining
        
    def process(self, 
                request_type: RequestType,
                payload: Any,
                context: GateContext) -> GateDecision:
        """
        Process a request through the security gate.
        
        This is the main entry point for all secured operations.
        """
        context.log_step('gate_entry')
        policy = self._policies.get(request_type, {})
        
        # Step 1: Rate limiting
        rate_key = f"{context.source}:{context.session_id}:{request_type.value}"
        rate_limit = policy.get('rate_limit', 100)
        allowed, remaining = self.check_rate_limit(rate_key, rate_limit)
        
        if not allowed:
            audit_logger.log(SecurityEvent(
                timestamp=time.time(),
                event_type='rate_limit_exceeded',
                severity='warning',
                source=context.source,
                details={
                    'request_type': request_type.value,
                    'session_id': context.session_id
                },
                session_id=context.session_id,
                threat_type=ThreatType.RATE_LIMIT_VIOLATION
            ))
            return GateDecision(
                action=GateAction.BLOCK,
                allowed=False,
                reason=f"Rate limit exceeded ({rate_limit} requests per minute)",
                confidence=1.0,
                details={'rate_limit': rate_limit, 'remaining': 0}
            )
            
        context.log_step('rate_limit_passed')
        
        # Step 2: Capability check (if required)
        required_cap = policy.get('required_capability')
        if required_cap and context.capability_token:
            if not self.capability_manager.check_capability(
                context.capability_token, required_cap, context.metadata
            ):
                audit_logger.log(SecurityEvent(
                    timestamp=time.time(),
                    event_type='capability_denied',
                    severity='warning',
                    source=context.source,
                    details={
                        'required': required_cap,
                        'token_level': context.capability_token.security_level.name
                    },
                    session_id=context.session_id,
                    threat_type=ThreatType.CAPABILITY_VIOLATION
                ))
                return GateDecision(
                    action=GateAction.BLOCK,
                    allowed=False,
                    reason=f"Missing required capability: {required_cap}",
                    confidence=1.0
                )
                
        context.log_step('capability_passed')
        
        # Step 3: Security level check
        required_level = policy.get('required_level', SecurityLevel.PUBLIC)
        if context.capability_token:
            token_level = context.capability_token.security_level.value
        else:
            token_level = SecurityLevel.PUBLIC.value
            
        if token_level < required_level.value:
            audit_logger.log_privilege_escalation(
                from_level=SecurityLevel(token_level),
                to_level=required_level,
                source=context.source,
                session_id=context.session_id
            )
            return GateDecision(
                action=GateAction.BLOCK,
                allowed=False,
                reason=f"Insufficient security level. Required: {required_level.name}",
                confidence=1.0
            )
            
        context.log_step('security_level_passed')
        
        # Step 4: Injection detection
        if policy.get('scan_injection', True):
            text_payload = self._extract_text(payload)
            if text_payload:
                is_clean, patterns, details = self.injection_detector.scan(
                    text_payload,
                    source=context.source,
                    session_id=context.session_id
                )
                
                if not is_clean:
                    confidence = details.get('confidence', 0.5)
                    
                    # Decide action based on confidence
                    if confidence > 0.8:
                        action = GateAction.BLOCK
                        allowed = False
                    elif confidence > 0.5:
                        action = GateAction.QUARANTINE
                        allowed = False
                    else:
                        action = GateAction.SANITIZE
                        allowed = True
                        
                    # Try sanitization if allowed
                    sanitized_payload = payload
                    sanitizations = []
                    if action in (GateAction.SANITIZE, GateAction.QUARANTINE):
                        sanitized_text = self.injection_detector.sanitize(text_payload)
                        if sanitized_text != text_payload:
                            sanitizations.append('injection_patterns')
                            sanitized_payload = self._replace_text(payload, sanitized_text)
                            
                    return GateDecision(
                        action=action,
                        allowed=allowed,
                        reason=f"Injection patterns detected: {patterns}",
                        confidence=confidence,
                        details=details,
                        sanitizations_applied=sanitizations
                    )
                    
        context.log_step('injection_scan_passed')
        
        # All checks passed
        return GateDecision(
            action=GateAction.ALLOW,
            allowed=True,
            reason="All security checks passed",
            confidence=1.0,
            details={
                'rate_limit_remaining': remaining,
                'request_type': request_type.value,
                'processing_time': time.time() - context.entry_time
            }
        )
        
    def _extract_text(self, payload: Any) -> Optional[str]:
        """Extract text content from various payload types for scanning"""
        if isinstance(payload, str):
            return payload
        elif isinstance(payload, dict):
            # Scan common text fields
            text_fields = ['text', 'message', 'content', 'prompt', 'input', 'query']
            texts = []
            for field in text_fields:
                if field in payload and isinstance(payload[field], str):
                    texts.append(payload[field])
            return ' '.join(texts) if texts else json.dumps(payload)
        elif isinstance(payload, list):
            return ' '.join(str(item) for item in payload if isinstance(item, str))
        return str(payload) if payload is not None else None
        
    def _replace_text(self, payload: Any, new_text: str) -> Any:
        """Replace text content in payload after sanitization"""
        if isinstance(payload, str):
            return new_text
        elif isinstance(payload, dict):
            result = payload.copy()
            # Replace in common text fields
            text_fields = ['text', 'message', 'content', 'prompt', 'input']
            for field in text_fields:
                if field in result and isinstance(result[field], str):
                    result[field] = new_text
                    break
            return result
        return payload
        
    def quarantine_request(self, context: GateContext, payload: Any, 
                          decision: GateDecision):
        """Quarantine a suspicious request for review"""
        quarantine_entry = {
            'timestamp': time.time(),
            'context': {
                'source': context.source,
                'session_id': context.session_id,
                'request_type': context.request_type.value
            },
            'decision': decision.to_dict(),
            'payload_hash': hashlib.sha256(
                json.dumps(payload, default=str).encode()
            ).hexdigest()[:16]
        }
        
        with self._quarantine_lock:
            self._quarantine.append(quarantine_entry)
            # Keep only last 1000 quarantined items
            if len(self._quarantine) > 1000:
                self._quarantine = self._quarantine[-1000:]
                
    def get_quarantine(self, limit: int = 100) -> List[Dict]:
        """Get quarantined requests"""
        with self._quarantine_lock:
            return self._quarantine[-limit:]
            
    def clear_quarantine(self):
        """Clear the quarantine"""
        with self._quarantine_lock:
            self._quarantine.clear()


# Global gate instance
gate = UnifiedGate()


def secure_entry(request_type: RequestType,
                 required_capability: Optional[str] = None,
                 auto_sanitize: bool = True):
    """
    Decorator to secure a function with the unified gate.
    
    Usage:
        @secure_entry(RequestType.FILE_ACCESS, required_capability='fs.read')
        def read_file(path: str, context: GateContext):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Tuple[T, GateDecision]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract or create context
            context = kwargs.get('gate_context')
            if not context:
                # Create default context
                context = GateContext(
                    request_type=request_type,
                    source=func.__name__,
                    session_id=kwargs.get('session_id', 'default'),
                    capability_token=kwargs.get('capability_token')
                )
                
            # Get payload (first arg or 'payload' kwarg)
            if args:
                payload = args[0]
            else:
                payload = kwargs.get('payload', kwargs)
                
            # Process through gate
            decision = gate.process(request_type, payload, context)
            
            if not decision.allowed:
                raise SecurityError(
                    f"Security gate blocked request: {decision.reason}"
                )
                
            # Apply sanitizations
            if decision.sanitizations_applied and auto_sanitize:
                if isinstance(payload, str) and 'injection_patterns' in decision.sanitizations_applied:
                    payload = sanitize_input(payload)
                    if args:
                        args = (payload,) + args[1:]
                    else:
                        kwargs['payload'] = payload
                        
            # Execute function
            result = func(*args, **kwargs)
            
            return result, decision
            
        return wrapper
    return decorator


@contextmanager
def secured_session(source: str,
                    user_id: Optional[str] = None,
                    capability_token: Optional[CapabilityToken] = None,
                    metadata: Optional[Dict] = None):
    """
    Context manager for a secured session.
    
    Usage:
        with secured_session('my_app', capability_token=token) as ctx:
            # All operations use this context
            result = some_secured_operation(payload, gate_context=ctx)
    """
    session_id = f"{source}_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
    
    context = GateContext(
        request_type=RequestType.USER_INPUT,
        source=source,
        session_id=session_id,
        user_id=user_id,
        capability_token=capability_token,
        metadata=metadata or {}
    )
    
    audit_logger.log(SecurityEvent(
        timestamp=time.time(),
        event_type='session_started',
        severity='info',
        source=source,
        details={'session_id': session_id, 'user_id': user_id},
        session_id=session_id,
        user_id=user_id
    ))
    
    try:
        yield context
    finally:
        context.log_step('session_ended')
        audit_logger.log(SecurityEvent(
            timestamp=time.time(),
            event_type='session_ended',
            severity='info',
            source=source,
            details={
                'session_id': session_id,
                'duration': time.time() - context.entry_time,
                'history': context.processing_history
            },
            session_id=session_id,
            user_id=user_id
        ))


class SecurityReport:
    """Generate security status reports"""
    
    @staticmethod
    def generate_summary() -> Dict[str, Any]:
        """Generate a security summary report"""
        detector = InjectionDetector()
        
        # Get recent events
        recent_events = audit_logger.get_events(since=time.time() - 86400)  # Last 24h
        
        threats_by_type = {}
        for event in recent_events:
            if event.threat_type:
                threats_by_type[event.threat_type.name] = \
                    threats_by_type.get(event.threat_type.name, 0) + 1
                
        critical_count = len([e for e in recent_events if e.severity == 'critical'])
        warning_count = len([e for e in recent_events if e.severity == 'warning'])
        
        return {
            'timestamp': time.time(),
            'period_hours': 24,
            'total_events': len(recent_events),
            'critical_events': critical_count,
            'warning_events': warning_count,
            'threats_by_type': threats_by_type,
            'detection_stats': detector.get_stats(),
            'quarantine_size': len(gate.get_quarantine(limit=0)),
            'status': 'healthy' if critical_count == 0 else 'at_risk'
        }
        
    @staticmethod
    def export_full_report(path: str):
        """Export a full security report to file"""
        summary = SecurityReport.generate_summary()
        
        # Get recent events with details
        recent_events = audit_logger.get_events(since=time.time() - 86400)
        events_data = [e.to_dict() for e in recent_events[-100:]]  # Last 100
        
        report = {
            'summary': summary,
            'recent_events': events_data,
            'quarantine': gate.get_quarantine(limit=50)
        }
        
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)
            
        return path


# Convenience functions
def quick_secure(payload: Any, 
                 request_type: RequestType = RequestType.USER_INPUT,
                 source: str = "quick_secure") -> Tuple[Any, GateDecision]:
    """
    Quick one-off security check without full session setup.
    
    Returns:
        (sanitized_payload, decision)
    """
    context = GateContext(
        request_type=request_type,
        source=source,
        session_id=f"quick_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
    )
    
    decision = gate.process(request_type, payload, context)
    
    if decision.sanitizations_applied:
        payload = gate._replace_text(payload, sanitize_input(gate._extract_text(payload)))
        
    return payload, decision


def check_safe(text: str, source: str = "check_safe") -> Tuple[bool, str]:
    """
    Quick check if text is safe.
    
    Returns:
        (is_safe, reason)
    """
    is_clean, details = scan_input(text, source)
    if not is_clean:
        return False, f"Injection detected: {details.get('categories', [])}"
    return True, "Clean"


def create_secure_context(capabilities: List[str],
                         level: SecurityLevel = SecurityLevel.USER,
                         expires_hours: int = 1) -> Tuple[GateContext, CapabilityToken]:
    """
    Create a secured context with a new capability token.
    
    Returns:
        (context, token)
    """
    token = gate.capability_manager.issue_token(
        capabilities=capabilities,
        security_level=level,
        expires_in=expires_hours * 3600
    )
    
    context = GateContext(
        request_type=RequestType.USER_INPUT,
        source='secure_context',
        session_id=f"ctx_{token.token_id[:8]}",
        capability_token=token
    )
    
    return context, token


# Module initialization
__all__ = [
    'UnifiedGate', 'GateContext', 'GateDecision', 'GateAction',
    'RequestType', 'SecurityReport', 'secured_session', 'secure_entry',
    'quick_secure', 'check_safe', 'create_secure_context', 'gate'
]