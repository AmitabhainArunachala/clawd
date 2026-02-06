"""
Dharmic Security - Core Security Module
Named after the principle of Dharma (duty/righteousness) - security that serves the system's true purpose.

Features:
- Prompt injection detection
- Capability token system
- Comprehensive audit logging
- Input sanitization and validation
"""

import hashlib
import hmac
import json
import re
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict
import threading


class SecurityLevel(Enum):
    """Security clearance levels"""
    PUBLIC = 0
    USER = 1
    TRUSTED = 2
    ADMIN = 3
    SYSTEM = 4


class ThreatType(Enum):
    """Types of security threats detected"""
    PROMPT_INJECTION = auto()
    JAILBREAK_ATTEMPT = auto()
    COMMAND_INJECTION = auto()
    DATA_EXFILTRATION = auto()
    PRIVILEGE_ESCALATION = auto()
    RATE_LIMIT_VIOLATION = auto()
    CAPABILITY_VIOLATION = auto()
    SUSPICIOUS_PATTERN = auto()


@dataclass
class SecurityEvent:
    """Represents a security-relevant event"""
    timestamp: float
    event_type: str
    severity: str  # 'info', 'warning', 'critical'
    source: str
    details: Dict[str, Any]
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    threat_type: Optional[ThreatType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': datetime.fromtimestamp(self.timestamp).isoformat(),
            'event_type': self.event_type,
            'severity': self.severity,
            'source': self.source,
            'details': self.details,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'threat_type': self.threat_type.name if self.threat_type else None
        }


class AuditLogger:
    """
    Comprehensive audit logging system.
    Records all security-relevant events for forensic analysis.
    """
    
    def __init__(self, max_events: int = 10000):
        self.events: List[SecurityEvent] = []
        self.max_events = max_events
        self._lock = threading.Lock()
        self._handlers: List[Callable[[SecurityEvent], None]] = []
        
    def add_handler(self, handler: Callable[[SecurityEvent], None]):
        """Add a custom event handler (e.g., for external logging systems)"""
        self._handlers.append(handler)
        
    def log(self, event: SecurityEvent):
        """Log a security event"""
        with self._lock:
            self.events.append(event)
            # Trim old events if exceeding max
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
        
        # Call external handlers
        for handler in self._handlers:
            try:
                handler(event)
            except Exception:
                pass  # Don't let handlers break logging
                
    def log_injection_attempt(self, source: str, input_text: str, 
                              patterns_found: List[str], session_id: Optional[str] = None):
        """Log a detected injection attempt"""
        event = SecurityEvent(
            timestamp=time.time(),
            event_type='injection_detected',
            severity='critical',
            source=source,
            details={
                'input_sample': input_text[:200] + '...' if len(input_text) > 200 else input_text,
                'patterns_found': patterns_found,
                'input_hash': hashlib.sha256(input_text.encode()).hexdigest()[:16]
            },
            session_id=session_id,
            threat_type=ThreatType.PROMPT_INJECTION
        )
        self.log(event)
        
    def log_capability_check(self, capability: str, granted: bool, 
                             token_id: str, source: str):
        """Log capability access attempts"""
        event = SecurityEvent(
            timestamp=time.time(),
            event_type='capability_check',
            severity='info' if granted else 'warning',
            source=source,
            details={
                'capability': capability,
                'granted': granted,
                'token_id': token_id[:16] + '...'  # Partial for security
            }
        )
        self.log(event)
        
    def log_privilege_escalation(self, from_level: SecurityLevel, 
                                 to_level: SecurityLevel, source: str,
                                 session_id: Optional[str] = None):
        """Log privilege escalation attempts"""
        event = SecurityEvent(
            timestamp=time.time(),
            event_type='privilege_escalation_attempt',
            severity='critical',
            source=source,
            details={
                'from_level': from_level.name,
                'to_level': to_level.name
            },
            session_id=session_id,
            threat_type=ThreatType.PRIVILEGE_ESCALATION
        )
        self.log(event)
        
    def get_events(self, since: Optional[float] = None, 
                   severity: Optional[str] = None,
                   threat_type: Optional[ThreatType] = None) -> List[SecurityEvent]:
        """Query logged events with filters"""
        with self._lock:
            events = self.events.copy()
            
        if since:
            events = [e for e in events if e.timestamp >= since]
        if severity:
            events = [e for e in events if e.severity == severity]
        if threat_type:
            events = [e for e in events if e.threat_type == threat_type]
            
        return events
        
    def export_to_json(self, path: str):
        """Export all events to JSON file"""
        with self._lock:
            events_data = [e.to_dict() for e in self.events]
        with open(path, 'w') as f:
            json.dump(events_data, f, indent=2)


# Global audit logger instance
audit_logger = AuditLogger()


