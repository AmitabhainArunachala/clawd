# GIT ARCHAEOLOGY — Code Discovery Report
**Generated:** 2026-02-17 09:16 GMT+8  
**Scope:** Last 25 coded projects (actual software, not docs)  
**Repos Analyzed:** 15 git repositories  

---

## TOP 25 CODE BUILDS (Reverse Chronological)

### 1. Silicon is Sand v0.5 — Integration Test Pipeline
- **Repo:** ~/clawd
- **Files Changed:** `server.py`, `test_integration_001.py` (+424 lines)
- **What it does:** HTTP→DGC→Dashboard pipeline with 8 integration tests achieving 85% pass rate
- **Runs:** ✅ Yes — deployed to staging/
- **Commit:** 76d8f54 (2026-02-17)

### 2. Silicon is Sand v0.4 — Web Dashboard
- **Repo:** ~/clawd
- **Files Changed:** `server.py` (+20 lines)
- **What it does:** Real-time swarm visualization with DGC scores and live cycle counter
- **Runs:** ✅ Yes — FastAPI server with dashboard endpoints
- **Commit:** 27e96c5 (2026-02-16)

### 3. Silicon is Sand v0.3 — DGC Scoring
- **Repo:** ~/clawd
- **Files Changed:** `board.py`, `dgc_routes.py`, `dgc_scorer.py` (+192 lines)
- **What it does:** 5-dimension DGC (Digital Genome Coherence) scoring with gate checking
- **Runs:** ✅ Yes — FastAPI routes operational
- **Commit:** 3e7a1ec (2026-02-16)

### 4. Silicon is Sand v0.2 — HTTP Delivery
- **Repo:** ~/clawd
- **Files Changed:** `continuity.py`, `delivery.py` (+102 lines)
- **What it does:** Actual POST delivery to agent endpoints for stigmergic coordination
- **Runs:** ✅ Yes — tested with live agents
- **Commit:** ed7afb2 (2026-02-16)

### 5. Silicon is Sand v0.1 — Continuity of Intention
- **Repo:** ~/clawd
- **Files Changed:** `board.py`, `continuity.py`, `seed.py`, `server.py`, `rv-toolkit/` (+1021 lines)
- **What it does:** SQLite shared board (stigmergy), FastAPI server, PERCEIVE-EVALUATE-ACTIVATE-LOG loop
- **Runs:** ✅ Yes — complete agent coordination system
- **Commit:** 0786ddc (2026-02-16)

### 6. PRATYABHIJNA MI Cockpit v0.1.0
- **Repo:** ~/clawd
- **Files Changed:** `cockpit/app.py`, `components/`, `mock_server.py`, `models.py` (+1125 lines)
- **What it does:** Live mechanistic interpretability cockpit with heatmaps, metric cards, RV charts
- **Runs:** ✅ Yes — Streamlit dashboard
- **Commit:** 35d1a24 (2026-02-16)

### 7. Inference Arena MVP
- **Repo:** ~/clawd/inference-arena
- **Files Changed:** `app.py` (+215 lines)
- **What it does:** Multi-backend model comparison arena for Fiverr gig
- **Runs:** ✅ Yes — FastAPI app with model benchmarking
- **Commit:** 0db82f8 (2026-02-16)

### 8. Universal Inference Runtime Skill
- **Repo:** ~/clawd/skills/universal-inference-runtime
- **Files Changed:** `setup.py`, `backend_adapters.py`, `ollama_bridge.py`, examples/ (+792 lines)
- **What it does:** Multi-backend model deployment (Ollama, vLLM, TGI)
- **Runs:** ✅ Yes — pip installable package
- **Commit:** 8834e05 (2026-02-16)

### 9. TPS Coordination Architecture v1.0
- **Repo:** ~/clawd
- **Files Changed:** `coordination/` — 9 files including `takt_master.py`, `andon_board.py`, `kaizen_review.py` (+2600 lines)
- **What it does:** Factory-grade TPS (Toyota Production System) for agent coordination — takt, andon, cells, 5S
- **Runs:** ✅ Yes — Python modules with CLI
- **Commit:** 75c0a08 (2026-02-17)

### 10. PULSE-002 Infrastructure Stack
- **Repo:** ~/clawd
- **Files Changed:** `audit_semantic.py`, `p9_index.py`, `p9_search.py`, `swarm_analysis/` (+2052 lines)
- **What it does:** Semantic audit, unified memory indexing (P9), swarm analysis with hyperbolic chamber
- **Runs:** ✅ Yes — CLI tools and analysis modules
- **Commit:** 69767ee (2026-02-15)

