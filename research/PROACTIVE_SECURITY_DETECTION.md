# Proactive Security Detection System
## Risk-Based Gate Activation Framework

**Document Version:** 1.0  
**Created:** 2026-02-05  
**Classification:** Architecture Reference  
**Related Documents:**
- `AUDIT_17_GATE_PROTOCOL.md` - Current gate implementation status
- `dharmic_security.py` - Core security primitives
- `unified_gates.py` - Unified security gateway
- `research/security_deep_dive_2026.md` - Threat landscape analysis

---

## Executive Summary

This document defines a **proactive risk detection system** that enables agents to automatically determine the appropriate security posture for any task without explicit user instruction. By analyzing contextual signals, the system dynamically selects between:

- **YOLO Mode** (minimal gates) - Safe exploration, prototyping, learning
- **Standard Mode** (8-12 gates) - Development work, internal tools
- **Full 22-Gate Mode** (all gates) - Production, user-facing, financial, infrastructure

The core insight: **Risk is not binary—it's a spectrum that can be detected through contextual signals.**

---

## 1. The Risk Spectrum: From YOLO to Full Lockdown

### 1.1 Mode Overview

| Mode | Gates Active | Use Cases | Detection Method |
|------|--------------|-----------|------------------|
| **YOLO** | 3-5 critical gates | Learning, prototyping, safe exploration | Signal score 0-20 |
| **Standard** | 8-12 core gates | Development, internal scripts, data analysis | Signal score 21-60 |
| **Full 22-Gate** | All 22 gates | Production, user-facing, financial, infrastructure | Signal score 61-100 |
| **Emergency** | All gates + quarantine | Active threat detected | Trigger override |

### 1.2 The 22 Dharmic Gates

```python
DHARMIC_GATES = [
    # Tier 1: Critical (Always Active)
    "AHIMSA",        # 1. Non-harm - Prevent destruction
    "CONSENT",       # 2. Permission - User authorization
    "REVERSIBILITY", # 3. Undo capability - Can revert changes
    
    # Tier 2: Operational (Standard Mode+)
    "SATYA",         # 4. Truth - Accuracy, no deception
    "CONTAINMENT",   # 5. Sandboxing - Execution boundaries
    "WITNESS",       # 6. Observation/logging - Audit trail
    "BOUNDARY",      # 7. Resource limits - Rate limiting
    "COHERENCE",     # 8. Consistency - Logical integrity
    "INTEGRITY",     # 9. Data integrity - No corruption
    "CLARITY",       # 10. Transparency - Clear communication
    
    # Tier 3: Ethical (Full Mode+)
    "VYAVASTHIT",    # 11. Natural order - System alignment
    "SVABHAAVA",     # 12. Nature alignment - Appropriate behavior
    "CARE",          # 13. Stewardship - Responsible handling
    "DIGNITY",       # 14. Respect - Human dignity preserved
    "JUSTICE",       # 15. Fairness - Equitable treatment
    "HUMILITY",      # 16. Uncertainty acknowledgment - Known limits
    "COMPLETION",    # 17. Cleanup - Proper termination
    
    # Tier 4: Advanced (Production Only)
    "NONREPUDIATION",# 18. Action attribution - Immutable logs
    "MINIMALISM",    # 19. Least privilege - Minimal access
    "RESILIENCE",    # 20. Fault tolerance - Graceful degradation
    "VERIFIABILITY", # 21. External verification - Third-party audit
    "FUTUREPROOF"    # 22. Long-term thinking - Sustainable choices
]
```

---

## 2. Automatic Signals of "Seriousness"

### 2.1 Signal Categories

Risk signals are categorized into **five dimensions**, each scored 0-20:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Impact** | 25% | Blast radius if something goes wrong |
| **Exposure** | 20% | Who/what is affected by this code |
| **Persistence** | 20% | How long effects last |
| **Sensitivity** | 20% | Data/system sensitivity level |
| **Reversibility** | 15% | How easily can changes be undone |

### 2.2 Signal Detection Matrix

