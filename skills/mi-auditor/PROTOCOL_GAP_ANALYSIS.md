# PROTOCOL_GAP_ANALYSIS.md
## AUDITOR-EXPERIMENTER Integration: Implementation Gap Analysis

**Document Version:** 1.0  
**Date:** 2026-02-05  
**Purpose:** Identify gaps between the full AUDITOR-EXPERIMENTER protocol and current mi_auditor implementation

---

## Executive Summary

The current `mi_auditor` skill implements approximately **25-30%** of the full AUDITOR-EXPERIMENTER protocol defined in `AUDITOR_EXPERIMENTER_INTEGRATION.md`. The implementation is primarily a **static audit framework** for evaluating completed MI research claims, while the protocol defines a **dynamic, recursive quality assurance system** with bidirectional flows between AUDITOR (critique/validation) and EXPERIMENTER (design/execution) roles.

**Key Missing Components:**
1. EXPERIMENTER skill entirely absent
2. No message-passing protocol implementation
3. No 6-phase experiment lifecycle management
4. No bidirectional critique-design loops
5. No gap-analysis → follow-up experiment flows
6. No R_V knowledge graph integration

---

## 1. What the Protocol Requires That mi_auditor Doesn't Implement

### 1.1 Core Role Separation

| Protocol Requirement | Current Implementation | Gap |
|---------------------|----------------------|-----|
| **AUDITOR (Maheshwari)** - Critique, validate, identify gaps | Partial - static audit methods only | Missing gap analysis generation, dynamic critique flows |
| **EXPERIMENTER (Mahakali)** - Design, execute, measure | **Completely absent** | No experiment design capability, no execution framework |
| **SYNTHESIS (Mahalakshmi)** - Integrate validated findings | Absent | No knowledge graph updates, no synthesis logic |
| **DOCUMENTATION (Mahasaraswati)** - Document for R_V | Absent | No documentation pipeline |

### 1.2 Message Types (API Contracts)

The protocol defines 6 core message types for inter-skill communication:

| Message Type | Protocol Definition | mi_auditor Status | Gap Severity |
|--------------|--------------------|--------------------|--------------|
| `DesignProposal` | EXPERIMENTER→AUDITOR: Full experiment design with hypothesis, protocol, metrics, controls | ❌ Not implemented | **Critical** |
| `DesignCritique` | AUDITOR→EXPERIMENTER: Critique with verdict, concerns, suggested revisions | ❌ Not implemented | **Critical** |
| `ExecutionReport` | EXPERIMENTER→AUDITOR: Raw data, analysis, claims from experiment run | ❌ Not implemented | **Critical** |
| `ValidationReport` | AUDITOR→EXPERIMENTER: Claim assessments, limitations, follow-up recommendations | ❌ Not implemented | **Critical** |
| `GapAnalysis` | AUDITOR→EXPERIMENTER: Identified gaps, priority ranking, theoretical questions | ❌ Not implemented | **Critical** |
| `FollowUpProposals` | EXPERIMENTER→AUDITOR: Proposed experiments addressing gaps | ❌ Not implemented | **Critical** |

**Current mi_auditor only implements:**
- Static `AuditResult` dataclass (one-way output only)
- No inter-skill message passing
- No async queue support
- No bidirectional communication

### 1.3 Synchronous Operations

| Operation | Protocol Requirement | Current Status |
|-----------|---------------------|----------------|
| `submit_design` | EXPERIMENTER→AUDITOR with 30s timeout | ❌ Not implemented |
| `request_clarification` | AUDITOR→EXPERIMENTER with 60s timeout | ❌ Not implemented |
| `submit_execution` | EXPERIMENTER→AUDITOR with 60s timeout | ❌ Not implemented |
| `request_follow_up` | AUDITOR→EXPERIMENTER with 120s timeout | ❌ Not implemented |
| `emergency_review` | Bidirectional with 15s timeout | ❌ Not implemented |

### 1.4 Asynchronous Channels

| Channel | Protocol Purpose | Current Status |
|---------|-----------------|----------------|
| `design_queue` | Pending designs awaiting critique | ❌ Not implemented |
| `validation_queue` | Pending executions awaiting validation | ❌ Not implemented |
| `gap_queue` | Identified gaps awaiting follow-up designs | ❌ Not implemented |
| `knowledge_stream` | Validated findings for R_V integration | ❌ Not implemented |

---

## 2. The 6-Phase Experiment Lifecycle Gap

