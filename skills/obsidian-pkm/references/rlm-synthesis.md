# RLM Synthesis Skill

**Recursive Language Models for Infinite Context Processing**

## What This Does

This skill wraps the RLM (Recursive Language Model) framework to enable OpenClaw to process
contexts far beyond normal token limits. RLM treats large documents as external memory that
the LLM can programmatically navigate, search, and synthesize.

## When to Use

- Processing entire codebases or documentation sets
- Synthesizing information across many files
- Research tasks requiring cross-document analysis
- Any task where context exceeds ~100K tokens

## Capabilities

- **Infinite Context**: Handle 10M+ tokens via recursive decomposition
- **Smart Chunking**: Auto-splits large inputs into manageable pieces
- **Parallel Processing**: Spawns sub-LLM calls for concurrent analysis
- **Self-Verification**: Can fact-check claims against source material

## Usage

```bash
# From command line
rlm-query "Find all mentions of X in this codebase" --path /path/to/files

# Or invoke via OpenClaw skill
/skill:rlm-synthesis "Synthesize the architecture of this project"
```

## Configuration

The skill uses the model hierarchy defined in openclaw.json:
- **Primary**: Kimi K2.5 (256K context, multimodal)
- **Reasoning**: Claude Opus 4.5 (heavy tasks)
- **Fallback**: Gemini 3 Flash, GPT-5.2 Codex

## Python API

```python
from rlm_synthesis import RLMSynthesis

rlm = RLMSynthesis()
result = rlm.query(
    files=["/path/to/files/*.md"],
    question="What is the main architecture?",
    model="kimi-k2.5"  # or "opus", "gemini", "codex"
)
```

## Technical Notes

- RLM is an inference-time wrapper, not a model itself
- Uses Python REPL environment for code execution
- Sub-LLM calls can be parallelized for speed
- Results are cached to avoid redundant API calls

## Dependencies

- `rlm` library (pip install git+https://github.com/alexzhang13/rlm.git)
- OpenRouter API key (for model access)
- Python 3.11+

## Author

Integrated for Dhyana's research system, Feb 2026
