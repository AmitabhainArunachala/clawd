# TRISHULA-WebSocket v2.0 Implementation Plan

## Executive Summary

**Project:** TRISHULA-WebSocket v2.0  
**Goal:** Replace file-based TRISHULA with real-time WebSocket coordination (<100ms latency, 99% uptime)  
**Timeline:** 14 days from kickoff  
**Team:** 3 agents (DC on Mac, AGNI on VPS, RUSHABDEV on VPS)

---

## 1. Phase Breakdown

### Phase 1: Proof of Concept (Days 1-3)
**Objective:** Validate WebSocket architecture on local Mac environment

**Deliverables:**
- WebSocket server prototype (Node.js/WebSocket library)
- Basic client connection handlers
- Message serialization protocol (JSON with binary fallback)
- Latency benchmark tests

**Technical Decisions:**
- Protocol: WebSocket (ws library for Node.js)
- Message format: JSON with compression consideration
- Connection handling: Auto-reconnect with exponential backoff
- Security: Token-based authentication

---

### Phase 2: VPS Deployment (Days 4-7)
**Objective:** Deploy and test WebSocket server on VPS infrastructure

**Deliverables:**
- Docker container for WebSocket server
- VPS deployment on AGNI's environment
- SSL/TLS termination (nginx reverse proxy)
- Health check and monitoring endpoints
- Load balancer configuration (if multi-instance)

**Infrastructure:**
- Server: AGNI VPS (primary), RUSHABDEV VPS (failover)
- Reverse Proxy: nginx with WebSocket upgrade support
- Monitoring: Basic uptime/latency tracking
- CI/CD: Automated deployment pipeline

---

### Phase 3: Integration (Days 8-11)
**Objective:** Connect all three agents to WebSocket coordination

**Deliverables:**
- DC (Mac) client integration with existing workflow
- AGNI VPS agent integration
- RUSHABDEV VPS agent integration
- Message routing and broadcast logic
- Audit trail logging system
- Error handling and recovery mechanisms

**Integration Points:**
- Agent registration and heartbeat protocol
- Message types: COMMAND, STATUS, RESULT, ERROR, HEARTBEAT
- Namespace isolation per agent/function
- Backward compatibility layer (fallback to file-based if WS down)

---

### Phase 4: Optimization (Days 12-14)
**Objective:** Achieve target latency (<100ms) and reliability (99% uptime)

**Deliverables:**
- Connection pooling optimization
- Binary message protocol (MessagePack) for large payloads
- Redis pub/sub for multi-server horizontal scaling
- Comprehensive test suite (load, stress, failover)
- Documentation and runbooks

**Optimizations:**
- Message compression (permessage-deflate)
- Binary protocol for structured data
- Connection keep-alive tuning
- Redis-backed session state

---

## 2. Timeline

| Phase | Duration | Start | End | Key Milestone |
|-------|----------|-------|-----|---------------|
| Phase 1: PoC | 3 days | Day 1 | Day 3 | <50ms local latency |
| Phase 2: VPS Deploy | 4 days | Day 4 | Day 7 | VPS accessible, SSL working |
| Phase 3: Integration | 4 days | Day 8 | Day 11 | All 3 agents connected |
| Phase 4: Optimization | 3 days | Day 12 | Day 14 | <100ms, 99% uptime proven |
| **TOTAL** | **14 days** | | | |

### Detailed Schedule

**Days 1-3 (PoC)**
- Day 1: Server setup, basic connection handling (DC)
- Day 2: Client library, message protocol (DC)
- Day 3: Testing, latency benchmarks (DC)

**Days 4-7 (VPS Deploy)**
- Day 4: Docker setup, AGNI VPS prep (AGNI)
- Day 5: Deployment, nginx config (AGNI)
- Day 6: SSL certs, health endpoints (AGNI)
- Day 7: Failover setup on RUSHABDEV VPS (RUSHABDEV)