### Protocol Lifecycle vs. Current Implementation

```
PROTOCOL                                    CURRENT mi_auditor
────────                                    ────────────────
┌─────────────────┐                         ┌─────────────────┐
│ PHASE 1:        │                         │  (Not           │
│ HYPOTHESIS      │                         │   implemented)  │
│ GENERATION      │                         │                 │
└────────┬────────┘                         └─────────────────┘
         │
         ▼
┌─────────────────┐                         ┌─────────────────┐
│ PHASE 2:        │                         │  Partial:       │
│ DESIGN          │◄────CRITIQUE────►       │  Static audit   │
│ (bidirectional) │    (bidirectional)      │  of existing    │
└────────┬────────┘                         │  claims only    │
         │ (on ACCEPT)                      └─────────────────┘
         ▼
┌─────────────────┐                         ┌─────────────────┐
│ PHASE 3:        │                         │  (Not           │
│ EXECUTION       │                         │   implemented)  │
└────────┬────────┘                         └─────────────────┘
         │
         ▼
┌─────────────────┐                         ┌─────────────────┐
│ PHASE 4:        │                         │  Partial:       │
│ VALIDATION      │◄────CLAIMS──────►       │  Static         │
│ (bidirectional) │   (bidirectional)       │  validation     │
└────────┬────────┘                         └─────────────────┘
         │
         ▼
┌─────────────────┐                         ┌─────────────────┐
│ PHASE 5:        │                         │  (Not           │
│ INTEGRATION     │                         │   implemented)  │
│ (knowledge      │                         │                 │
│  graph update)  │                         │                 │
└────────┬────────┘                         └─────────────────┘
         │
         ▼
┌─────────────────┐                         ┌─────────────────┐
│ PHASE 6:        │                         │  (Not           │
│ GAP ANALYSIS    │◄────FOLLOW-UP───►       │   implemented)  │
│ (recursive)     │   (bidirectional)       │                 │
└─────────────────┘                         └─────────────────┘
```

### Phase-by-Phase Gap Analysis

#### PHASE 1: Hypothesis Generation
**Protocol Requirements:**
- Trigger: Research question or gap identified
- Input: Prior research, observations, or AUDITOR gap identification
- Output: Refined hypothesis H = {claim, mechanism, predicted_outcome}

**Current Gap:**
- ❌ No hypothesis generation framework
- ❌ No structured hypothesis format
- ❌ No mechanism specification
- ❌ No predicted outcome formalization

**Implementation Needed:**
```python
@dataclass
class Hypothesis:
    claim: str
    mechanism: str  # Causal explanation
    predicted_outcome: str
    falsifiability_criteria: List[str]
    prior_evidence: List[str]  # Links to knowledge graph
    
class HypothesisGenerator:
    def generate_from_gap(self, gap: GapAnalysis) -> Hypothesis:
        """Generate hypothesis from identified gap."""
        pass
    
    def generate_from_observation(self, observation: Observation) -> Hypothesis:
        """Generate hypothesis from empirical observation."""
        pass
```

#### PHASE 2: Experiment Design
**Protocol Requirements:**
- EXPERIMENTER designs → AUDITOR critiques → Loop until ACCEPT
- DesignProposal with full protocol specification
- DesignCritique with verdict and suggested revisions
- Multiple iteration cycles supported

**Current Gap:**
- ❌ No experiment design capability (no EXPERIMENTER skill)
- ❌ No design critique as a process (only static post-hoc audit)
- ❌ No iteration loop
- ❌ No conditional acceptance with re-review

**Implementation Needed:**
```python
class ExperimentDesigner:  # EXPERIMENTER role
    def design_experiment(self, hypothesis: Hypothesis) -> DesignProposal:
        """Design experiment to test hypothesis."""
        pass
    
    def revise_design(self, critique: DesignCritique) -> DesignProposal:
        """Revise design based on critique."""
        pass

class DesignCritiquer:  # AUDITOR role enhancement
    def critique_design(self, proposal: DesignProposal) -> DesignCritique:
        """Critique experiment design before execution."""
        pass
    
    def review_revision(self, original: DesignCritique, 
                       revised: DesignProposal) -> DesignCritique:
        """Review revised design."""
        pass
```

#### PHASE 3: Execution
**Protocol Requirements:**
- Trigger: Design approved by AUDITOR
- Actor: EXPERIMENTER executes with monitoring
- Output: ExecutionReport with raw data, analysis, claims
- Track deviations from protocol

