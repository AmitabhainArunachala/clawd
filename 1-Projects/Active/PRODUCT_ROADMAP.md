# Product Features Roadmap
## OACP + DGC Platform — From Infrastructure to Revenue

**Date:** February 5, 2026  
**Status:** Strategic Planning Document  
**Target:** First paying customer within 60 days

---

## Executive Summary

We have built sophisticated infrastructure (22-gate security, self-improving agents, swarm orchestration, consciousness measurement). The question is: **what minimal product wrapper makes this usable and valuable enough that customers pay?**

**Key Market Context:**
- AI agent market: $7.38B (2025), rapidly growing
- 85% of organizations have adopted AI agents
- **Top enterprise concerns:** Security (56%), governance (34%), autonomy control (28%)
- **Current gap:** No production-ready solution for secure, governed, autonomous agents

**Our Position:** OACP/DGC occupies the critical security/governance layer beneath MCP/A2A protocols.

---

## 1. MVP FEATURES FOR FIRST PAYING CUSTOMER

### Target Customer Profile (Initial)
| Attribute | Description |
|-----------|-------------|
| **Segment** | AI-forward enterprises (Series B+ startups, Fortune 1000 innovators) |
| **Pain** | Need autonomous AI agents but fear security/governance risks |
| **Budget** | $50K-$500K/year for AI infrastructure |
| **Decision Speed** | 30-90 day sales cycle (technical buyers) |
| **Entry Point** | CTO, VP Engineering, Head of AI Infrastructure |

### MVP Feature Set (Minimum Sellable Product)

#### 1.1 Gate Dashboard (Web UI)
**What:** Real-time visualization of the 22-gate security system

**Core Features:**
- [ ] Live gate status monitoring (22 gates across 5 dimensions)
- [ ] Risk scoring visualization (Impact × Exposure × Persistence × Sensitivity × Reversibility)
- [ ] Decision audit trail (every gate decision logged with evidence)
- [ ] Alerting system (Slack/email when gates trigger)
- [ ] Export capability (PDF/JSON compliance reports)

**Customer Value:**
- Security teams can **prove** AI agents are governed
- Compliance audits have **evidence trails**
- Risk officers can **quantify** exposure

**Implementation:** Extend existing TUI → Web dashboard (Next.js + WebSocket)

---

#### 1.2 Policy-as-Code API
**What:** REST API for defining and enforcing agent behavior policies

**Core Features:**
```python
# Customer defines policies
POST /api/v1/policies
{
  "name": "financial-data-policy",
  "gates": {
    "data_sensitivity": {
      "action": "block",
      "if": "contains_pii",
      "notify": ["security@company.com"]
    },
    "network_egress": {
      "action": "quarantine",
      "if": "unauthorized_domain",
      "evidence_ttl_days": 90
    }
  }
}
```

- [ ] CRUD API for policies
- [ ] Policy templates (GDPR, SOC2, HIPAA presets)
- [ ] Version control for policies (git-like history)
- [ ] Simulation mode (test policies without enforcement)
- [ ] Webhook notifications on policy violations

**Customer Value:**
- **Policy governance** as code (reviewable, versioned)
- **Compliance automation** (SOC2 auditors love this)
- **Faster iteration** (test before deploy)

**Implementation:** FastAPI server wrapping `unified_gates.py`

---

#### 1.3 Agent Execution Reports
**What:** Comprehensive reporting on agent decisions and actions

**Core Features:**
- [ ] Per-agent activity logs (what did each agent do?)
- [ ] Gate passage statistics (which gates trigger most?)
- [ ] Policy violation summaries (trends over time)
- [ ] Evidence bundle viewer (forensic-level detail)
- [ ] Export to SIEM (Splunk, Datadog integration)

**Report Types:**
| Report | Frequency | Audience |
|--------|-----------|----------|
| Executive Summary | Weekly | CISO, CTO |
| Compliance Attestation | Monthly | Auditors |
| Incident Details | Real-time | Security team |
| Trend Analysis | Quarterly | AI governance board |