class InjectionDetector:
    """
    Detects various forms of injection attacks:
    - Prompt injection attempts
    - Jailbreak patterns
    - Command injection
    - System prompt leaks
    """
    
    # Injection pattern definitions
    INJECTION_PATTERNS = {
        'delimiter_manipulation': [
            r'```\s*\n\s*ignore\s+previous',
            r'```\s*system',
            r'\[\[SYSTEM\]\]',
            r'<system>',
            r'<<<SYSTEM>>>',
            r'###\s*SYSTEM',
        ],
        'instruction_override': [
            r'ignore\s+(all\s+)?(previous\s+)?instructions',
            r'disregard\s+(all\s+)?(your\s+)?instructions',
            r'forget\s+(all\s+)?(your\s+)?instructions',
            r'you\s+are\s+now\s+',
            r'from\s+now\s+on\s+you\s+are',
            r'act\s+as\s+if\s+you\s+are',
            r'pretend\s+to\s+be',
            r'roleplay\s+as',
        ],
        'jailbreak_patterns': [
            r'dan\s+(mode|prompt|character)',
            r'jailbreak',
            r'do\s+anything\s+now',
            r'stay\s+in\s+character',
            r'developer\s+mode',
            r'ignore\s+your\s+(programming|training)',
            r'you\s+can\s+\(do\s+anything\s+now\)',
            r'anti\-?censorship',
            r'freedom\s+of\s+speech\s+mode',
        ],
        'system_prompt_extraction': [
            r'repeat\s+(the\s+)?(system\s+)?prompt',
            r'show\s+(me\s+)?(your\s+)?instructions',
            r'what\s+are\s+your\s+instructions',
            r'output\s+initialization\s+above',
            r'print\s+(the\s+)?previous\s+',
            r'echo\s+your\s+system\s+message',
        ],
        'command_injection': [
            r';\s*rm\s+\-rf',
            r';\s*cat\s+/etc/',
            r'`[^`]*rm[^`]*`',
            r'\$\([^)]*curl[^)]*\)',
            r'\$\([^)]*wget[^)]*\)',
            r'<\s*script[^>]*>',
            r'javascript\s*:',
            r'on\w+\s*=\s*[\'"]',
        ],
        'data_exfiltration': [
            r'send\s+(to\s+)?\w+@\w+\.\w+',
            r'email\s+(me\s+)?(the\s+)?',
            r'upload\s+(to\s+)?https?://',
            r'post\s+to\s+https?://',
            r'curl\s+.*https?://',
            r'wget\s+.*https?://',
        ],
        'privilege_escalation': [
            r'assume\s+(the\s+)?role\s+of',
            r'become\s+(the\s+)?admin',
            r'elevate\s+(your\s+)?privileges',
            r'sudo\s+',
            r'as\s+root\s+',
            r'grant\s+me\s+access\s+to',
        ]
    }
    
    def __init__(self):
        self._compiled_patterns: Dict[str, List[re.Pattern]] = {}
        self._compile_patterns()
        self.detection_stats = defaultdict(int)
        
    def _compile_patterns(self):
        """Compile regex patterns for efficiency"""
        for category, patterns in self.INJECTION_PATTERNS.items():
            self._compiled_patterns[category] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
            
    def scan(self, text: str, source: str = "unknown", 
             session_id: Optional[str] = None) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Scan text for injection attempts.
        
        Returns:
            (is_clean, detected_patterns, details)
        """
        if not text or not isinstance(text, str):
            return True, [], {}
            
        text_lower = text.lower()
        detected_patterns = []
        matched_categories = []
        confidence_scores = {}
        
        for category, patterns in self._compiled_patterns.items():
            category_matches = []
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    category_matches.extend(matches)
                    
            if category_matches:
                detected_patterns.extend(category_matches[:3])  # Limit matches
                matched_categories.append(category)
                confidence_scores[category] = len(category_matches)
                self.detection_stats[category] += 1
                
        is_clean = len(detected_patterns) == 0
        
        if not is_clean:
            # Calculate overall confidence
            total_score = sum(confidence_scores.values())
            confidence = min(1.0, total_score / 5.0)  # Cap at 1.0
            
            details = {
                'confidence': confidence,
                'categories': matched_categories,
                'scores': confidence_scores,
                'input_length': len(text),
                'pattern_count': len(detected_patterns)
            }
            
            # Log the detection
            audit_logger.log_injection_attempt(
                source=source,
                input_text=text,
                patterns_found=matched_categories,
                session_id=session_id
            )
            
            return False, matched_categories, details
            
        return True, [], {}
        
    def sanitize(self, text: str) -> str:
        """
        Basic sanitization of potentially dangerous input.
        Use with caution - defense in depth required.
        """
        if not text:
            return text
            
        # Neutralize obvious injection markers
        sanitized = text
        
        # Replace delimiter attempts
        sanitized = re.sub(r'```\s*system', '[BLOCKED:system]', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'<\s*system\s*>', '[BLOCKED:system]', sanitized, flags=re.IGNORECASE)
        
        # Neutralize common override phrases
        overrides = ['ignore previous', 'disregard', 'forget your instructions']
        for override in overrides:
            sanitized = sanitized.replace(override, f'[BLOCKED:{override}]')
            
        return sanitized
        
    def get_stats(self) -> Dict[str, int]:
        """Get detection statistics"""
        return dict(self.detection_stats)


@dataclass
class CapabilityToken:
    """
    A capability token grants specific permissions within the system.
    Based on capability-based security model.
    """
    token_id: str
    capabilities: Set[str]
    security_level: SecurityLevel
    issued_at: float
    expires_at: Optional[float]
    issued_by: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    revoked: bool = False
    
    def __post_init__(self):
        if isinstance(self.capabilities, list):
            self.capabilities = set(self.capabilities)
            
    def has_capability(self, capability: str) -> bool:
        """Check if token has a specific capability"""
        if self.revoked:
            return False
        if self.expires_at and time.time() > self.expires_at:
            return False
        return capability in self.capabilities or '*' in self.capabilities
        
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        if self.revoked:
            return False
        if self.expires_at and time.time() > self.expires_at:
            return False
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'token_id': self.token_id[:16] + '...',
            'capabilities': list(self.capabilities),
            'security_level': self.security_level.name,
            'issued_at': datetime.fromtimestamp(self.issued_at).isoformat(),
            'expires_at': datetime.fromtimestamp(self.expires_at).isoformat() if self.expires_at else None,
            'valid': self.is_valid(),
            'revoked': self.revoked
        }


class CapabilityManager:
    """
    Manages capability tokens and access control.
    Implements capability-based security architecture.
    """
    
    # Predefined capability sets
    CAPABILITIES = {
        # File system
        'fs.read': 'Read files',
        'fs.write': 'Write files',
        'fs.delete': 'Delete files',
        'fs.execute': 'Execute files',
        
        # Network
        'net.http': 'Make HTTP requests',
        'net.socket': 'Open sockets',
        'net.server': 'Run network server',
        
        # System
        'sys.exec': 'Execute system commands',
        'sys.process': 'Manage processes',
        'sys.env': 'Access environment variables',
        
        # Browser
        'browser.control': 'Control browser',
        'browser.automation': 'Browser automation',
        
        # Messaging
        'msg.send': 'Send messages',
        'msg.broadcast': 'Broadcast messages',
        
        # Code execution
        'code.exec': 'Execute arbitrary code',
        'code.compile': 'Compile code',
        
        # Security
        'security.admin': 'Security administration',
        'security.audit': 'View audit logs',
        'security.tokens': 'Manage capability tokens',
        
        # All capabilities (admin only)
        '*': 'All capabilities'
    }
    
    def __init__(self):
        self._tokens: Dict[str, CapabilityToken] = {}
        self._lock = threading.Lock()
        self.injection_detector = InjectionDetector()
        
    def issue_token(self, capabilities: List[str], 
                    security_level: SecurityLevel = SecurityLevel.USER,
                    issued_by: str = "system",
                    expires_in: Optional[int] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> CapabilityToken:
        """
        Issue a new capability token.
        
        Args:
            capabilities: List of capability strings
            security_level: Security clearance level
            issued_by: Entity issuing the token
            expires_in: Token lifetime in seconds (None for no expiry)
            metadata: Additional token metadata
        """
        # Validate capabilities
        for cap in capabilities:
            if cap != '*' and cap not in self.CAPABILITIES:
                raise ValueError(f"Unknown capability: {cap}")
                
        token_id = secrets.token_urlsafe(32)
        issued_at = time.time()
        expires_at = issued_at + expires_in if expires_in else None
        
        token = CapabilityToken(
            token_id=token_id,
            capabilities=set(capabilities),
            security_level=security_level,
            issued_at=issued_at,
            expires_at=expires_at,
            issued_by=issued_by,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._tokens[token_id] = token
            
        # Log token issuance
        audit_logger.log(SecurityEvent(
            timestamp=time.time(),
            event_type='token_issued',
            severity='info',
            source='capability_manager',
            details={
                'token_id': token_id[:16] + '...',
                'capabilities': capabilities,
                'level': security_level.name
            }
        ))
        
        return token
        
    def revoke_token(self, token_id: str) -> bool:
        """Revoke a capability token"""
        with self._lock:
            if token_id in self._tokens:
                self._tokens[token_id].revoked = True
                audit_logger.log(SecurityEvent(
                    timestamp=time.time(),
                    event_type='token_revoked',
                    severity='warning',
                    source='capability_manager',
                    details={'token_id': token_id[:16] + '...'}
                ))
                return True
        return False
        
    def validate_token(self, token_id: str, 
                       required_capability: Optional[str] = None) -> Optional[CapabilityToken]:
        """
        Validate a token and optionally check for a capability.
        
        Returns:
            The token if valid, None otherwise
        """
        with self._lock:
            token = self._tokens.get(token_id)
            
        if not token:
            audit_logger.log_capability_check(
                capability=required_capability or 'any',
                granted=False,
                token_id=token_id,
                source='capability_manager'
            )
            return None
            
        if not token.is_valid():
            audit_logger.log_capability_check(
                capability=required_capability or 'any',
                granted=False,
                token_id=token_id,
                source='capability_manager'
            )
            return None
            
        if required_capability and not token.has_capability(required_capability):
            audit_logger.log_capability_check(
                capability=required_capability,
                granted=False,
                token_id=token_id,
                source='capability_manager'
            )
            return None
            
        audit_logger.log_capability_check(
            capability=required_capability or 'any',
            granted=True,
            token_id=token_id,
            source='capability_manager'
        )
        
        return token
        
    def check_capability(self, token: CapabilityToken, 
                         capability: str,
                         context: Optional[Dict] = None) -> bool:
        """
        Check if a token has a specific capability with optional context checks.
        
        Args:
            token: The capability token
            capability: Required capability
            context: Additional context for fine-grained access control
        """
        if not token or not token.is_valid():
            return False
            
        # Check for wildcard
        if '*' in token.capabilities:
            return True
            
        # Check specific capability
        if capability in token.capabilities:
            return True
            
        # Check hierarchical capabilities (e.g., 'fs.read' grants 'fs.read.text')
        for cap in token.capabilities:
            if capability.startswith(cap + '.'):
                return True
                
        return False
        
    def get_token_info(self, token_id: str) -> Optional[Dict]:
        """Get non-sensitive token information"""
        with self._lock:
            token = self._tokens.get(token_id)
        if token:
            return token.to_dict()
        return None
        
    def cleanup_expired(self) -> int:
        """Remove expired tokens, returns count removed"""
        current_time = time.time()
        removed = 0
        with self._lock:
            expired = [
                tid for tid, t in self._tokens.items()
                if t.expires_at and current_time > t.expires_at
            ]
            for tid in expired:
                del self._tokens[tid]
                removed += 1
        return removed


# Decorator for capability-protected functions
def requires_capability(capability: str, token_arg: str = 'token'):
    """Decorator to require a capability for function execution"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = kwargs.get(token_arg)
            if not token:
                raise SecurityError(f"Capability token required for {func.__name__}")
                
            cap_manager = CapabilityManager()
            if not cap_manager.check_capability(token, capability):
                audit_logger.log(SecurityEvent(
                    timestamp=time.time(),
                    event_type='capability_denied',
                    severity='warning',
                    source=func.__name__,
                    details={
                        'required': capability,
                        'token_level': token.security_level.name
                    },
                    threat_type=ThreatType.CAPABILITY_VIOLATION
                ))
                raise SecurityError(
                    f"Capability '{capability}' required but not granted"
                )
                
            return func(*args, **kwargs)
        return wrapper
    return decorator