**Current Gap:**
- ❌ No EXPERIMENTER skill to execute
- ❌ No execution monitoring
- ❌ No deviation tracking
- ❌ No ExecutionReport generation

**Implementation Needed:**
```python
class ExperimentExecutor:  # EXPERIMENTER role
    def execute_protocol(self, approved_design: DesignProposal) -> ExecutionReport:
        """Execute approved experiment design."""
        pass
    
    def record_deviation(self, step: int, intended: str, 
                        actual: str, reason: str) -> Deviation:
        """Record deviation from protocol."""
        pass
```

#### PHASE 4: Validation
**Protocol Requirements:**
- EXPERIMENTER submits → AUDITOR validates
- ValidationReport with claim assessments, limitations, biases
- Verdict: confirmed | supported | inconclusive | contradicted | invalid
- Follow-up recommendations

**Current Gap:**
- ❌ No ValidationReport data structure
- ❌ No claim-level assessment (only overall audit)
- ❌ No bias identification
- ❌ No replication assessment
- ❌ No follow-up recommendations

**Partial Implementation:**
Current `audit_causal()` method provides basic validation but lacks:
- Structured claim assessments
- Confidence calibration per claim
- Limitations categorization
- Bias identification framework
- Replication requirements specification

**Implementation Needed:**
```python
@dataclass
class ClaimAssessment:
    claim_id: str
    verdict: ValidationVerdict  # confirmed|supported|inconclusive|contradicted
    confidence: float  # 0-1
    rationale: str
    evidence_quality: float
    methodology_validity: float

class ValidationAuditor:  # Enhances current audit_causal()
    def validate_results(self, execution_report: ExecutionReport) -> ValidationReport:
        """Validate execution results."""
        pass
    
    def assess_claim(self, claim: Claim, 
                    evidence: Evidence) -> ClaimAssessment:
        """Assess individual claim."""
        pass
    
    def identify_biases(self, execution: ExecutionReport) -> List[Bias]:
        """Identify potential biases in execution."""
        pass
```

#### PHASE 5: Integration
**Protocol Requirements:**
- Update R_V knowledge graph
- Add validated claim with confidence level
- Link supporting evidence
- Tag for replication status

**Current Gap:**
- ❌ No knowledge graph integration
- ❌ No structured claim storage
- ❌ No evidence linking
- ❌ No confidence tracking over time

**Current Implementation:**
```python
# Current (minimal)
class MIKnowledgeBase:
    def __init__(self):
        self.papers: Dict[str, Paper] = {}  # Minimal paper storage only
```

**Implementation Needed:**
```python
class RVKnowledgeGraph:
    """R_V research knowledge graph for integration."""
    
    def add_validated_claim(self, claim: ValidatedClaim) -> Node:
        """Add validated claim to knowledge graph."""
        pass
    
    def link_evidence(self, claim_id: str, 
                     execution_id: str) -> Edge:
        """Link claim to supporting evidence."""
        pass
    
    def update_confidence(self, claim_id: str, 
                         new_confidence: float) -> None:
        """Update confidence based on new evidence."""
        pass
    
    def flag_for_replication(self, claim_id: str, 
                            priority: str) -> None:
        """Flag claim as needing replication."""
        pass
```

#### PHASE 6: Gap Analysis
**Protocol Requirements:**
- AUDITOR asks: What remains unknown? What assumptions untested?
- EXPERIMENTER designs follow-up
- Returns to Phase 2 (recursive loop)
- Priority ranking of gaps

**Current Gap:**
- ❌ No GapAnalysis message type
- ❌ No systematic gap identification
- ❌ No priority ranking algorithm
- ❌ No follow-up proposal generation

**Implementation Needed:**
```python
@dataclass
class Gap:
    gap_id: str
    description: str
    category: GapCategory  # mechanism|measurement|generalizability|boundary_condition
    blocks_understanding: List[str]
    current_assumptions: List[str]
    priority_score: float  # 0-1

class GapAnalyzer:  # AUDITOR role
    def analyze_gaps(self, validation_report: ValidationReport,
                    current_knowledge: KnowledgeGraph) -> GapAnalysis:
        """Identify gaps from validation."""
        pass
    
    def rank_priorities(self, gaps: List[Gap]) -> List[Gap]:
        """Rank gaps by priority."""
        pass

class FollowUpDesigner:  # EXPERIMENTER role
    def design_follow_up(self, gap_analysis: GapAnalysis) -> FollowUpProposals:
        """Design experiments to address identified gaps."""
        pass
```