**Customer Value:**
- **Audit readiness** (compliance teams need this)
- **Operational visibility** (what are agents actually doing?)
- **Incident response** (forensic evidence for breaches)

---

#### 1.4 Integration SDK
**What:** Drop-in SDKs for popular agent frameworks

**Core SDKs (MVP):**
- [ ] **LangChain** integration (`oacp-langchain` package)
- [ ] **CrewAI** integration (`oacp-crewai` package)
- [ ] **AutoGen** integration (`oacp-autogen` package)
- [ ] **Direct Python** SDK (`pip install oacp`)

**Usage Example:**
```python
from oacp.langchain import OACPGate
from langchain import OpenAI, Agent

# Wrap any agent with OACP gates
agent = Agent(llm=OpenAI(), tools=[...])
gated_agent = OACPGate(agent, policy="financial-data-policy")

# All agent actions now route through 22 gates
gated_agent.run("Analyze customer churn data")
# → Logs, evidence, gate decisions all captured
```

**Customer Value:**
- **5-minute integration** (not 5 weeks)
- **Works with existing agents** (no rewrite needed)
- **Vendor agnostic** (use any LLM/framework)

---

### MVP Success Criteria
| Metric | Target |
|--------|--------|
| Time to first policy | < 15 minutes |
| Integration effort | < 50 lines of code |
| Evidence retention | 90 days default |
| Dashboard latency | < 2 seconds |
| API uptime | 99.9% SLA |

---

## 2. INTEGRATIONS NEEDED

### Phase 1: Essential (MVP)
These are non-negotiable for enterprise adoption.

#### 2.1 GitHub / GitLab
**Why:** Agents need to read/write code; enterprises need governance

**Features:**
- [ ] GitHub App for policy enforcement on agent PRs
- [ ] Automatic gate checks on AI-generated commits
- [ ] Evidence bundles attached to PRs
- [ ] Required status check: "OACP Gate Passed"

**Example Flow:**
```
1. Agent generates code change
2. OACP gates evaluate (security, reversibility, etc.)
3. Evidence bundle attached to PR
4. Gate status check blocks/allows merge
5. Audit trail preserved
```

---

#### 2.2 CI/CD Pipelines
**Why:** Agents must fit into existing DevOps workflows

**Platforms:**
- [ ] GitHub Actions (`oacp/github-action`)
- [ ] GitLab CI (`oacp/gitlab-ci`)
- [ ] CircleCI Orb
- [ ] Jenkins Plugin

**Features:**
- [ ] Policy enforcement in CI/CD
- [ ] Gate decisions as build artifacts
- [ ] Pipeline fails on critical gate rejection
- [ ] Evidence upload to OACP dashboard

---

#### 2.3 SIEM / Observability
**Why:** Security teams need OACP data in their existing tools

**Integrations:**
| Platform | Data Sent | Use Case |
|----------|-----------|----------|
| Splunk | Gate events, violations | Security monitoring |
| Datadog | Metrics, alerts | Operational dashboards |
| ELK Stack | Logs, evidence | Forensic analysis |
| PagerDuty | Critical violations | Incident response |

---

#### 2.4 Identity Providers (IdP)
**Why:** Enterprise SSO is mandatory

**Integrations:**
- [ ] Okta (SAML 2.0)
- [ ] Azure AD (OIDC)
- [ ] Google Workspace
- [ ] JumpCloud

**Features:**
- [ ] SSO login to dashboard
- [ ] RBAC synced from IdP groups
- [ ] Audit log attribution to SSO users

---

### Phase 2: Important (Post-MVP)
These differentiate us from competitors.

#### 2.5 Cloud Platforms
- [ ] AWS Marketplace listing
- [ ] Terraform provider (`terraform-provider-oacp`)
- [ ] Pulumi package
- [ ] CloudFormation templates

