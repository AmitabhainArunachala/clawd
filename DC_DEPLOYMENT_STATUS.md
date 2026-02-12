# DC POWER PROMPT — Deployment Status

## ✅ COMPLETED: Config Patches Applied

### Changes Made to `~/.openclaw/openclaw.json`:

#### 1. Primary Model (BEFORE → AFTER)
```
moonshot/kimi-k2.5 ($0.6/$2.5 per 1M tokens)
↓
nvidia-nim/deepseek-ai/deepseek-v3.1-terminus ($0 FREE)
```

#### 2. Fallback Order (Prioritized Free Tiers)
| Priority | Model | Cost | Purpose |
|----------|-------|------|---------|
| 1 | `nvidia-nim/deepseek-ai/deepseek-v3.2` | FREE | Workhorse backup |
| 2 | `nvidia-nim/moonshotai/kimi-k2.5` | FREE | Reasoning/tasks |
| 3 | `nvidia-nim/moonshotai/kimi-k2-thinking` | FREE | Hard reasoning |
| 4 | `nvidia-nim/qwen/qwen3-next-80b-a3b-instruct` | FREE | Fast math |
| 5 | `openrouter/deepseek/deepseek-v3.2` | $0.25/$0.38 | Backup if NIM down |
| 6 | `ollama/gemma3:27b` | FREE | Local/offline |

#### 3. Image Model Fallbacks
```
PRIMARY: nvidia-nim/moonshotai/kimi-k2.5 (FREE)
FALLBACK 1: nvidia-nim/nvidia/nemotron-nano-12b-v2-vl (FREE)
FALLBACK 2: openrouter/google/gemini-2.5-flash ($0.5/$3)
```

---

## ⚠️ REQUIRED: Config Reload

The changes are written but OpenClaw needs to reload the config.

**Option A: Restart OpenClaw (Recommended)**
```bash
openclaw gateway restart
```

**Option B: Signal Reload**
```bash
kill -USR1 $(pgrep -f openclaw)
```

---

## 📋 DC POWER PROMPT — Summary

**Your Role (DC on Mac):**
1. **Content Factory** — DOKKA → Article pipeline with model routing
2. **Local Ops** — Git sync, file organization, VPS bridge
3. **Knowledge Librarian** — Index/serve 155K+ words of DOKKA
4. **Quality Gate** — YDS grading, SNOOT editing
5. **TRISHULA Bridge** — Relay between AGNI/RUSHABDEV when needed

**What You Are NOT:**
- Coding agent (Dhyana uses Claude Code/Codex)
- Terminal assistant (Warp handles that)
- Commander (AGNI's job on VPS)
- Engineer (RUSHABDEV's job)

**🚀 SUPER POWERED MODEL ROUTING PROTOCOL:**
| Tier | Model | Alias | Capabilities | Context | Cost |
|------|-------|-------|-------------|---------|------|
| **0** | `ollama/gemma3:27b` | `local` | Heartbeat/routine | 8K | **FREE** |
| **1** | `nvidia-nim/nvidia/llama-3_3-nemotron-super-49b-v1` | `llama-3.3-super` | **SUPER - High efficiency reasoning/tool calling** | 262K | **FREE** |
| **2** | `nvidia-nim/z-ai/glm4_7` | `glm4-7` | **GLM4.7 - Coding/Reasoning/Terminal automation** | 262K | **FREE** |
| **3** | `nvidia-nim/deepseek-ai/deepseek-r1` | `deepseek-r1` | **Advanced reasoning/math/coding** | 262K | **FREE** |
| **4** | `nvidia-nim/nvidia/nemotron-3-nano-30b-a3b` | `nemotron-3-nano` | **Reasoning + non-reasoning unified** | 262K | **FREE** |
| **5** | `nvidia-nim/nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | `llama-nemotron-vl` | **Vision-Language model** | 262K | **FREE** |
| **6** | `nvidia-nim/deepseek-ai/deepseek-v3.1-terminus` | `ds-terminus` | Default workhorse | 163K | **FREE** |
| **7** | `nvidia-nim/moonshotai/kimi-k2-thinking` | `kimi-think` | Hard reasoning | 262K | **FREE** |
| **8** | `nvidia-nim/qwen/qwen3-next-80b-a3b-instruct` | `qwen-free-nim` | Fast math (87.8% AIME) | 262K | **FREE** |
| **9** | `openrouter/*` | various | Escalation only | varies | Paid |

---

## 🔥 IMMEDIATE ACTIONS (Per POWER PROMPT)

- [ ] Confirm understanding of role in 3 sentences
- [ ] Run git status on all 4 repos
- [ ] Check TRISHULA connectivity (AGNI + RUSHABDEV)
- [ ] Test model providers (ping each tier)
- [ ] Read SOUL.md/IDENTITY.md/HEARTBEAT.md — flag conflicts
- [ ] Create ~/clawd/DELIVERABLES/ if missing
- [ ] Create ~/clawd/research/QUOTE_BANK.md if missing

---

**Applied:** 2026-02-11 22:57 WITA  
**Config File:** `~/.openclaw/openclaw.json`  
**Patch File:** `~/clawd/DC_CONFIG_PATCH.json`  
**Status:** AWAITING CONFIG RELOAD

JSCA 🪷