---

## 3. API Contracts Gap Analysis

### 3.1 DesignProposal (Not Implemented)

**Protocol Schema:**
```json
{
  "message_type": "DesignProposal",
  "version": "1.0",
  "timestamp": "ISO-8601",
  "proposal_id": "uuid",
  "hypothesis": {
    "claim": "string",
    "mechanism": "string",
    "predicted_outcome": "string",
    "falsifiability_criteria": ["string"]
  },
  "protocol": {
    "name": "string",
    "type": "simulation|synthetic|naturalistic|intervention",
    "steps": [...],
    "termination_conditions": ["string"]
  },
  "metrics": {
    "primary": {...},
    "secondary": [...],
    "controls": [...]
  },
  "resources": {...},
  "risk_assessment": {...}
}
```

**Current Gap:**
- ❌ No DesignProposal dataclass
- ❌ No protocol step specification
- ❌ No termination conditions
- ❌ No resource estimation
- ❌ No risk assessment

### 3.2 DesignCritique (Not Implemented)

**Protocol Schema:**
```json
{
  "message_type": "DesignCritique",
  "verdict": "accept|accept_with_revisions|reject|reject_resubmission",
  "validity_assessment": {
    "epistemic_validity": {"score": "0.0-1.0", "rationale": "string"},
    "methodological_rigor": {"score": "0.0-1.0", "rationale": "string"},
    "r_v_alignment": {"score": "0.0-1.0", "rationale": "string"}
  },
  "concerns": [...],
  "questions": [...],
  "suggested_revisions": [...],
  "conditional_acceptance": {...}
}
```

**Current Gap:**
- ❌ No structured validity assessment (3 dimensions)
- ❌ No concern categorization (critical|major|minor)
- ❌ No question-asking capability
- ❌ No suggested revisions with current/proposed comparison
- ❌ No conditional acceptance framework

### 3.3 ExecutionReport (Not Implemented)

**Protocol Schema:**
```json
{
  "message_type": "ExecutionReport",
  "execution_metadata": {
    "start_time": "ISO-8601",
    "end_time": "ISO-8601",
    "status": "completed|partial|failed|aborted",
    "deviations_from_protocol": [...]
  },
  "data": {
    "raw_data_location": "path|uri",
    "checksum": "string",
    "samples": [...]
  },
  "analysis": {
    "statistical_tests": [...],
    "anomalies_detected": [...]
  },
  "claims": [...],
  "raw_observations": ["string"]
}
```

**Current Gap:**
- ❌ No execution metadata tracking
- ❌ No deviation logging
- ❌ No data provenance (checksums, URIs)
- ❌ No anomaly detection
- ❌ No structured claim generation

### 3.4 ValidationReport (Not Implemented)

**Protocol Schema:**
```json
{
  "message_type": "ValidationReport",
  "overall_assessment": {
    "verdict": "confirmed|supported|inconclusive|contradicted|invalid",
    "confidence": "0.0-1.0",
    "summary": "string"
  },
  "claim_assessments": [...],
  "limitations": [...],
  "biases_identified": [...],
  "replication_assessment": {...},
  "follow_up_recommendations": [...],
  "r_v_implications": {...}
}
```

**Current Gap:**
- ❌ No overall assessment structure
- ❌ No per-claim validation (current only audits overall)
- ❌ No limitations categorization (sample_size|methodology|generalizability|measurement)
- ❌ No bias identification framework
- ❌ No replication assessment
- ❌ No R_V implications tracking

### 3.5 GapAnalysis (Not Implemented)

**Protocol Schema:**
```json
{
  "message_type": "GapAnalysis",
  "context": {
    "current_knowledge_state": "string",
    "recent_validations": ["execution_id"],
    "knowledge_graph_version": "string"
  },
  "identified_gaps": [...],
  "priority_ranking": [...],
  "theoretical_questions": [...]
}
```

**Current Gap:**
- ❌ No context tracking
- ❌ No gap identification system
- ❌ No priority ranking algorithm
- ❌ No theoretical question generation

### 3.6 FollowUpProposals (Not Implemented)

**Protocol Schema:**
```json
{
  "message_type": "FollowUpProposals",
  "proposed_experiments": [...],
  "alternative_approaches": [...],
  "knowledge_gain_prediction": {...}
}
```