**Days 8-11 (Integration)**
- Day 8: DC Mac client integration (DC)
- Day 9: AGNI agent integration (AGNI)
- Day 10: RUSHABDEV agent integration (RUSHABDEV)
- Day 11: Full mesh testing, bug fixes (ALL)

**Days 12-14 (Optimization)**
- Day 12: Performance tuning, compression (DC)
- Day 13: Redis integration, failover tests (AGNI + RUSHABDEV)
- Day 14: Final benchmarks, documentation (ALL)

---

## 3. Task Assignments

### DC (Mac - Development/Testing Lead)

| Phase | Tasks | Hours |
|-------|-------|-------|
| 1 | WebSocket server prototype, client library, benchmarks | 16h |
| 3 | Mac client integration, workflow adaptation | 12h |
| 4 | Performance tuning, MessagePack implementation | 10h |
| **Total** | | **38h** |

**Responsibilities:**
- Architecture design
- Local development and testing
- Mac-specific client implementation
- Performance optimization
- Documentation

---

### AGNI (VPS - Infrastructure Lead)

| Phase | Tasks | Hours |
|-------|-------|-------|
| 2 | Docker containerization, primary VPS deployment | 12h |
| 2 | nginx reverse proxy, SSL termination | 8h |
| 3 | AGNI agent integration | 8h |
| 4 | Redis integration, failover logic | 8h |
| **Total** | | **36h** |

**Responsibilities:**
- Primary VPS infrastructure
- Docker and deployment automation
- SSL/TLS and security
- Redis coordination layer
- Monitoring setup

---

### RUSHABDEV (VPS - Reliability Lead)

| Phase | Tasks | Hours |
|-------|-------|-------|
| 2 | Failover VPS setup, load balancer config | 10h |
| 3 | RUSHABDEV agent integration | 8h |
| 4 | Stress testing, chaos engineering | 10h |
| 4 | Uptime monitoring, alerting | 6h |
| **Total** | | **34h** |

**Responsibilities:**
- Failover server and redundancy
- Load testing and stress validation
- 99% uptime verification
- Alerting and incident response
- Backup and recovery procedures

---

## 4. Dependencies and Blockers

### Critical Path Dependencies

```
[DC: PoC Server] → [AGNI: VPS Deploy] → [ALL: Integration] → [ALL: Optimization]
       ↓                ↓                      ↓
   [Validation]    [DNS/SSL certs]      [Agent availability]
```

### Potential Blockers

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| DC Mac firewall blocking WebSocket | High | Medium | Use port 443, test early |
| VPS network latency >100ms | Critical | Low | CDN/edge deployment, protocol optimization |
| SSL certificate delays | Medium | Low | Use Let's Encrypt, automate |
| Agent time sync issues | Medium | Medium | NTP sync requirement, tolerance in protocol |
| Redis not available on VPS | Medium | Low | Implement in-memory fallback |
| Docker resource limits | Medium | Medium | Monitor, scale VPS if needed |

### External Dependencies

1. **DNS propagation** (Day 5) - May take 24-48 hours
2. **SSL certificate issuance** (Day 5) - Usually instant but can delay
3. **VPS provider stability** - Monitor during stress testing

---

## 5. Success Criteria

### Performance Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Message latency (p50) | <50ms | `Date.now()` diff on send/ack |
| Message latency (p99) | <100ms | Load test with 1000 messages |
| Connection establishment | <500ms | Time to first message |
| Throughput | >1000 msg/sec | Load test benchmark |

### Reliability Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Uptime | 99% | 30-day monitoring period |
| Connection stability | <1 disconnect/day | Reconnect counter |
| Message delivery | 99.9% | Ack/nack tracking |
| Failover time | <5 seconds | Manual failover test |

### Functional Requirements

- [ ] All 3 agents can connect simultaneously
- [ ] Messages delivered to intended recipients only (no broadcast storms)
- [ ] Audit trail captures all messages with timestamp
- [ ] Auto-reconnect on network interruption
- [ ] Backward compatibility with file-based TRISHULA (fallback mode)