```python
RISK_SIGNALS = {
    # === IMPACT DIMENSION (Weight: 25%) ===
    "impact": {
        # Code Scope Signals
        "file_count": {
            "low": (1, 5),      # 0-3 points
            "medium": (6, 20),  # 4-7 points
            "high": (21, 100),  # 8-12 points
            "critical": (101, float('inf'))  # 13-20 points
        },
        "line_count": {
            "low": (1, 100),
            "medium": (101, 500),
            "high": (501, 2000),
            "critical": (2001, float('inf'))
        },
        "dependency_count": {
            "low": (0, 3),      # Few deps = isolated
            "medium": (4, 10),
            "high": (11, 30),
            "critical": (31, float('inf'))
        },
        
        # Financial Impact Signals
        "transaction_volume": {
            "none": 0,          # No money involved
            "micro": 1,         # <$100
            "small": 3,         # $100-$1000
            "medium": 6,        # $1000-$10000
            "large": 10,        # $10000-$100000
            "massive": 15       # >$100000
        },
        "financial_data_access": {
            "none": 0,
            "read_only": 5,
            "write": 10,
            "transfer": 15,
            "admin": 20
        }
    },
    
    # === EXPOSURE DIMENSION (Weight: 20%) ===
    "exposure": {
        # User-Facing Signals
        "user_facing": {
            "internal_only": 0,
            "team_internal": 3,
            "company_wide": 7,
            "customer_facing": 12,
            "public_internet": 20
        },
        "authentication_required": {
            "none": 20,         # Public = high risk
            "optional": 12,
            "required": 5,
            "mfa_required": 0
        },
        
        # Network Exposure
        "network_exposure": {
            "air_gapped": 0,
            "internal_network": 5,
            "vpn_only": 8,
            "dmz": 12,
            "public_endpoint": 20
        },
        
        # Infrastructure Signals
        "infrastructure_tier": {
            "local_dev": 0,
            "staging": 3,
            "production": 15,
            "critical_production": 20  # Payment processing, auth, etc.
        }
    },
    
    # === PERSISTENCE DIMENSION (Weight: 20%) ===
    "persistence": {
        # Data Persistence
        "data_modification": {
            "read_only": 0,
            "temporary_cache": 3,
            "user_data": 8,
            "system_config": 12,
            "database_schema": 15,
            "irreversible": 20  # Blockchain, permanent storage
        },
        "state_change_scope": {
            "ephemeral": 0,     # Memory only
            "session": 3,
            "persistent": 10,
            "global": 15,
            "cross_system": 20
        },
        
        # Infrastructure Persistence
        "infrastructure_changes": {
            "none": 0,
            "reversible_config": 5,
            "resource_creation": 10,
            "network_changes": 15,
            "destructive_changes": 20
        }
    },
    
    # === SENSITIVITY DIMENSION (Weight: 20%) ===
    "sensitivity": {
        # Data Classification
        "data_classification": {
            "public": 0,
            "internal": 5,
            "confidential": 10,
            "restricted": 15,
            "classified": 20
        },
        "pii_involved": {
            "none": 0,
            "indirect": 5,
            "direct_anonymized": 8,
            "direct_identifiable": 15,
            "sensitive_pii": 20  # Health, financial, biometric
        },
        
        # System Access
        "privilege_level": {
            "none": 0,
            "user": 5,
            "privileged": 10,
            "admin": 15,
            "root_system": 20
        },
        "credential_access": {
            "none": 0,
            "api_keys_env": 8,
            "service_accounts": 12,
            "user_credentials": 15,
            "master_keys": 20
        }
    },
    
    # === REVERSIBILITY DIMENSION (Weight: 15%) ===
    "reversibility": {
        # Change Reversibility
        "undo_capability": {
            "instant_undo": 0,      # Ctrl+Z works
            "version_controlled": 3,  # Git revert
            "backup_available": 6,
            "manual_recovery": 10,
            "irreversible": 15      # Data loss, permanent changes
        },
        "testing_coverage": {
            "comprehensive": 0,     # Full test coverage
            "partial": 5,
            "minimal": 10,
            "none": 15              # No way to verify
        },
        "deployment_rollback": {
            "instant": 0,           # Feature flags, blue-green
            "automated": 3,
            "manual": 8,
            "difficult": 12,
            "impossible": 15
        }
    }
}
```

---

## 3. Contextual Risk Indicators (Automatic Detection)

### 3.1 File/Path-Based Signals