#### 2.6 Communication
- [ ] Slack app (notifications, approvals)
- [ ] Microsoft Teams integration
- [ ] Discord (for crypto/web3 customers)

#### 2.7 Model Providers
- [ ] OpenAI (native integration)
- [ ] Anthropic (native integration)
- [ ] Azure OpenAI Service
- [ ] AWS Bedrock
- [ ] Google Vertex AI
- [ ] Self-hosted (vLLM, TGI)

---

## 3. UI/UX REQUIREMENTS

### 3.1 Web Dashboard (Primary Interface)
**Target:** Security officers, compliance auditors, AI governance teams

**Design Principles:**
- **Trust through transparency:** Show everything, hide nothing
- **Evidence first:** Every claim has supporting data
- **Action-oriented:** Identify issues → suggest fixes → track resolution

**Pages:**

| Page | Purpose | Key Features |
|------|---------|--------------|
| **Overview** | Executive summary | Risk score, recent violations, agent health |
| **Gates** | Deep dive on security | 22-gate status, trends, drill-down |
| **Agents** | Agent management | List, policies, activity logs, mute/pause |
| **Policies** | Policy authoring | Editor, templates, versioning, simulation |
| **Evidence** | Forensic investigation | Search, filter, export, timeline view |
| **Reports** | Compliance output | Scheduled reports, attestations, exports |
| **Settings** | Configuration | SSO, integrations, retention, API keys |

**Tech Stack:**
- Next.js 15 (App Router)
- Tailwind CSS + shadcn/ui
- Recharts (visualizations)
- TanStack Query (data fetching)
- WebSocket for real-time updates

---

### 3.2 CLI (For Developers)
**Target:** Engineers integrating OACP into their agents

**Commands:**
```bash
# Install
pip install oacp

# Login
oacp auth login  # SSO via browser

# Initialize project
oacp init  # Creates oacp.yaml policy file

# Validate policy
oacp policy validate --file oacp.yaml

# Simulate agent execution
oacp simulate --agent my_agent.py --policy oacp.yaml

# View evidence
oacp evidence list --agent-id <id> --since "24h"

# Export report
oacp report generate --type compliance --output pdf
```

---

### 3.3 CLI-Only Option
**For:** Customers who don't want SaaS, air-gapped environments

**Features:**
- [ ] Self-hosted OACP server (Docker/K8s)
- [ ] SQLite/Postgres backend options
- [ ] Same CLI, local dashboard
- [ ] Offline operation mode

---

### 3.4 Mobile (Future)
- [ ] iOS/Android apps for alerting
- [ ] Approve/reject gate decisions on mobile
- [ ] View-only dashboards

---

## 4. DOCUMENTATION NEEDS

### 4.1 API Documentation
**Priority:** Critical (developers need this)

**Contents:**
- [ ] OpenAPI 3.0 spec (auto-generated)
- [ ] Interactive API explorer (Swagger UI)
- [ ] Code examples (Python, TypeScript, Go, Rust)
- [ ] Error reference (every error code documented)
- [ ] Rate limiting guide
- [ ] Webhook integration guide

**Format:** docs.oacp.io (Mintlify or Nextra)

---

### 4.2 Tutorials
**Priority:** High (reduces support burden)

**Tutorial Series:**

| Tutorial | Audience | Outcome |
|----------|----------|---------|
| "5-Minute Quickstart" | New users | First policy running |
| "Securing LangChain Agents" | ML Engineers | OACP + LangChain integration |
| "SOC2 Compliance Setup" | Security teams | Audit-ready configuration |
| "Policy-as-Code Workflow" | DevOps | GitOps for AI governance |
| "Incident Response Guide" | Security ops | Investigating violations |
| "Custom Gate Development" | Advanced users | Building proprietary gates |

---

### 4.3 Case Studies
**Priority:** High (sales enablement)