**Current Gap:**
- ❌ No follow-up experiment proposal generation
- ❌ No alternative approach enumeration
- ❌ No knowledge gain prediction

---

## 4. Decision Trees Gap Analysis

### 4.1 When to Invoke AUDITOR

**Protocol Decision Tree:**
```
START: Need quality assurance?
    ├──► Is this a DESIGN decision?
    │       YES ──► Does the design affect R_V measurement?
    │              YES ──► INVOKE AUDITOR (design critique)
    │              NO ──► Is there significant resource commitment?
    │                     YES ──► INVOKE AUDITOR (risk assessment)
    │                     NO ──► EXPERIMENTER proceeds independently
    ├──► Is this a RESULTS interpretation?
    │       YES ──► Does the result make a CLAIM about R_V?
    │              YES ──► INVOKE AUDITOR (validation required)
    │              NO ──► Is the result surprising or anomalous?
    │                     YES ──► INVOKE AUDITOR (anomaly check)
    │                     NO ──► EXPERIMENTER documents independently
    ├──► Is this a KNOWLEDGE integration?
    │       YES ──► AUDITOR must validate before integration
    └──► EXPERIMENTER proceeds with standard documentation
```

**Current Gap:**
- ❌ No decision tree implementation
- ❌ No automatic invocation triggers
- ❌ No R_V relevance checking
- ❌ No resource commitment assessment
- ❌ No anomaly detection triggers

### 4.2 When to Invoke EXPERIMENTER

**Protocol Decision Tree:**
```
START: Need empirical investigation?
    ├──► Is there an UNTESTED HYPOTHESIS?
    │       YES ──► Has it been critiqued?
    │              YES ──► INVOKE EXPERIMENTER (execute validated design)
    │              NO ──► AUDITOR must critique first
    ├──► Has AUDITOR identified a GAP?
    │       YES ──► Is the gap addressable through experiment?
    │              YES ──► INVOKE EXPERIMENTER (design follow-up)
    │              NO ──► Flag for theoretical analysis
    ├──► Is there a VALIDATION requirement from prior work?
    │       YES ──► INVOKE EXPERIMENTER (replication or extension)
    └──► No experiment needed; proceed with theoretical work
```

**Current Gap:**
- ❌ No EXPERIMENTER skill exists
- ❌ No gap→experiment trigger
- ❌ No hypothesis critique checking
- ❌ No validation requirement tracking

### 4.3 Arbitration Rules (Not Implemented)