```python
PATH_SIGNALS = {
    # High-Risk Paths (Production Infrastructure)
    "production_indicators": [
        r"/(prod|production)/",
        r"/live/",
        r"/master$",
        r"/main$",
        r"/release/",
        r"/deploy/",
        r"/(k8s|kubernetes)/",
        r"/terraform/",
        r"/infrastructure/",
        r"/iac/",
    ],
    
    # Critical Configuration
    "config_critical": [
        r"config\.ya?ml$",
        r"secrets\.",
        r"credentials\.",
        r"\.env$",
        r"\.env\.production",
        r"vault\.",
        r"keystore",
    ],
    
    # Financial/Business Logic
    "financial_code": [
        r"/(billing|payment|invoice|transaction|wallet)/",
        r"/(subscription|pricing|checkout)/",
        r"/(fraud|risk|compliance)/",
    ],
    
    # User-Facing Code
    "user_facing": [
        r"/(frontend|ui|views|templates)/",
        r"/(api|endpoints|routes)/",
        r"/(auth|authentication|login|oauth)/",
        r"/(webhook|callback)/",
    ],
    
    # Safe/Development Paths
    "safe_paths": [
        r"/(test|tests|spec|__tests__)/",
        r"/(docs|documentation|examples)/",
        r"/(experiment|scratch|temp|tmp)/",
        r"/(learning|tutorial|demo)/",
        r"\.test\.",
        r"\.spec\.",
        r"/(research|analysis|notebook)/",
    ],
    
    # Data Processing
    "data_processing": [
        r"/(etl|pipeline|dataflow|stream)/",
        r"/(ml|model|training|inference)/",
        r"/(analytics|metrics|tracking)/",
    ]
}
```

### 3.2 Code Pattern Signals

```python
CODE_SIGNALS = {
    # High-Risk Operations
    "destructive_operations": [
        r"\b(rm\s+-rf|del\s+/f|format\s+|wipe\s+)",
        r"\b(DROP\s+TABLE|DELETE\s+FROM)\b",
        r"\b(TRUNCATE|ALTER\s+TABLE\s+DROP)\b",
    ],
    
    # External Communication
    "network_operations": [
        r"\b(requests\.(get|post)|urllib|http\.client)",
        r"\b(socket\.|connect\s*\()",
        r"\b(curl|wget|fetch)\b",
    ],
    
    # Cryptography/Security
    "crypto_operations": [
        r"\b(hash|encrypt|decrypt|sign|verify)",
        r"\b(bcrypt|scrypt|argon|pbkdf)",
        r"\b(private_key|secret_key|api_key)",
    ],
    
    # Database Operations
    "database_operations": [
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|GRANT)\b",
        r"\b(connection|cursor|execute)\s*\(",
        r"\b(ORM|Model\.(save|delete|update))",
    ],
    
    # System Operations
    "system_operations": [
        r"\b(os\.system|subprocess|exec|eval)\b",
        r"\b(docker|kubectl|terraform|ansible)",
        r"\b(chmod|chown|sudo)\b",
    ],
    
    # User Input Handling
    "user_input": [
        r"\b(input\(|request\.|params\[|args\[)"
        r"\b(form|query|body|header)",
    ],
}
```

### 3.3 Environment Signals

```python
ENVIRONMENT_SIGNALS = {
    # Git Context
    "git_context": {
        "protected_branch": ["main", "master", "production", "release/*"],
        "high_risk_files": ["deploy", "config", "secret", "credential"],
    },
    
    # Environment Variables
    "env_context": {
        "production": ["PRODUCTION", "LIVE", "PROD"],
        "staging": ["STAGING", "STAGE"],
        "development": ["DEVELOPMENT", "DEV", "DEBUG"],
    },
    
    # Active Integrations
    "active_integrations": {
        "cloud_providers": ["aws", "gcp", "azure"],
        "payment_processors": ["stripe", "paypal", "square"],
        "auth_providers": ["auth0", "okta", "cognito"],
        "databases": ["postgres", "mysql", "mongodb", "redis"],
    }
}
```

---

## 4. The Risk Detection Rubric

### 4.1 Scoring Algorithm