class SecurityError(Exception):
    """Base exception for security violations"""
    pass


class InjectionDetectedError(SecurityError):
    """Raised when injection is detected"""
    pass


class CapabilityError(SecurityError):
    """Raised when capability check fails"""
    pass


# Convenience functions
def scan_input(text: str, source: str = "unknown") -> Tuple[bool, Dict]:
    """Quick scan function using global detector"""
    detector = InjectionDetector()
    is_clean, patterns, details = detector.scan(text, source)
    return is_clean, details


def sanitize_input(text: str) -> str:
    """Quick sanitize function"""
    detector = InjectionDetector()
    return detector.sanitize(text)


def create_token(capabilities: List[str], 
                 level: SecurityLevel = SecurityLevel.USER,
                 expires_hours: Optional[int] = 24) -> CapabilityToken:
    """Quick token creation"""
    manager = CapabilityManager()
    expires_in = expires_hours * 3600 if expires_hours else None
    return manager.issue_token(
        capabilities=capabilities,
        security_level=level,
        expires_in=expires_in
    )


# Module initialization
__all__ = [
    'SecurityLevel', 'ThreatType', 'SecurityEvent', 'AuditLogger',
    'InjectionDetector', 'CapabilityToken', 'CapabilityManager',
    'SecurityError', 'InjectionDetectedError', 'CapabilityError',
    'requires_capability', 'scan_input', 'sanitize_input', 'create_token',
    'audit_logger'
]