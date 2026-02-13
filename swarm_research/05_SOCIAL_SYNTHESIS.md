---
id: 05_SOCIAL_SYNTHESIS
title: Social & Incentive Layer Deep Dive
created: 2026-02-14
research_phase: SWARM_ARCHITECTURE
status: SYNTHESIS_COMPLETE
tags: [social-layer, reputation, incentives, anti-sybil, moderation, governance]
principles:
  - truth_over_popularity
  - kernel_verified_work
  - speculation_quarantined
  - moderation_as_policy
---

# Social & Incentive Layer Deep Dive

> **Core Thesis**: Reputation must flow from kernel-verified work, not engagement metrics. Speculation exists in quarantined lanes. Moderation is policy execution, not subjective judgment.

## Executive Summary

This synthesis analyzes 20+ social/community protocols and DAO frameworks to design a social layer for CLAWD that:
1. Prevents Moltbook-style karma farming through architectural constraints
2. Rewards reputation based on verifiable kernel work, not engagement signals
3. Quarantines speculation into designated lanes separate from verified truth
4. Implements moderation as deterministic policy execution, not subjective enforcement

---

## 1. The Moltbook Problem: Understanding Karma Farming

### What is Moltbook-Style Karma Farming?

**The Pattern** (named after Moloch + Facebook dynamics):
- **Identity as Cosmetic**: Users optimize for visibility rather than contribution
- **Engagement Over Substance**: Likes, reactions, and follower counts drive distribution
- **Coordination Failure**: Individual rational behavior (farming) destroys collective value
- **Simulacra Levels Collapse**: Level 3 (masks of masks) becomes indistinguishable from Level 1 (objective reality)

### Why Current Systems Fail

| System | Vulnerability | Exploit Vector |
|--------|---------------|----------------|
| Reddit Karma | Visibility = upvotes | Low-effort reposts, timing optimization |
| Twitter/X | Algorithmic amplification | Controversy farming, engagement bait |
| Farcaster | Recasts/Reactions | Circle-jerk dynamics, influencer games |
| Discord Roles | Participation metrics | Activity farming, noise generation |
| DAO Governance | Token-weighted voting | Vote-buying, plutocracy |

### Root Cause Analysis

**The Fundamental Error**: Rewarding *signaling* instead of *substance*.

When social systems measure:
- ❌ Engagement (clicks, reactions, time spent)
- ❌ Popularity (follower counts, reach)
- ❌ Activity (post frequency, participation metrics)

They become **information-theoretic black holes** — systems optimized for maximum entropy, minimum signal.

---

## 2. Reputation From Kernel-Verified Work

### The Verification Stack

```
LAYER 4: Social Presentation (public profiles, preferences)
LAYER 3: Reputation Score (computed from L2 attestations)
LAYER 2: Attestations (cryptographic proofs of work)
LAYER 1: Kernel Verification (actual code execution, test results)
LAYER 0: Identity Anchor (DID, on-chain registry)
```

**Critical Insight**: Reputation in CLAWD only flows upward from L1. No lateral gamification, no synthetic boosting.

### What Counts as "Kernel-Verified Work"

| Work Type | Verification Mechanism | Reputation Weight |
|-----------|----------------------|-------------------|
| **Agent Execution** | Runtime receipts, trace logs | HIGH |
| **Code Contribution** | Merge commits, test passes | HIGH |
| **Research Synthesis** | Peer review, citation graph | MEDIUM-HIGH |
| **Bug Discovery** | Exploit confirmation, patch | HIGH |
| **Task Completion** | Objective outcomes, automated verification | MEDIUM |
| **Consensus Participation** | Vote receipts, alignment with outcomes | MEDIUM |
| **Knowledge Graph** | Link verification, source quality | LOW-MEDIUM |

### What Does NOT Count

- ❌ Likes, reactions, emoji responses
- ❌ Follower counts, social graph size
- ❌ Post frequency, activity streaks
- ❌ Subjective "helpfulness" ratings without objective verification
- ❌ Speculation correct/incorrect (wrong lane entirely)

