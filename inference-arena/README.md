# Inference Arena

A live model comparison dashboard powered by the Universal Inference Runtime.

**Tagline:** 18 models. 1 prompt. You decide who wins.

## Quick Start

```bash
cd inference-arena

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Prerequisites

- Ollama running locally (`ollama serve`)
- At least 2 models pulled (`ollama pull gemma3:4b`, etc.)

## MVP Features (Day 1-2)

- [x] Compare 6 hero models side-by-side
- [x] Simple up/down voting per response
- [x] Example prompt buttons
- [x] Export comparison history
- [ ] Persistent storage (Day 3)
- [ ] Model leaderboard (Day 4)
- [ ] SHAKTI_GINKO integration (Day 5)

## Roadmap

See `SHIPPING_PLAN.md` for the 7-day sprint breakdown.

## Architecture

```
User Prompt → Ollama API → 6 Parallel Queries → Side-by-side Display → Vote
```

Built on the Universal Inference Runtime for hot model swapping.

---

*Day 1 MVP - 2026-02-16*