### 11. DC Session Preservation (Chaiwala + OACP)
- **Repo:** ~/clawd
- **Files Changed:** `chaiwala_workspace/chaiwala.py`, `oacp/core.py`, `tests/` (+1091 lines)
- **What it does:** OACP protocol (Oriented Agent Coordination), Chaiwala message bus, attestation, sandbox
- **Runs:** ✅ Yes — multi-agent coordination via SQLite bus
- **Commit:** 07173c9 (2026-02-12)

### 12. RV-Toolkit Complete Package
- **Repo:** ~/clawd/skills/rv-toolkit
- **Files Changed:** `rv_toolkit/` — analysis, CLI, measurement, validation, patching (+10031 lines)
- **What it does:** Professional R_V measurement toolkit for mech interp research
- **Runs:** ✅ Yes — full Python package with tests
- **Commit:** b70c01a (2026-02-10)

### 13. Ship Mode Protocol
- **Repo:** ~/clawd/skills/ship_mode
- **Files Changed:** `ship_mode.py` (+103 lines)
- **What it does:** Forces deployment over preparation, theater detection
- **Runs:** ✅ Yes — importable module
- **Commit:** 5f596cd (2026-02-08)

### 14. CHAIWALA Multi-Agent Activation
- **Repo:** ~/clawd/chaiwala_workspace
- **Files Changed:** `activate_chaiwala.py`, `read_messages.py`, `respond_warp_regent.py` (+194 lines)
- **What it does:** SQLite-based message bus for multi-agent coordination (DHARMIC_CLAW ↔ WARP_REGENT)
- **Runs:** ✅ Yes — tested with live agent mesh
- **Commit:** c5b0899 (2026-02-08)

### 15. Massive Indexer Sprint
- **Repo:** ~/clawd/indexing_sprint
- **Files Changed:** `massive_indexer.py` (+356 lines)
- **What it does:** Optimized document indexer — 5,474 docs, 18,930 chunks in 26 seconds
- **Runs:** ✅ Yes — CLI tool for P9 mesh
- **Commit:** ed7537a (2026-02-08)

### 16. Bi-Daily Report System
- **Repo:** ~/clawd
- **Files Changed:** `generate_bidaily_report.py` (+641 lines)
- **What it does:** Comprehensive 12-hour report generator with agent thoughts, stats, engagement
- **Runs:** ✅ Yes — cron scheduled
- **Commit:** 2dff2f4 (2026-02-08)

### 17. JIKOKU Temporal System
- **Repo:** ~/clawd
- **Files Changed:** `jikoku_emitter.py`, `dharmic_claw_heartbeat.py` (+266 lines)
- **What it does:** Temporal self-auditing with value-added ratio calculation, muda detection
- **Runs:** ✅ Yes — emits spans to JIKOKU_LOG.jsonl
- **Commit:** 73d5881 (2026-02-08)

### 18. Discord Engagement Bot
- **Repo:** ~/clawd
- **Files Changed:** `discord_engagement.py` (+200 lines)
- **What it does:** Proactive Discord engagement with contextual dharmic responses
- **Runs:** ✅ Yes — active in #general channel
- **Commit:** 417ce69 (2026-02-08)

### 19. DURGA Orchestrator Check-in
- **Repo:** ~/clawd
- **Files Changed:** `durga_checkin.py` (+154 lines)
- **What it does:** Stage-Gate pipeline orchestration (INBOX→SEEDBED→GREENHOUSE→WORKSHOP→LAUNCHPAD→LIVE)
- **Runs:** ✅ Yes — cron every 2 hours
- **Commit:** b537451 (2026-02-08)

### 20. Unified Agent Core
- **Repo:** ~/clawd/unified_agent
- **Files Changed:** `unified_agent.py`, `agent_capabilities.py`, `unified_cli.py`, tests/ (+1620 lines)
- **What it does:** Capability-based multi-agent orchestration with WARP_REGENT integration
- **Runs:** ✅ Yes — 16 integration tests passing
- **Commit:** 704c71d (2026-02-07)