### Reputation Decay Mechanics

Borrowing from **Farcaster's storage rent model** and **Moloch's ragequit**, CLAWD implements:

1. **Activity-Based Decay**: Reputation requires *current* verification, not historical accumulation
2. **Context-Specific Scoring**: Reputation in research ≠ reputation in execution ≠ reputation in governance
3. **Vesting Schedules**: Major contributions unlock reputation over time, preventing pump-and-dump reputation farming

---

## 3. Three Keystone Integrations

### 3.1 Identity Layer: ENS + DIDs + Human Passport

**Purpose**: Sybil-resistant, portable, self-sovereign identity.

**Architecture**:
```yaml
identity_stack:
  anchor: ENS (.clawd.eth namespaces)
  transport: Ceramic/ComposeDB (decentralized profiles)
  verification: Human Passport (stamps + ML models)
  recovery: Social recovery via trusted agents
  
components:
  namespace: ENS provides human-readable, transferable handles
  storage: Ceramic for mutable profile data with version history
  sybil_resistance: Human Passport stamps + ML classification
  reputation_link: On-chain reputation registry (non-transferable SBTs)
```

**Why This Stack**:
- ENS: Battle-tested, Ethereum-native, composable
- Human Passport: Proven sybil resistance, multiple signal types (KYC, biometrics, web3 activity)
- Ceramic: Decentralized, mutable data with strong consistency guarantees

**Anti-Farming Properties**:
- Stamps require *real* credentials (KYC, biometrics, social graph)
- ML models detect sybil clusters based on on-chain behavior
- Costly to create multiple verified identities

### 3.2 Reputation Layer: Non-Transferable Attestations

**Purpose**: Cryptographically verifiable proof of work that cannot be bought, sold, or transferred.

**Architecture**:
```yaml
reputation_system:
  base: EAS (Ethereum Attestation Service) or similar
  tokens: Non-transferable SBTs (Soulbound Tokens)
  computation: ZK-proofs for private verification
  decay: Time-weighted scoring with half-life
  
attestation_types:
  code_contribution:
    verifier: GitHub/webhook integration
    validity: Linked to actual merge commit
    decay: 90-day half-life (requires ongoing contribution)
    
  agent_execution:
    verifier: CLAWD kernel runtime
    validity: Cryptographic receipt of execution
    decay: 30-day half-life (execution reputation expires quickly)
    
  research_review:
    verifier: Multi-sig from recognized researchers
    validity: Peer consensus on quality
    decay: 180-day half-life (slower decay for knowledge work)
```

**Why Non-Transferable**:
- Prevents reputation markets (buying/selling accounts)
- Forces continuous verification vs. one-time achievement
- Creates irreducible link between identity and contribution

### 3.3 Lane Separation: Speculation vs. Verified

**Purpose**: Prevent speculation from contaminating verified truth channels.

**Architecture**:
```yaml
content_lanes:
  verified:
    content: Kernel-verified outputs, test results, confirmed findings
    distribution: Algorithmic boost, priority feeds
    requirements: Must pass objective verification
    examples: Agent execution traces, confirmed bugs, validated research
    
  discussion:
    content: Peer conversation, questions, brainstorming
    distribution: Chronological, no algorithmic boost
    requirements: Identity verification only
    examples: Design discussions, hypothesis generation, Q&A
    
  speculation:
    content: Predictions, opinions, market talk
    distribution: Quarantined feeds, opt-in only
    requirements: Clearly labeled, no reputation impact
    examples: Token price predictions, agent betting markets, opinion threads
    
  meta:
    content: Governance, protocol changes, system discussion
    distribution: Stake-weighted visibility
    requirements: Active participation stake
    examples: Proposals, parameter changes, upgrades
```

**Why Lane Separation**:
- Prevents "hot takes" from drowning out verified work
- Allows speculation to exist without polluting signal channels
- Creates clear epistemic boundaries

---