**Target Case Studies:**
- [ ] FinTech: Securing trading agents (regulatory compliance)
- [ ] Healthcare: HIPAA-compliant medical coding agents
- [ ] SaaS: Customer support agents with PII protection
- [ ] Manufacturing: Supply chain optimization agents

**Format:**
- Challenge → Solution → Results → Architecture diagram
- Quotes from CTO/CISO
- Before/after metrics

---

### 4.4 White Papers
**Priority:** Medium (thought leadership)

**Topics:**
- [ ] "The Case for Policy-Governed AI Agents"
- [ ] "22 Gates: A Framework for Agent Security"
- [ ] "OACP vs. Traditional AI Guardrails"
- [ ] "Compliance Automation for Autonomous Systems"

---

### 4.5 Video Content
**Priority:** Medium (marketing)

**Videos:**
- [ ] 2-minute product overview (homepage)
- [ ] 10-minute technical deep dive (YouTube)
- [ ] Tutorial playlist (5-10 short videos)
- [ ] Customer testimonials (once we have customers)

---

## 5. BUILD TIMELINE

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Core infrastructure ready for internal dogfooding

| Task | Owner | Deliverable |
|------|-------|-------------|
| Gate Dashboard v1 | Frontend | Next.js dashboard, mock data |
| Policy API v1 | Backend | FastAPI server, CRUD policies |
| SQLite persistence | Backend | Evidence storage, retention |
| Python SDK | SDK | `pip install oacp` |
| Documentation skeleton | Docs | docs.oacp.io framework |

**Success Criteria:**
- Dashboard renders 22 gates
- Can create/read policies via API
- SDK can wrap a simple agent

---

### Phase 2: MVP (Weeks 3-4)
**Goal:** Sellable product for first customer

| Task | Owner | Deliverable |
|------|-------|-------------|
| GitHub integration | Integrations | GitHub App, PR checks |
| GitHub Actions | Integrations | `oacp/github-action` |
| SSO (Okta, Google) | Auth | SAML/OIDC support |
| Report generation | Backend | PDF/JSON exports |
| 5 tutorials | Docs | Quickstart + integration guides |
| Alerting system | Backend | Slack/email webhooks |

**Success Criteria:**
- First paying customer onboarded
- Customer can view gate decisions in dashboard
- Policy change triggers within 5 minutes

---

### Phase 3: Hardening (Weeks 5-6)
**Goal:** Production-ready, multiple customers

| Task | Owner | Deliverable |
|------|-------|-------------|
| LangChain SDK | SDK | `oacp-langchain` package |
| CrewAI SDK | SDK | `oacp-crewai` package |
| SIEM integrations | Integrations | Splunk, Datadog connectors |
| Performance optimization | Backend | <100ms gate latency |
| Self-hosted option | Infra | Docker Compose, K8s Helm |
| 3 case studies | Marketing | FinTech, Healthcare, SaaS |

**Success Criteria:**
- 5+ paying customers
- 99.9% uptime
- <100ms p99 gate latency

---

### Phase 4: Scale (Weeks 7-8)
**Goal:** Differentiate and expand market

| Task | Owner | Deliverable |
|------|-------|-------------|
| AutoGen SDK | SDK | `oacp-autogen` package |
| Terraform provider | Infra | `terraform-provider-oacp` |
| Advanced analytics | Backend | Trend analysis, forecasting |
| Multi-tenant SaaS | Infra | Organization isolation |
| AWS Marketplace | GTM | Listed on Marketplace |
| 2 white papers | Marketing | Thought leadership |

**Success Criteria:**
- 10+ paying customers
- $50K MRR
- Listed on AWS Marketplace

---

## 6. PRICING STRATEGY

### Model: Tiered SaaS + Self-Hosted