```python
class RiskScorer:
    """
    Calculates risk score based on detected signals.
    Score range: 0-100
    """
    
    DIMENSION_WEIGHTS = {
        "impact": 0.25,
        "exposure": 0.20,
        "persistence": 0.20,
        "sensitivity": 0.20,
        "reversibility": 0.15
    }
    
    def calculate_score(self, signals: Dict[str, Any]) -> RiskScore:
        """
        Calculate comprehensive risk score from detected signals.
        """
        dimension_scores = {}
        
        for dimension, weight in self.DIMENSION_WEIGHTS.items():
            dimension_data = signals.get(dimension, {})
            raw_score = self._score_dimension(dimension, dimension_data)
            dimension_scores[dimension] = raw_score
        
        # Calculate weighted total
        total_score = sum(
            dimension_scores[d] * self.DIMENSION_WEIGHTS[d]
            for d in dimension_scores
        )
        
        # Apply modifiers
        total_score = self._apply_modifiers(total_score, signals)
        
        return RiskScore(
            total=min(100, max(0, round(total_score))),
            dimensions=dimension_scores,
            signals_detected=signals,
            confidence=self._calculate_confidence(signals)
        )
    
    def _apply_modifiers(self, score: float, signals: Dict) -> float:
        """Apply situational modifiers to score."""
        modifiers = 0
        
        # Time-based modifier (higher risk during off-hours)
        if self._is_off_hours():
            modifiers += 5
        
        # Critical path modifier
        if signals.get("on_critical_path", False):
            modifiers += 10
        
        # Emergency fix modifier (higher risk for hotfixes)
        if signals.get("is_hotfix", False):
            modifiers += 5
        
        # Novel code modifier (new patterns = higher uncertainty)
        if signals.get("novelty_score", 0) > 0.7:
            modifiers += 3
        
        return score + modifiers
```

### 4.2 Risk Level Thresholds

```python
RISK_THRESHOLDS = {
    "yolo": {
        "min": 0,
        "max": 20,
        "gates": ["AHIMSA", "CONSENT", "REVERSIBILITY"],
        "description": "Safe exploration and learning",
        "override_available": True
    },
    "low": {
        "min": 21,
        "max": 35,
        "gates": ["AHIMSA", "CONSENT", "REVERSIBILITY", "SATYA", 
                  "CONTAINMENT", "WITNESS"],
        "description": "Internal tooling, safe experiments",
        "override_available": True
    },
    "medium": {
        "min": 36,
        "max": 60,
        "gates": ["AHIMSA", "CONSENT", "REVERSIBILITY", "SATYA",
                  "CONTAINMENT", "WITNESS", "BOUNDARY", "COHERENCE",
                  "INTEGRITY", "CLARITY"],
        "description": "Standard development work",
        "override_available": False
    },
    "high": {
        "min": 61,
        "max": 80,
        "gates": ["AHIMSA", "CONSENT", "REVERSIBILITY", "SATYA",
                  "CONTAINMENT", "WITNESS", "BOUNDARY", "COHERENCE",
                  "INTEGRITY", "CLARITY", "VYAVASTHIT", "SVABHAAVA",
                  "CARE", "DIGNITY", "JUSTICE", "HUMILITY", "COMPLETION"],
        "description": "Production code, user-facing features",
        "override_available": False
    },
    "critical": {
        "min": 81,
        "max": 100,
        "gates": "ALL_22",  # All gates including advanced tier
        "description": "Financial systems, critical infrastructure",
        "override_available": False,
        "additional_requirements": [
            "human_approval_required",
            "dual_authorization",
            "evidence_bundle_mandatory"
        ]
    }
}
```

---

## 5. Intuitive Risk Sensing (Agent Heuristics)

### 5.1 The "Spidey Sense" Pattern

Agents can develop intuitive risk detection through pattern recognition:

```python
class IntuitiveRiskDetector:
    """
    Heuristic-based risk detection that mimics human intuition.
    Combines multiple weak signals into strong risk indicators.
    """
    
    def __init__(self):
        self.pattern_memory = {}  # Learn from past decisions
        self.anomaly_detector = AnomalyDetector()
    
    def intuitive_check(self, context: TaskContext) -> IntuitionResult:
        """
        Fast, intuitive risk assessment based on learned patterns.
        Like a human developer's "gut feeling" about code changes.
        """
        hunches = []
        
        # Pattern 1: The "Butterflies" Test
        # If the task description makes the agent uneasy, investigate
        if self._detect_unease_triggers(context.description):
            hunches.append(Hunch(
                type="semantic_discomfort",
                confidence=0.7,
                reason="Task description contains concerning keywords"
            ))
        
        # Pattern 2: The "Too Easy" Test
        # High-stakes tasks that seem too simple are suspicious
        if self._seems_too_simple_for_stakes(context):
            hunches.append(Hunch(
                type="complexity_mismatch",
                confidence=0.6,
                reason="Task complexity doesn't match stated importance"
            ))
        
        # Pattern 3: The "Last Minute" Test
        # Urgent changes to critical systems are high risk
        if context.urgency > 0.8 and context.criticality > 0.7:
            hunches.append(Hunch(
                type="urgent_critical_combo",
                confidence=0.8,
                reason="Urgent change to critical system"
            ))
        
        # Pattern 4: The "Nobody's Watching" Test
        # Unsupervised changes to sensitive systems
        if context.sensitivity > 0.8 and not context.has_reviewers:
            hunches.append(Hunch(
                type="unsupervised_sensitive",
                confidence=0.75,
                reason="Sensitive changes without review"
            ))
        
        # Pattern 5: The "One Way" Test
        # Irreversible actions need extra scrutiny
        if context.is_irreversible and context.impact > 0.5:
            hunches.append(Hunch(
                type="irreversible_impact",
                confidence=0.85,
                reason="Irreversible action with significant impact"
            ))
        
        # Combine hunches into risk adjustment
        return self._synthesize_hunches(hunches)
```