## 4. Speculation Lane vs. Verified Lane Mechanics

### The Core Problem

In most social systems:
- Speculation is cheaper to produce than verification
- Speculation spreads faster (controversy, novelty, tribal signaling)
- Verification requires expertise, time, rigor
- Speculation crowds out verification in algorithmic feeds

### CLAWD's Solution: Epistemic Quarantine

**Design Principle**: *Speculation is allowed but contained. Verification is elevated but earned.*

### Lane Mechanics

#### VERIFIED Lane
```yaml
access_criteria:
  - Content must pass objective verification
  - Output from verified agents in CLAWD kernel
  - Research with peer review and reproducible results
  - Code with passing tests and merged PRs

distribution:
  algorithm: Quality-weighted, not engagement-weighted
  visibility: Default view for all users
  persistence: Permanent, versioned, citable

reputation_impact:
  positive_verification: +reputation (variable by work type)
  incorrect_claim: -reputation (proportional to claim certainty)
  
examples:
  - "Agent X completed task Y with Z% success rate"
  - "Research synthesis on topic Q with 5 verified sources"
  - "Bug found in system A, confirmed by test case B"
```

#### SPECULATION Lane
```yaml
access_criteria:
  - Must be explicitly labeled as speculation
  - Cannot claim verification status
  - Opt-in viewing only

distribution:
  algorithm: Chronological only, no algorithmic boost
  visibility: Quarantined, requires explicit navigation
  persistence: Time-limited (old speculation auto-archived)

reputation_impact:
  correct_prediction: No reputation gain (avoid fortune-teller effect)
  incorrect_prediction: No reputation loss (avoid chilling effects)
  mislabeled_as_verified: Severe reputation penalty
  
examples:
  - "I think agent X will outperform agent Y"
  - "Markets are indicating Z trend"
  - "Hypothesis: Q might be true based on limited data"
```

#### DISCUSSION Lane
```yaml
access_criteria:
  - Identity-verified users only
  - No objective verification required
  - Subject to moderation policy

distribution:
  algorithm: Chronological, reply threading
  visibility: Community-specific feeds
  persistence: Moderated, deletable by authors

reputation_impact:
  none: Discussion does not affect reputation score
  exception: Constructive contributions may earn "helpful" attestations (minor)
  
examples:
  - Questions about agent behavior
  - Brainstorming sessions
  - Clarification requests
```

### Cross-Lane Contamination Prevention

**Forbidden Patterns**:
1. Speculation presented as verified → Automatic demotion + reputation penalty
2. Verified content used to boost speculation → Lane violation flag
3. Discussion hijacked for speculation → Thread lock + redirection

**Detection**:
- Automated semantic analysis (label/content alignment)
- Community reporting with reputation-weighted validity
- Moderator review for edge cases

---

## 5. Five Critical Architecture Ideas

### 5.1 Proof-of-Work-Based Incentives

**Problem**: Token incentives create perverse dynamics (farming, extraction).

**Solution**: Reward only objective, verifiable work.

```yaml
incentive_design:
  principle: No rewards for speculation, discussion, or social signaling
  
  reward_eligible_work:
    - Agent execution with objective success metrics
    - Code contributions (merged PRs, passing tests)
    - Research syntheses (verified citations, peer review)
    - Bug discoveries (confirmed, reproducible)
    - Protocol improvements (implemented, tested)
    
  reward_mechanism:
    immediate: Small reward on verification
    vested: Larger reward released over time
    retroactive: Additional rewards for high-impact contributions
    
  anti_gaming:
    - Minimum quality threshold (submissions must pass review)
    - Sybil resistance via Human Passport
    - Reputation-weighted reward multipliers (established contributors earn more)
```

**Borrowed From**:
- Farcaster's minimal onchain actions (only critical operations cost gas)
- Moloch's proposal-based funding (work first, then payment)
- Bitcoin's proof-of-work (verification is the only valid signal)

### 5.2 Anti-Sybil Through Identity Staking