### Benchmark Protocol

```bash
# Run before and after optimization
./benchmark.js --duration 60s --connections 3 --rate 100

# Expected output:
# Latency p50: 45ms
# Latency p99: 98ms
# Success rate: 99.97%
# Throughput: 1200 msg/sec
```

---

## 6. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTS                              │
├──────────────┬─────────────────┬────────────────────────────┤
│  DC (Mac)    │  AGNI (VPS)     │  RUSHABDEV (VPS)           │
│  Agent Client│  Agent Client   │  Agent Client              │
└──────┬───────┴────────┬────────┴────────────┬───────────────┘
       │                │                     │
       └────────────────┼─────────────────────┘
                        │ WebSocket (wss://)
                        ▼
       ┌─────────────────────────────────────┐
       │           nginx (SSL)               │
       └─────────────────┬───────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
   ┌──────▼──────┐              ┌───────▼──────┐
   │ AGNI VPS    │◄────────────►│RUSHABDEV VPS │
   │  Primary    │   Redis      │   Failover   │
   │   Server    │   Pub/Sub    │   Server     │
   └─────────────┘              └──────────────┘
          │                             │
          └──────────────┬──────────────┘
                         ▼
                ┌─────────────────┐
                │  Audit Logger   │
                │  (Redis/Files)  │
                └─────────────────┘
```

---

## 7. Message Protocol

### Message Types

```json
{
  "type": "COMMAND|STATUS|RESULT|ERROR|HEARTBEAT|ACK",
  "from": "agent_id",
  "to": "agent_id|broadcast",
  "id": "uuid",
  "timestamp": 1707561600000,
  "payload": {},
  "priority": 1-5
}
```

### Connection Lifecycle

1. **Connect** → Server validates token
2. **Register** → Agent announces capabilities
3. **Heartbeat** → Every 30 seconds (configurable)
4. **Message Exchange** → Command/Result flow
5. **Disconnect** → Cleanup, log session

---

## 8. Rollback Plan

If WebSocket v2.0 fails validation:

1. **Immediate (0-1 hour):** Switch to fallback mode (file-based TRISHULA)
2. **Short-term (1-24 hours):** Debug critical issue, hotfix if possible
3. **Long-term (>24 hours):** Revert to v1.0, schedule v2.1 planning

Fallback trigger conditions:
- Uptime <95% over 24 hours
- Latency p99 >200ms consistently
- Message loss >1%
- Any agent unable to connect for >1 hour

---

## 9. Post-Launch Monitoring

### Week 1-2 (Stabilization)
- Daily latency reports
- Connection stability review
- Error log triage

### Week 3-4 (Validation)
- 99% uptime verification
- Performance regression tests
- Documentation updates

### Ongoing
- Weekly uptime reports
- Monthly performance reviews
- Quarterly capacity planning

---

## Appendix A: File Structure

```
/trishula-ws/
├── server/
│   ├── src/
│   │   ├── server.js
│   │   ├── handlers/
│   │   ├── middleware/
│   │   └── utils/
│   ├── Dockerfile
│   └── package.json
├── client/
│   ├── src/
│   │   ├── client.js
│   │   └── adapters/
│   └── package.json
├── shared/
│   └── protocol.js
├── tests/
│   ├── benchmark.js
│   └── integration/
└── deploy/
    ├── docker-compose.yml
    └── nginx.conf
```

## Appendix B: Emergency Contacts

| Agent | Role | Escalation |
|-------|------|------------|
| DC | Lead Developer | Architecture decisions |
| AGNI | Infrastructure | VPS/Deployment issues |
| RUSHABDEV | Reliability | Failover/Uptime issues |

---

*Document Version: 1.0*  
*Created: 2026-02-10*  
*Next Review: Upon Phase 1 completion*