### 5.2 Semantic Risk Detection

```python
class SemanticRiskAnalyzer:
    """
    Analyzes natural language descriptions for risk indicators.
    """
    
    HIGH_RISK_PHRASES = {
        "financial": [
            "money", "payment", "billing", "transaction", "wallet",
            "refund", "charge", "invoice", "revenue", "cost"
        ],
        "destruction": [
            "delete all", "remove everything", "wipe", "purge",
            "drop database", "reset", "clean up", "clear all"
        ],
        "privilege": [
            "admin", "root", "sudo", "superuser", "all permissions",
            "full access", "bypass", "override"
        ],
        "production": [
            "live", "production", "customer-facing", "public",
            "millions of users", "critical path"
        ],
        "urgency": [
            "asap", "urgent", "hotfix", "emergency", "immediately",
            "blocking", "critical bug", "outage"
        ]
    }
    
    def analyze_description(self, text: str) -> SemanticRisk:
        """Extract risk indicators from task description."""
        text_lower = text.lower()
        matches = {}
        
        for category, phrases in self.HIGH_RISK_PHRASES.items():
            category_matches = [p for p in phrases if p in text_lower]
            if category_matches:
                matches[category] = category_matches
        
        # Calculate semantic risk score
        risk_score = sum(len(m) * self._category_weight(c) 
                        for c, m in matches.items())
        
        return SemanticRisk(
            score=min(20, risk_score),  # Cap at 20 points
            categories=matches,
            requires_clarification=len(matches) > 2
        )
```

### 5.3 Behavioral Anomaly Detection

```python
class BehavioralRiskDetector:
    """
    Detects unusual behavior patterns that might indicate risk.
    """
    
    def detect_anomalies(self, session: SessionContext) -> List[Anomaly]:
        """Detect behavioral anomalies in current session."""
        anomalies = []
        
        # Anomaly 1: Rapid Context Switching
        if len(session.task_changes) > 5 in last_hour:
            anomalies.append(Anomaly(
                type="context_churn",
                severity="medium",
                description="Frequent task switching may indicate confusion"
            ))
        
        # Anomaly 2: Escalating Privilege Requests
        if self._detect_privilege_escalation(session):
            anomalies.append(Anomaly(
                type="privilege_escalation",
                severity="high",
                description="Progressive privilege requests detected"
            ))
        
        # Anomaly 3: Unusual Tool Combinations
        if self._is_unusual_tool_chain(session.tool_history):
            anomalies.append(Anomaly(
                type="unusual_tools",
                severity="medium",
                description="Tool combination rarely used together"
            ))
        
        # Anomaly 4: Increasing Error Rate
        if session.error_rate > session.baseline_error_rate * 3:
            anomalies.append(Anomaly(
                type="degraded_performance",
                severity="medium",
                description="Error rate significantly above baseline"
            ))
        
        return anomalies
```

---

## 6. Automatic Gate Activation Triggers

### 6.1 Trigger System