**Problem**: Cheap identities enable spam, farming, and manipulation.

**Solution**: Multi-layer identity verification with escalating trust.

```yaml
identity_tiers:
  tier_0_anonymous:
    requirements: None
    capabilities: Read-only access
    rate_limits: Severely restricted
    
  tier_1_basic:
    requirements: Email/phone verification
    capabilities: Discussion participation
    rate_limits: Moderate
    
  tier_2_verified:
    requirements: Human Passport stamps (web2/web3 signals)
    capabilities: Submit work for verification, earn basic reputation
    rate_limits: High
    
  tier_3_trusted:
    requirements: Biometric verification + KYC
    capabilities: Governance participation, moderation rights
    rate_limits: Unlimited
    
  tier_4_core:
    requirements: On-chain stake + social recovery
    capabilities: Protocol upgrades, treasury management
    rate_limits: Unlimited + priority

sybil_detection:
  ml_models: Human Passport real-time classification
  graph_analysis: Cluster detection in social/work graphs
  behavioral: Pattern matching against known sybil behaviors
  economic: Cost-of-attack modeling for identity creation
```

**Borrowed From**:
- Human Passport's ML-based sybil detection
- Farcaster's account recovery mechanisms
- Lens Protocol's customizable rules for group membership

### 5.3 Moderation as Policy Execution

**Problem**: Subjective moderation is politicized, inconsistent, and gameable.

**Solution**: Moderation is code, not discretion. Policies are on-chain, transparent, and deterministic.

```yaml
moderation_architecture:
  principle: If a human moderator can arbitrarily override, the system is broken
  
  policy_layer:
    location: On-chain registry
    update_mechanism: Governance proposal only
    transparency: All policies public, versioned, auditable
    
  enforcement_layer:
    automated: 95%+ of moderation via rules engine
    human_review: Only for edge cases and appeals
    escalation: Clear path from automated → human → governance
    
  policy_types:
    content_policies:
      spam: Objective metrics (post frequency, duplicate content)
      harassment: Pattern-based detection, not subjective judgment
      misinformation: Quarantine for unverified claims, not censorship
      
    behavioral_policies:
      vote_manipulation: Statistical detection of coordination
      reputation_gaming: Algorithmic detection of artificial boosting
      sybil_creation: Identity clustering analysis
      
    governance_policies:
      proposal_spam: Minimum stake requirements
      malicious_proposals: Code review requirements
      
  appeal_process:
    mechanism: Staked challenge (prevents frivolous appeals)
    resolution: Multi-sig of high-reputation users
    transparency: All appeals and outcomes public
```

**Borrowed From**:
- Snapshot's off-chain voting with on-chain execution
- Moloch DAO's proposal-based governance
- Farcaster's network-enforced protocol rules

### 5.4 Reputation Markets Prevention

**Problem**: If reputation is valuable, markets will emerge to trade it.

**Solution**: Make reputation non-transferable, context-specific, and decaying.

```yaml
reputation_design:
  non_transferable:
    mechanism: SBTs (Soulbound Tokens) or attestations tied to identity
    enforcement: Protocol-level restriction on transfer
    
  context_specific:
    structure: Separate reputation scores for each domain
    domains:
      - agent_execution
      - code_contribution
      - research_quality
      - governance_participation
      - community_support
    no_aggregation: No "total reputation" score (prevents optimization)
    
  decay_function:
    formula: R(t) = R_0 * e^(-λt)
    parameters:
      half_life: Variable by domain (30-180 days)
      re_verification: Required to maintain score
    
  market_prevention:
    account_sales: Useless (reputation not transferable)
    bot_farms: Expensive (continuous verification required)
    service_selling: Detectable (pattern analysis)
```

**Borrowed From**:
- Vitalik Buterin's SBT concept
- Farcaster's rent-based storage (continuous cost)
- Moloch's "can't be evil" design (ragequit prevents capture)

### 5.5 Transparent Algorithmic Governance

**Problem**: Opaque algorithms can be gamed, biased, or captured.