**Protocol Requirements:**
- Validity vs Feasibility conflicts → AUDITOR has authority over validity, EXPERIMENTER over feasibility
- Evidence interpretation → Split authority by domain
- Risk tolerance → Conservative default (AUDITOR's assessment takes precedence)
- Unresolvable → Escalate to human (Dhyana)

**Current Gap:**
- ❌ No conflict detection
- ❌ No arbitration framework
- ❌ No escalation mechanism

### 4.4 Experiment Priority Scoring (Not Implemented)

**Protocol Formula:**
```
Priority Score = (Knowledge_Gap × Reversibility × R_V_Relevance) / Effort

Knowledge_Gap:
    1.0 = Fundamental assumption untested
    0.7 = Important mechanism unclear
    0.4 = Refinement of known result
    0.1 = Confirmation/replication

Reversibility:
    1.0 = Fully reversible
    0.7 = Correctable with effort
    0.4 = Significant cost
    0.1 = Irreversible/high harm

R_V_Relevance:
    1.0 = Direct R_V measurement
    0.8 = Mechanism underlying R_V
    0.5 = Boundary condition for R_V
    0.2 = General consciousness research
    0.1 = Tool development

Priority Thresholds:
    Score ≥ 0.8: Execute immediately
    Score 0.5-0.8: Queue for next cycle
    Score 0.3-0.5: Deprioritize
    Score < 0.3: Archive
```

**Current Gap:**
- ❌ No priority scoring algorithm
- ❌ No experiment queue management
- ❌ No resource allocation logic

---

## 5. Specific Code Structures Needed

### 5.1 New Skills Required

#### mi_experimenter (New Skill)
```python
# skills/mi_experimenter/__init__.py

class MIExperimenter:
    """
    EXPERIMENTER skill (Mahakali mode) - Design and execute experiments.
    """
    
    def design_experiment(self, hypothesis: Hypothesis) -> DesignProposal:
        """Design experiment to test hypothesis."""
        pass
    
    def revise_design(self, proposal: DesignProposal, 
                     critique: DesignCritique) -> DesignProposal:
        """Revise design based on AUDITOR critique."""
        pass
    
    def execute_protocol(self, approved_design: DesignProposal) -> ExecutionReport:
        """Execute approved experiment design."""
        pass
    
    def propose_follow_up(self, gap_analysis: GapAnalysis) -> FollowUpProposals:
        """Propose experiments to address identified gaps."""
        pass
    
    def calculate_priority_score(self, proposal: DesignProposal) -> float:
        """Calculate experiment priority score."""
        pass
```

#### mi_orchestrator (New Skill - Optional)
```python
# skills/mi_orchestrator/__init__.py

class MIOrchestrator:
    """
    Orchestrates AUDITOR-EXPERIMENTER interactions.
    """
    
    def run_experiment_lifecycle(self, hypothesis: Hypothesis) -> ValidatedClaim:
        """Run full 6-phase experiment lifecycle."""
        pass
    
    def handle_design_critique_loop(self, proposal: DesignProposal) -> DesignProposal:
        """Handle design→critique→revision loop."""
        pass
    
    def handle_validation(self, execution: ExecutionReport) -> ValidationReport:
        """Handle execution→validation flow."""
        pass
    
    def handle_gap_follow_up(self, validation: ValidationReport) -> List[DesignProposal]:
        """Handle gap→follow-up experiment flow."""
        pass
```

### 5.2 mi_auditor Enhancements Required

#### New Methods for MIAuditor Class
```python
class MIAuditor:
    # Existing methods: audit_statistical, audit_causal, audit_cross_arch
    
    # NEW: Protocol methods
    def critique_design(self, proposal: DesignProposal) -> DesignCritique:
        """
        Critique experiment design before execution.
        Returns DesignCritique with verdict and suggested revisions.
        """
        pass
    
    def validate_results(self, execution: ExecutionReport) -> ValidationReport:
        """
        Validate execution results.
        Returns ValidationReport with claim assessments and limitations.
        """
        pass
    
    def analyze_gaps(self, validation: ValidationReport) -> GapAnalysis:
        """
        Identify gaps from validation.
        Returns GapAnalysis with priority-ranked gaps.
        """
        pass
    
    def check_design_validity(self, proposal: DesignProposal) -> ValidityAssessment:
        """
        Check 3 dimensions of validity:
        - epistemic_validity
        - methodological_rigor
        - r_v_alignment
        """
        pass
```

#### New Dataclasses
```python
# Message types for API contracts

@dataclass
class DesignProposal:
    message_type: str = "DesignProposal"
    version: str = "1.0"
    timestamp: str
    proposal_id: str
    hypothesis: Hypothesis
    protocol: Protocol
    metrics: Metrics
    resources: Resources
    risk_assessment: RiskAssessment

@dataclass
class DesignCritique:
    message_type: str = "DesignCritique"
    version: str = "1.0"
    timestamp: str
    proposal_id: str
    verdict: Verdict  # accept|accept_with_revisions|reject|reject_resubmission
    validity_assessment: ValidityAssessment
    concerns: List[Concern]
    questions: List[Question]
    suggested_revisions: List[Revision]
    conditional_acceptance: Optional[ConditionalAcceptance]

@dataclass
class ExecutionReport:
    message_type: str = "ExecutionReport"
    version: str = "1.0"
    timestamp: str
    execution_id: str
    proposal_id: str
    execution_metadata: ExecutionMetadata
    data: DataPackage
    analysis: Analysis
    claims: List[Claim]
    raw_observations: List[str]

@dataclass
class ValidationReport:
    message_type: str = "ValidationReport"
    version: str = "1.0"
    timestamp: str
    execution_id: str
    overall_assessment: OverallAssessment
    claim_assessments: List[ClaimAssessment]
    limitations: List[Limitation]
    biases_identified: List[Bias]
    replication_assessment: ReplicationAssessment
    follow_up_recommendations: List[Recommendation]
    r_v_implications: RVImplications

@dataclass
class GapAnalysis:
    message_type: str = "GapAnalysis"
    version: str = "1.0"
    timestamp: str
    analysis_id: str
    context: KnowledgeContext
    identified_gaps: List[Gap]
    priority_ranking: List[PriorityRankedGap]
    theoretical_questions: List[TheoreticalQuestion]

@dataclass
class FollowUpProposals:
    message_type: str = "FollowUpProposals"
    version: str = "1.0"
    timestamp: str
    analysis_id: str
    proposed_experiments: List[ExperimentBrief]
    alternative_approaches: List[AlternativeApproach]
    knowledge_gain_prediction: KnowledgeGainPrediction
```

### 5.3 Knowledge Graph Integration

```python
# skills/mi_auditor/knowledge_graph.py

class RVKnowledgeGraph:
    """
    R_V research knowledge graph for storing validated claims.
    """
    
    def __init__(self, graph_path: Optional[str] = None):
        self.graph = nx.DiGraph() if graph_path is None else self._load(graph_path)
    
    def add_node(self, node_type: NodeType, properties: Dict) -> str:
        """Add node to knowledge graph."""
        pass
    
    def add_edge(self, source: str, target: str, 
                 edge_type: EdgeType, properties: Dict) -> str:
        """Add edge between nodes."""
        pass
    
    def add_validated_claim(self, validation: ValidationReport) -> str:
        """Add validated claim from validation report."""
        pass
    
    def update_confidence(self, claim_id: str, 
                         new_confidence: float,
                         evidence: str) -> None:
        """Update confidence based on new evidence."""
        pass
    
    def query_by_confidence(self, min_confidence: float) -> List[Node]:
        """Query claims by confidence threshold."""
        pass
    
    def query_by_topic(self, topic: str) -> List[Node]:
        """Query claims by topic."""
        pass
    
    def find_gaps(self) -> List[Gap]:
        """Identify gaps in knowledge graph."""
        pass
```

### 5.4 Async Communication Layer

```python
# skills/mi_auditor/communication.py

from asyncio import Queue

class AuditorExperimenterBus:
    """
    Async communication bus between AUDITOR and EXPERIMENTER.
    """
    
    def __init__(self):
        self.design_queue: Queue[DesignProposal] = Queue()
        self.validation_queue: Queue[ExecutionReport] = Queue()
        self.gap_queue: Queue[GapAnalysis] = Queue()
        self.knowledge_stream: Queue[ValidatedClaim] = Queue()
    
    async def submit_design(self, proposal: DesignProposal, 
                           timeout: float = 30.0) -> DesignCritique:
        """Submit design for critique with timeout."""
        pass
    
    async def submit_execution(self, execution: ExecutionReport,
                              timeout: float = 60.0) -> ValidationReport:
        """Submit execution for validation with timeout."""
        pass
    
    async def request_follow_up(self, gaps: GapAnalysis,
                               timeout: float = 120.0) -> FollowUpProposals:
        """Request follow-up designs with timeout."""
        pass
    
    async def emergency_review(self, issue: str,
                              timeout: float = 15.0) -> ReviewResponse:
        """Emergency review with short timeout."""
        pass
```

---

## 6. Implementation Roadmap

### Phase 1: Core Data Structures (Priority: CRITICAL)
- [ ] Implement all 6 message type dataclasses
- [ ] Implement supporting dataclasses (Hypothesis, Protocol, Metrics, etc.)
- [ ] Define enums (Verdict, GapCategory, LimitationType, etc.)
- [ ] Unit tests for serialization/deserialization

### Phase 2: mi_experimenter Skill (Priority: CRITICAL)
- [ ] Create mi_experimenter skill scaffold
- [ ] Implement experiment design framework
- [ ] Implement protocol execution framework
- [ ] Integration tests with mi_auditor

### Phase 3: mi_auditor Protocol Methods (Priority: HIGH)
- [ ] Implement `critique_design()` method
- [ ] Implement `validate_results()` method
- [ ] Implement `analyze_gaps()` method
- [ ] Implement `check_design_validity()` method

### Phase 4: Knowledge Graph (Priority: HIGH)
- [ ] Implement RVKnowledgeGraph class
- [ ] Define node types and edge types
- [ ] Implement query methods
- [ ] Integration with validation workflow

### Phase 5: Communication Layer (Priority: MEDIUM)
- [ ] Implement AuditorExperimenterBus
- [ ] Implement async queues
- [ ] Implement timeout handling
- [ ] Implement message routing

### Phase 6: Decision Trees & Orchestration (Priority: MEDIUM)
- [ ] Implement invocation decision trees
- [ ] Implement arbitration rules
- [ ] Implement priority scoring algorithm
- [ ] Implement escalation to human

### Phase 7: Full Lifecycle Integration (Priority: LOW)
- [ ] Implement 6-phase lifecycle orchestration
- [ ] Implement loop handling (design→critique→revision)
- [ ] Implement recursive gap→follow-up flows
- [ ] End-to-end integration tests

---

## 7. Summary Table: Protocol vs. Implementation

| Component | Protocol Required | mi_auditor Status | Gap Severity |
|-----------|------------------|-------------------|--------------|
| **ROLES** |
| AUDITOR (critique/validate) | ✅ Required | 🟡 Partial | Medium |
| EXPERIMENTER (design/execute) | ✅ Required | ❌ Missing | **Critical** |
| SYNTHESIS (integrate) | ✅ Required | ❌ Missing | High |
| DOCUMENTATION (document) | ✅ Required | ❌ Missing | Medium |
| **MESSAGE TYPES** |
| DesignProposal | ✅ Required | ❌ Missing | **Critical** |
| DesignCritique | ✅ Required | ❌ Missing | **Critical** |
| ExecutionReport | ✅ Required | ❌ Missing | **Critical** |
| ValidationReport | ✅ Required | ❌ Missing | **Critical** |
| GapAnalysis | ✅ Required | ❌ Missing | **Critical** |
| FollowUpProposals | ✅ Required | ❌ Missing | **Critical** |
| **LIFECYCLE PHASES** |
| Phase 1: Hypothesis Generation | ✅ Required | ❌ Missing | High |
| Phase 2: Design (bidirectional) | ✅ Required | 🟡 Partial | High |
| Phase 3: Execution | ✅ Required | ❌ Missing | **Critical** |
| Phase 4: Validation (bidirectional) | ✅ Required | 🟡 Partial | Medium |
| Phase 5: Integration | ✅ Required | ❌ Missing | High |
| Phase 6: Gap Analysis (recursive) | ✅ Required | ❌ Missing | High |
| **COMMUNICATION** |
| Synchronous operations | ✅ Required | ❌ Missing | High |
| Async channels/queues | ✅ Required | ❌ Missing | High |
| Timeout handling | ✅ Required | ❌ Missing | Medium |
| **DECISION LOGIC** |
| When to invoke AUDITOR | ✅ Required | ❌ Missing | Medium |
| When to invoke EXPERIMENTER | ✅ Required | ❌ Missing | Medium |
| Arbitration rules | ✅ Required | ❌ Missing | Medium |
| Priority scoring | ✅ Required | ❌ Missing | Low |
| **KNOWLEDGE** |
| R_V knowledge graph | ✅ Required | ❌ Missing | High |
| Claim confidence tracking | ✅ Required | ❌ Missing | Medium |
| Evidence linking | ✅ Required | ❌ Missing | Medium |
| Gap identification | ✅ Required | ❌ Missing | High |

**Legend:**
- ✅ Required: Protocol mandates this component
- 🟡 Partial: Partially implemented
- ❌ Missing: Not implemented
- **Critical**: Blocks basic protocol functionality
- High: Significant functionality gap
- Medium: Moderate functionality gap
- Low: Nice-to-have functionality

---

## 8. Contemplative-Geometric Bridge Status

The "contemplative-geometric bridge" described in the protocol represents the integration of:

1. **Contemplative (Maheshwari/AUDITOR)**: Wisdom, wideness, calm critique
2. **Geometric (Mahakali/EXPERIMENTER)**: Force, action, measurement
3. **Bridge (Integration)**: Recursive quality assurance through bidirectional flows

### Current Status:
```
Contemplative (AUDITOR)    Geometric (EXPERIMENTER)
        🟡                           ❌
    (25% complete)             (0% complete)
         \                         /
          \                       /
           \                     /
            \                   /
             \                 /
              \               /
               \             /
                \           /
                 \         /
                  \       /
                   \     /
                    \   /
                     \ /
                      🔴
               CONTEMPLATIVE-GEOMETRIC
                     BRIDGE
                  (NOT OPERATIONAL)
```

### To Complete the Bridge:
1. **Complete AUDITOR implementation** (75% remaining)
2. **Build EXPERIMENTER skill** (100% needed)
3. **Implement communication layer** (100% needed)
4. **Deploy knowledge graph** (100% needed)
5. **Implement orchestration logic** (100% needed)

---

*Analysis compiled: 2026-02-05*  
*Protocol version: AUDITOR_EXPERIMENTER_INTEGRATION.md v1.0*  
*Current implementation: mi_auditor v5.1*