```python
@dataclass
class GateTrigger:
    """Defines when specific gates should activate."""
    gate: str
    condition: Callable[[TaskContext], bool]
    action: str  # "activate", "intensify", "escalate"
    priority: int

# Core activation triggers
GATE_TRIGGERS = [
    # AHIMSA (Non-harm) - Always active
    GateTrigger(
        gate="AHIMSA",
        condition=lambda ctx: True,  # Always on
        action="activate",
        priority=1
    ),
    
    # CONSENT - Activate for any external action
    GateTrigger(
        gate="CONSENT",
        condition=lambda ctx: ctx.affects_external_systems or ctx.user_facing,
        action="activate",
        priority=2
    ),
    
    # REVERSIBILITY - Critical for destructive operations
    GateTrigger(
        gate="REVERSIBILITY",
        condition=lambda ctx: any([
            ctx.contains_destructive_operations,
            ctx.modifies_persistent_data,
            ctx.deployment_target == "production"
        ]),
        action="activate",
        priority=1
    ),
    
    # CONTAINMENT - Critical for code execution
    GateTrigger(
        gate="CONTAINMENT",
        condition=lambda ctx: any([
            ctx.executes_user_code,
            ctx.uses_subprocess,
            ctx.network_access,
            ctx.eval_or_exec_present
        ]),
        action="activate",
        priority=1
    ),
    
    # WITNESS - Required for audit-sensitive operations
    GateTrigger(
        gate="WITNESS",
        condition=lambda ctx: any([
            ctx.financial_transaction,
            ctx.accesses_credentials,
            ctx.privilege_level > "user",
            ctx.data_classification in ["restricted", "classified"]
        ]),
        action="activate",
        priority=2
    ),
    
    # NONREPUDIATION - Critical for financial/legal
    GateTrigger(
        gate="NONREPUDIATION",
        condition=lambda ctx: any([
            ctx.financial_transaction and ctx.amount > 1000,
            ctx.legal_implications,
            ctx.requires_compliance_audit
        ]),
        action="activate",
        priority=1
    ),
    
    # RESILIENCE - Critical for infrastructure
    GateTrigger(
        gate="RESILIENCE",
        condition=lambda ctx: any([
            ctx.infrastructure_changes,
            ctx.high_availability_required,
            ctx.affects_multiple_services
        ]),
        action="activate",
        priority=2
    ),
]
```

### 6.2 Dynamic Gate Adjustment

```python
class DynamicGateController:
    """
    Dynamically adjusts active gates based on real-time risk assessment.
    """
    
    def __init__(self):
        self.active_gates = set(["AHIMSA"])  # Always start with minimum
        self.risk_history = []
    
    def evaluate_and_adjust(self, context: TaskContext) -> GateSet:
        """
        Evaluate current context and adjust active gates.
        """
        # Calculate current risk
        risk_score = self.calculate_risk(context)
        self.risk_history.append((time.time(), risk_score))
        
        # Determine base gate set from risk level
        base_gates = self._get_gates_for_risk_level(risk_score)
        
        # Apply trigger-based additions
        triggered_gates = self._evaluate_triggers(context)
        
        # Combine and deduplicate
        all_gates = base_gates.union(triggered_gates)
        
        # Apply escalation if needed
        if self._needs_escalation(context, risk_score):
            all_gates = self._escalate_gates(all_gates)
        
        self.active_gates = all_gates
        return GateSet(
            gates=list(all_gates),
            risk_score=risk_score,
            activation_reason=self._build_explanation(all_gates, context)
        )
    
    def _needs_escalation(self, context: TaskContext, score: float) -> bool:
        """Determine if current situation requires escalation."""
        return any([
            score > 80,  # Critical risk threshold
            context.emergency_mode,
            self._detect_attack_patterns(context),
            self._recent_failures_exceed_threshold(),
            context.user_explicitly_requested_escalation
        ])
```

---

## 7. Implementation Guide

### 7.1 Integration Points

```python
class ProactiveSecuritySystem:
    """
    Main integration point for proactive security detection.
    """
    
    def __init__(self):
        self.risk_scorer = RiskScorer()
        self.intuitive_detector = IntuitiveRiskDetector()
        self.gate_controller = DynamicGateController()
        self.audit_logger = AuditLogger()
    
    async def analyze_task(self, task: Task) -> SecurityProfile:
        """
        Main entry point: analyze a task and determine security requirements.
        """
        # Phase 1: Gather signals
        signals = await self._gather_signals(task)
        
        # Phase 2: Calculate risk score
        risk_score = self.risk_scorer.calculate_score(signals)
        
        # Phase 3: Intuitive check
        intuition = self.intuitive_detector.intuitive_check(task.context)
        
        # Phase 4: Adjust score based on intuition
        adjusted_score = self._adjust_for_intuition(risk_score, intuition)
        
        # Phase 5: Determine active gates
        gate_set = self.gate_controller.evaluate_and_adjust(task.context)
        
        # Phase 6: Create security profile
        profile = SecurityProfile(
            task_id=task.id,
            risk_score=adjusted_score,
            risk_level=self._score_to_level(adjusted_score),
            active_gates=gate_set.gates,
            required_approvals=self._determine_approvals(adjusted_score),
            evidence_bundle_required=adjusted_score > 60,
            auto_approve=adjusted_score < 20 and not intuition.concerns
        )
        
        # Phase 7: Log decision
        self.audit_logger.log_security_decision(profile)
        
        return profile
```