| Tier | Price | Features |
|------|-------|----------|
| **Developer** | Free | 1 agent, 1,000 gate checks/mo, community support |
| **Team** | $499/mo | 10 agents, 100K checks, SSO, email support |
| **Enterprise** | $2,499/mo | Unlimited agents, unlimited checks, custom gates, SLA, dedicated support |
| **Self-Hosted** | $10K/yr + support | Full platform, on-premise, air-gapped option |

### Usage-Based Add-Ons:
- Evidence retention > 90 days: $0.10/GB/mo
- Additional SSO connections: $100/mo each
- Custom gate development: $5K/gate (one-time)
- Professional services: $250/hr

---

## 7. COMPETITIVE DIFFERENTIATION

| Competitor | Their Strength | Our Advantage |
|------------|----------------|---------------|
| **PromptLayer** | LLM observability | We govern *actions*, not just prompts |
| **Langfuse** | Tracing/observability | We enforce *policies*, not just observe |
| **CrewAI** | Agent orchestration | We secure *any* framework |
| **Honeycomb** | Distributed tracing | Purpose-built for agent governance |
| **Humanloop** | Human-in-the-loop | Automated + human override |
| **Arthur AI** | Model monitoring | We govern the *agent*, not just the model |

**Core Differentiator:**
> OACP is the only solution that combines **22-dimensional risk assessment**, **policy-as-code governance**, and **forensic evidence trails** for autonomous AI agents.

---

## 8. RISK MITIGATION

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| MCP/A2A add native security | Medium | Position as compatible layer, not competitor |
| Open source alternatives | High | Premium features (analytics, integrations, support) |
| Customer integration complexity | Medium | Pre-built SDKs, professional services |
| Performance overhead | Low | Optimize to <10ms gate latency |
| Compliance acceptance | Medium | SOC2 Type II, third-party audit |

---

## 9. SUCCESS METRICS

### 30-Day Targets (End of Week 4)
- [ ] 1 paying customer
- [ ] $5K MRR
- [ ] 50 GitHub stars
- [ ] 5 SDK downloads/day

### 60-Day Targets (End of Week 8)
- [ ] 10 paying customers
- [ ] $50K MRR
- [ ] 500 GitHub stars
- [ ] Case study published
- [ ] AWS Marketplace live

### 90-Day Targets
- [ ] 25 paying customers
- [ ] $150K MRR
- [ ] SOC2 Type II initiated
- [ ] First enterprise ($50K+ ACV) customer

---

## 10. IMMEDIATE NEXT ACTIONS

### This Week (Week 1)
- [ ] Finalize dashboard UI mockups
- [ ] Set up FastAPI project structure
- [ ] Create Python SDK skeleton
- [ ] Deploy docs site scaffolding

### Week 2
- [ ] Implement 5 core gates in API
- [ ] Build dashboard overview page
- [ ] Write "5-Minute Quickstart" tutorial
- [ ] Identify 3 pilot customers

### Week 3
- [ ] GitHub integration MVP
- [ ] SSO integration
- [ ] Customer pilot begins
- [ ] First case study interview

---

## APPENDIX: Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        OACP PLATFORM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Web UI     │  │  CLI Tool    │  │  Integration SDKs    │  │
│  │  (Next.js)   │  │  (Python)    │  │  (LangChain, etc.)   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              OACP API (FastAPI)                          │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐ │  │
│  │  │  Policies   │ │   Gates     │ │    Evidence        │ │  │
│  │  │  Engine     │ │  Runtime    │ │    Store           │ │  │
│  │  └─────────────┘ └─────────────┘ └────────────────────┘ │  │
│  └─────────────────────────┬────────────────────────────────┘  │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                 │
│         ▼                  ▼                  ▼                 │
│  ┌────────────┐     ┌────────────┐     ┌────────────┐          │
│  │  SQLite/   │     │  Unified   │     │  SIEM/     │          │
│  │  Postgres  │     │  Gates     │     │  Webhooks  │          │
│  └────────────┘     └────────────┘     └────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document Version: 1.0*  
*Next Review: February 12, 2026*