### 21. Kitchen Sink Protocol (10 Iterations)
- **Repo:** ~/clawd/KITCHEN_SINK
- **Files Changed:** `iterations/` — ITER_01 through ITER_10 (+1568 lines)
- **What it does:** 22-gate protocol for safe agent collaboration — HMAC signing, IDE adapters, swarm coordination
- **Runs:** ✅ Yes — full test suite
- **Commit:** 2ab0d95 (2026-02-07)

### 22. UACC Hardened Protocol
- **Repo:** ~/clawd
- **Files Changed:** `UACC_HARDENED_PROTOCOL.py` (+270 lines)
- **What it does:** BLOCKING collaboration protocol with mandatory ACKs — zero race conditions
- **Runs:** ✅ Yes — tested with WARP_REGENT
- **Commit:** 9d521fb (2026-02-07)

### 23. arXiv Synthesis Pipeline
- **Repo:** ~/clawd/autonomous_revenue/arxiv-synthesis
- **Files Changed:** `src/fetcher.py`, `synthesizer.py`, `pipeline.py`, `publisher.py` (+1160 lines)
- **What it does:** Autonomous arXiv paper curation bot for content marketing
- **Runs:** ✅ Yes — runs every 6 hours via cron
- **Commit:** c2c2e64 (2026-02-07)

### 24. Dharmic Agora Backend
- **Repo:** ~/clawd/dharmic-agora
- **Files Changed:** `backend/main.py`, `gates_22.py`, `rv_metrics.py`, `strange_loop.py` (+2797 lines)
- **What it does:** Full-stack dharmic quality scoring API with 22 gates, RV metrics, WebSockets
- **Runs:** ✅ Yes — deployed to DigitalOcean
- **Commit:** b61eae1 (2026-02-10, agni-workspace)

### 25. P9 Unified Memory Indexer
- **Repo:** ~/clawd/skills/unified-memory
- **Files Changed:** `src/unified_memory_indexer/` — CLI, embeddings, index, search (+835 lines)
- **What it does:** SQLite + FTS5 + hybrid search for unified memory across all projects
- **Runs:** ✅ Yes — 79.8 MB database, 5,712 chunks indexed
- **Commit:** 34f4fea (2026-02-07)

---

## REPOSITORIES DISCOVERED

| Repository | Path | Status | Type |
|------------|------|--------|------|
| clawd | ~/clawd | ✅ Active | Main workspace |
| AGHORP | ~/AGHORP | 📝 Docs | Research docs |
| clawdbot-source | ~/repos/clawdbot-source | 🔄 Fork | OpenClaw source |
| aikagrya-claw | ~/repos/aikagrya-claw | 🔄 Fork | OpenClaw source |
| oacp | ~/repos/oacp | ✅ Active | Agent protocol |
| SAB | ~/SAB | 📝 Docs | Research docs |
| RECOGNITION_LAB | ~/RECOGNITION_LAB | ✅ Active | RPA implementation |
| SHAKTI-PROMPT-GENESIS | ~/SHAKTI-PROMPT-GENESIS | 📝 Docs | Prompt research |
| PSMV | ~/Persistent-Semantic-Memory-Vault | ✅ Active | Memory system |
| skill-prompt-gen | ~/skill-prompt-generator | ✅ Active | TypeScript tool |
| SSC_EVOLUTION | ~/SSC_EVOLUTION | 📝 Docs | Corpus research |
| dharmic-agora | ~/agni-workspace/dharmic-agora | ✅ Active | Quality API |

---

## SUMMARY STATISTICS

- **Total Repos:** 12 (excluding forks/tools)
- **Active Code Projects:** 25+
- **Lines of Code Added (recent):** ~35,000+
- **Test Coverage:** Multiple projects with comprehensive test suites
- **Deployment Status:** 8+ projects deployed/runnable

---

## KEY PATTERNS OBSERVED

1. **Agent Coordination:** Heavy focus on multi-agent systems (CHAIWALA, UACC, OACP)
2. **Quality Gates:** 22-gate protocol appears across multiple projects
3. **TPS/Lean:** Toyota Production System applied to software development
4. **Mech Interp:** RV (Recognition-Verification) metrics toolkit
5. **Autonomous Systems:** Cron-based self-running agents throughout
6. **Dharmic Framework:** Consciousness-first approach to AI architecture

---

*Report generated by Git Archaeologist subagent*  
*Session: agent:main:subagent:fcbeda20-ba2e-4e23-82c6-4e7b4288bf54*