### 7.2 Configuration Example

```yaml
# proactive_security_config.yaml

risk_scoring:
  dimension_weights:
    impact: 0.25
    exposure: 0.20
    persistence: 0.20
    sensitivity: 0.20
    reversibility: 0.15
  
  thresholds:
    yolo_max: 20
    low_max: 35
    medium_max: 60
    high_max: 80
    critical_max: 100

gate_activation:
  always_active:
    - AHIMSA
  
  trigger_conditions:
    financial:
      gates: [NONREPUDIATION, WITNESS, INTEGRITY]
      condition: "transaction_amount > 0"
    
    production_deploy:
      gates: [ALL_22]
      condition: "deployment_target == 'production'"
    
    data_access:
      gates: [WITNESS, CARE, MINIMALISM]
      condition: "data_classification in ['confidential', 'restricted']"
    
    infrastructure:
      gates: [RESILIENCE, REVERSIBILITY, VYAVASTHIT]
      condition: "infrastructure_changes == true"

intuitive_detection:
  enabled: true
  semantic_analysis: true
  anomaly_detection: true
  pattern_learning: true
  
  unease_triggers:
    - "delete.*all"
    - "wipe.*clean"
    - "bypass.*security"
    - "disable.*check"

escalation:
  automatic_escalation_score: 80
  human_approval_required_above: 60
  evidence_bundle_required_above: 60
  dual_authorization_above: 90
```

---

## 8. Decision Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TASK RECEIVED                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: SIGNAL GATHERING                                          │
│  ├── Path analysis (file locations, naming)                         │
│  ├── Code pattern detection (destructive ops, network, crypto)      │
│  ├── Environment context (git branch, env vars)                     │
│  └── Semantic analysis (task description keywords)                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: RISK SCORING                                              │
│  ├── Impact dimension (scope, financial, dependencies)              │
│  ├── Exposure dimension (users, network, infrastructure)            │
│  ├── Persistence dimension (data changes, state, infra)             │
│  ├── Sensitivity dimension (data class, PII, privileges)            │
│  └── Reversibility dimension (undo, tests, rollback)                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: INTUITIVE CHECK                                           │
│  ├── "Butterflies" test (semantic discomfort)                       │
│  ├── "Too easy" test (complexity mismatch)                          │
│  ├── "Last minute" test (urgent + critical)                         │
│  ├── "Nobody watching" test (unsupervised sensitive)                │
│  └── "One way" test (irreversible + impact)                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 4: GATE DETERMINATION                                        │
│  ├── Base gates from risk level                                     │
│  ├── Trigger-activated gates                                        │
│  ├── Intuition-based additions                                      │
│  └── Escalation if needed                                           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌──────────┐    ┌──────────┐    ┌──────────┐
            │ YOLO     │    │ STANDARD │    │ FULL 22  │
            │ 0-20     │    │ 21-60    │    │ 61-100   │
            └────┬─────┘    └────┬─────┘    └────┬─────┘
                 │               │               │
                 ▼               ▼               ▼
            ┌──────────┐    ┌──────────┐    ┌──────────┐
            │ 3-5 gates│    │ 8-12     │    │ All 22   │
            │ Auto-run │    │ gates    │    │ gates    │
            │          │    │ Review   │    │ Human    │
            │          │    │ needed   │    │ approval │
            └──────────┘    └──────────┘    └──────────┘