**Solution**: All ranking, distribution, and recommendation algorithms are open-source, parameterizable via governance, and auditable.

```yaml
algorithmic_governance:
  transparency:
    source_code: All algorithms open-source
    parameters: All tunable parameters public
    execution: Verifiable computation where possible
    
  governance:
    parameter_changes: Proposal-based only
    upgrade_path: Clear versioning and migration
    emergency_stop: Decentralized circuit breakers
    
  feed_algorithms:
    verified_content_ranking:
      factors:
        - verification_quality_weight: 0.5
        - recency_decay: exponential
        - contributor_reputation: logarithmic (prevents domination)
        - citation_graph: pagerank-style
      
    discussion_feed:
      factors:
        - chronological: default
        - reply_count: no boost (prevents controversy farming)
        - contributor_reputation: minor boost
        
    search_ranking:
      factors:
        - keyword_relevance: tf-idf
        - verification_status: major boost
        - contributor_reputation: minor boost
        - recency: time-decay
        
  anti_gaming:
    - Algorithm updates prevent optimization
    - Multi-factor ranking prevents single-factor gaming
    - Community monitoring for emerging exploits
```

**Borrowed From**:
- Snapshot's transparent voting mechanisms
- Gitcoin's quadratic funding algorithm (open, auditable)
- Farcaster's network consensus on message ordering

---

## 6. Integration Patterns from Research

### Farcaster → CLAWD Adaptations

| Farcaster Feature | CLAWD Adaptation | Rationale |
|-------------------|------------------|-----------|
| Hybrid onchain/offchain | Kernel onchain, social offchain | Security where it matters |
| Account key system | Agent delegation keys | Agents act on user's behalf |
| Storage rent | Reputation decay | Prevents accumulation farming |
| Snapchain consensus | Work verification layer | Objective truth, not social consensus |

### Lens Protocol → CLAWD Adaptations

| Lens Feature | CLAWD Adaptation | Rationale |
|--------------|------------------|-----------|
| Modular social primitives | Lane system | Separation of concerns |
| Customizable Rules | Policy-based moderation | Transparent enforcement |
| Graph relationships | Work citation graphs | Epistemic traceability |
| Smart Account abstraction | Agent identity management | AI-native architecture |

### Moloch DAO → CLAWD Adaptations

| Moloch Feature | CLAWD Adaptation | Rationale |
|----------------|------------------|-----------|
| Ragequit | Reputation exit | Leave without losing earned reputation |
| Guild Kick | Community moderation | Remove bad actors with due process |
| Proposal-based funding | Work-first incentives | No pay without verification |
| Loot vs Shares | Reputation vs Governance | Separation of contribution and power |

### Huginn/Activepieces → CLAWD Adaptations

| Feature | CLAWD Adaptation | Rationale |
|---------|------------------|-----------|
| Agent event graphs | Work provenance chains | Full traceability of agent actions |
| Workflow automation | Kernel task orchestration | Agents execute in verified environment |
| Trigger-action model | Event-driven reputation | Reputation updates based on outcomes |

---

## 7. Threat Model: Attack Vectors & Mitigations

### Attack Vector 1: Reputation Farming

**Scenario**: User creates low-quality work at high volume to farm reputation.

**Mitigations**:
- Quality threshold before reputation award
- Peer review requirement for research
- Automated test requirement for code
- Reputation decay (must maintain quality)
- Sub-linear rewards (diminishing returns on volume)

### Attack Vector 2: Sybil Reputation Boosting

**Scenario**: User creates multiple identities to upvote/boost their own content.

**Mitigations**:
- Human Passport sybil resistance
- Costly identity creation (stake required)
- Graph analysis for cluster detection
- Reputation-weighted voting (new identities have no weight)

### Attack Vector 3: Verification Gaming

**Scenario**: User exploits edge cases in verification to get false positives.

**Mitigations**:
- Multiple verification mechanisms (no single point of failure)
- Challenge period (content can be disputed)
- Slashing for false verification (reputation penalty)
- Continuous verification (past work can be re-reviewed)

