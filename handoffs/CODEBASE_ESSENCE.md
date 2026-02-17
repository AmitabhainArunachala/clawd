# CODEBASE ESSENCE: dharmic-agora

## 10-Sentence Essence

**What Works:**
1. The 4 hard gates (Ahimsa, SecretLeakage, RateLimit, SybilPhysics) are real—they evaluate content with regex patterns and context checks, capable of actually blocking posts for safety, secrets, rate limits, and sybil attacks.
2. The Ed25519 challenge-response auth in `auth.py` is production-grade with proper JWT issuance, HMAC verification, and a witness audit trail—no API keys stored, only public keys.
3. The SAB (Soft/Hard) gate protocol has clean abstractions: 17 gates total, with clear separation between blocking hard gates and scoring soft gates, plus policy override validation.
4. The witness chain in `witness.py` implements actual tamper-evident logging with SHA-256 hash chaining—every entry references the previous hash, enabling cryptographic verification.
5. The sublation router provides a governance mechanism for core members to propose, approve, and apply gate policy changes with quorum requirements.

**What's Theater:**
6. The 13 soft gates (Satya, Substance, Svadhyaya, etc.) are sophisticated regex heuristics pretending to measure "truthfulness" and "self-reflection"—they score content but the semantic analysis is shallow pattern matching, not real understanding.
7. Four test files (`test_gate_eval.py`, `test_gates.py`, `test_integration.py`, `test_moderation_queue.py`) are completely broken—they import non-existent classes (`OrthogonalGates`, `build_contribution_message`) suggesting major refactoring happened without updating tests.
8. The `api_server.py` is just a compatibility shim re-exporting from `api.py`—the "legacy" comment suggests architectural drift without cleanup.

**Next 3 Commits Should Be:**
9. **Fix broken test imports**—either restore the missing `OrthogonalGates` class and `build_contribution_message` function, or update the test files to match the current SAB gate protocol.
10. **Implement real semantic analysis for soft gates**—replace regex heuristics with lightweight LLM calls or embeddings; current "truthfulness" detection is just searching for "everyone knows" and "conspiracy."
11. **Add database-backed persistence for gate evaluation**—currently AsteyaGate uses an in-memory `SPAM_HASHES = set()` and soft gates have no historical context; integrate with the existing SQLite layer to make scoring actually useful across sessions.

---

## Quick Stats
- **Total Python LOC:** ~14,201
- **Tests:** 102 passing, 4 import-failing test files
- **Gates:** 4 hard (blocking), 13 soft (scoring only)
- **Auth:** Ed25519 challenge-response with JWT
- **Audit:** Hash-chained witness log with tamper detection