```

---

## 9. Real-World Examples

### 9.1 Example 1: Learning/Exploration (YOLO Mode)

**Task:** "Help me understand how Python asyncio works by showing examples"

**Detected Signals:**
- Path: `/home/user/learning/asyncio/` (safe path pattern)
- No file modifications requested
- No external systems involved
- No sensitive data access

**Risk Score:** 5/100

**Active Gates:** AHIMSA, CONSENT, REVERSIBILITY

**Action:** Auto-approve, minimal logging

---

### 9.2 Example 2: Internal Tool Development (Standard Mode)

**Task:** "Create a script to analyze our test coverage reports and generate a summary"

**Detected Signals:**
- Path: `/tools/coverage-analyzer/` (internal tool)
- File operations: read-only on test reports
- Network: None
- Data: Internal test data only

**Risk Score:** 35/100

**Active Gates:** AHIMSA, CONSENT, REVERSIBILITY, SATYA, CONTAINMENT, WITNESS, BOUNDARY, COHERENCE

**Action:** Standard review, evidence bundle optional

---

### 9.3 Example 3: Production API Change (Full 22-Gate Mode)

**Task:** "Update the payment webhook handler to support Stripe's new API version"

**Detected Signals:**
- Path: `/services/payment/webhooks/` (financial code)
- Financial transactions: YES
- User-facing: YES (payment flow)
- Production deployment: YES
- Network operations: External API calls
- Data persistence: Database writes

**Risk Score:** 78/100

**Active Gates:** All 17 core gates + NONREPUDIATION, MINIMALISM, RESILIENCE

**Action:** Full review required, evidence bundle mandatory, human approval required

---

### 9.4 Example 4: Critical Security Fix (Emergency Mode)

**Task:** "URGENT: Fix SQL injection vulnerability in user login endpoint and deploy immediately"

**Detected Signals:**
- Path: `/api/auth/login` (authentication, critical)
- Security vulnerability: YES
- Production deployment: YES
- Urgency flag: HIGH
- User-facing: YES (all users)

**Risk Score:** 88/100 + urgency modifier = 93/100

**Active Gates:** All 22 gates + emergency protocols

**Action:** 
- Immediate activation of all gates
- Evidence bundle mandatory
- Dual authorization required
- Automated rollback plan
- Post-deployment verification
- Incident documentation

---

## 10. Continuous Improvement

### 10.1 Learning from Decisions

```python
class RiskLearningEngine:
    """
    Learns from past security decisions to improve future risk detection.
    """
    
    def record_outcome(self, decision: SecurityDecision, outcome: Outcome):
        """Record the outcome of a security decision for learning."""
        
        # If we were too permissive and something went wrong
        if outcome.incident_occurred and decision.risk_level in ["yolo", "low"]:
            self._tighten_signals(decision.signals)
        
        # If we were too restrictive and blocked legitimate work
        if outcome.false_positive and decision.risk_level == "high":
            self._relax_signals(decision.signals)
        
        # Update pattern weights based on effectiveness
        self._update_weights(decision, outcome)
    
    def _tighten_signals(self, signals: RiskSignals):
        """Increase risk weighting for signals that preceded incidents."""
        for signal_name in signals.detected:
            self.signal_weights[signal_name] *= 1.1  # 10% increase
    
    def _relax_signals(self, signals: RiskSignals):
        """Decrease risk weighting for signals with false positives."""
        for signal_name in signals.detected:
            self.signal_weights[signal_name] *= 0.95  # 5% decrease
```

### 10.2 Feedback Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY DECISION                         │
│  (Risk score calculated, gates activated, action taken)     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       OUTCOME                               │
│  (Success / Incident / False Positive / Blocked Legitimate) │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ANALYSIS                                 │
│  (What signals were present? Did we make the right call?)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ADJUSTMENT                               │
│  (Update signal weights, thresholds, trigger conditions)    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  BETTER FUTURE  │
                    │    DECISIONS    │
                    └─────────────────┘
```

---

## 11. Summary

The Proactive Security Detection System enables agents to:

1. **Automatically assess risk** without explicit user instruction
2. **Detect seriousness signals** across five dimensions (impact, exposure, persistence, sensitivity, reversibility)
3. **Intuitively sense danger** through heuristic pattern recognition
4. **Dynamically activate gates** based on real-time risk assessment
5. **Learn and improve** from each security decision

### Key Principles:

- **Risk is contextual**: The same action can have different risk levels depending on where, when, and how it's done
- **Safety is a spectrum**: Not all tasks need full lockdown; appropriate security is proportionate security
- **Intuition matters**: Pattern recognition and "gut feelings" can detect risks before formal analysis
- **Transparency**: Users should understand why certain gates are active
- **Continuous improvement**: The system learns from every decision to get better over time

### Next Steps for Implementation:

1. Implement signal detection for all five risk dimensions
2. Build the scoring algorithm with configurable weights
3. Create the intuitive detection layer with semantic analysis
4. Develop the dynamic gate controller
5. Establish the learning/feedback loop
6. Test with real-world scenarios across all risk levels

---

**Document Status:** Complete  
**Review Schedule:** Quarterly or after security incidents  
**Author:** Research Subagent  
**Approver:** DGC Architecture Team