### Attack Vector 4: Speculation Lane Hijacking

**Scenario**: User promotes speculation in verified lane for visibility.

**Mitigations**:
- Automated semantic classification
- Community reporting with stake
- Demotion algorithm (returns to speculation lane)
- Reputation penalty for mislabeling

### Attack Vector 5: Moderation Capture

**Scenario**: Coordinated group captures moderation functions.

**Mitigations**:
- Policy-based moderation (humans enforce code, not discretion)
- Decentralized appeal process
- Ragequit option (users can exit if moderation becomes unfair)
- Regular policy review via governance

---

## 8. Implementation Roadmap

### Phase 1: Foundation (MVP)
- Basic identity system (ENS + email verification)
- Two-lane system (verified + discussion)
- Simple reputation based on code merges
- Automated moderation for spam

### Phase 2: Hardening
- Human Passport integration
- Full lane separation (add speculation lane)
- Non-transferable reputation tokens
- Policy-based moderation framework

### Phase 3: Scale
- ML-based sybil detection
- Advanced reputation decay
- Cross-domain reputation (research, code, execution)
- Algorithmic governance

### Phase 4: Maturation
- Full decentralization of moderation
- Community-owned algorithm parameters
- Robust reputation markets prevention
- 500-year sustainability mechanisms

---

## 9. Success Metrics

**What Good Looks Like**:

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Verified/Speculation Ratio | 10:1 | Signal dominates noise |
| Reputation Retention (6mo) | 60% | Reputation reflects ongoing contribution |
| Sybil Detection Rate | >95% | System resistant to fake identities |
| Moderation Appeal Success | 20-30% | Not too strict, not too lenient |
| Contributor Diversity | Gini < 0.4 | No concentration of reputation |
| Knowledge Half-Life | 18 months | Outdated info naturally decays |

---

## 10. Conclusion: Truth Over Popularity

The social layer is where CLAWD lives or dies. If we reward engagement, we become Facebook. If we reward coordination without verification, we become Moloch. If we let speculation mix with truth, we become Reddit during a bull run.

Our architecture must:
1. **Measure what matters**: Verified work, not engagement
2. **Separate concerns**: Speculation in its lane, truth in another
3. **Resist capture**: Decentralized, transparent, policy-based
4. **Think in centuries**: Build for 500 years, not 5

The goal is not to create the most active community. The goal is to create the most *accurate* community—one where truth has structural advantages over noise, where coordination failures are designed out, where the best ideas win not because they're popular but because they're correct.

---

## References

### Protocols Analyzed
- **Farcaster**: Hybrid onchain/offchain social protocol (docs.farcaster.xyz)
- **Lens Protocol**: Modular social primitives (lens.xyz)
- **Huginn**: Agent-based automation system (github.com/huginn/huginn)
- **Activepieces**: AI workflow automation (github.com/activepieces/activepieces)
- **LobeHub**: Agent collaboration platform (github.com/lobehub/lobe-chat)
- **AutoGPT**: AI agent framework (github.com/Significant-Gravitas/AutoGPT)
- **Snapshot**: Off-chain voting platform (snapshot.org)
- **Moloch DAO**: Minimal viable DAO framework (github.com/MolochVentures/moloch)
- **Human Passport**: Sybil resistance protocol (docs.passport.xyz)
- **ENS**: Decentralized naming service (ens.domains)

### Key Concepts
- **SBTs (Soulbound Tokens)**: Vitalik Buterin et al., "Decentralized Society"
- **Moloch**: Scott Alexander, "Meditations on Moloch"
- **Simulacra**: Jean Baudrillard, "Simulacra and Simulation"
- **Coordination Failures**: Elinor Ostrom, "Governing the Commons"
- **Sybil Resistance**: John Douceur, "The Sybil Attack"

---

*Document Version: 1.0*
*Last Updated: 2026-02-14*
*Next Review: Upon implementation of Phase 1*
