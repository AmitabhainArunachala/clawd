# DGC Backup Models - Quick Reference

## Overview

The `dgc_backup_models.py` module provides a high-performance, fault-tolerant multi-provider LLM fallback system with parallel provider attempts, circuit breakers, and intelligent caching.

## Supported Providers

| Provider | Env Var | Default Model | Speed | Quality |
|----------|---------|---------------|-------|---------|
| **Groq** | `GROQ_API_KEY` | llama-3.1-8b-instant | ⚡ Fastest | ⭐⭐ |
| **OpenAI** | `OPENAI_API_KEY` | gpt-4o-mini | ⚡ Fast | ⭐⭐⭐ |
| **Anthropic** | `ANTHROPIC_API_KEY` | claude-3-haiku | 🐢 Medium | ⭐⭐⭐⭐ |
| **Together** | `TOGETHER_API_KEY` | llama-3.1-8B | ⚡ Fast | ⭐⭐ |
| **Moonshot** | `MOONSHOT_API_KEY` | kimi-k2.5 | 🐢 Slow | ⭐⭐⭐⭐⭐ |
| **Google** | `GOOGLE_API_KEY` | gemini-1.5-flash | ⚡ Fast | ⭐⭐⭐ |

## Quick Start

### Basic Usage

```python
from dgc_backup_models import BackupModelRouter, complete, quick_chat

# Method 1: Direct router (recommended for apps)
router = BackupModelRouter()
result = await router.complete("What is the meaning of life?")
print(result.content)  # The answer
print(result.provider)  # Which provider succeeded
print(result.latency_ms)  # How long it took
await router.close()

# Method 2: Quick chat (just the string)
response = await quick_chat("Say hello")

# Method 3: Singleton
result = await complete("Your message here")
```

### With Options

```python
result = await router.complete(
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    preferred_provider=Provider.GROQ,  # Try this first
    preferred_model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=1000,
    tier=2  # 1=fast/cheap, 3=best quality
)
```

## Key Features

### 1. Parallel Fallback

Instead of trying providers one-by-one (slow), the router tries multiple providers in parallel and returns the first successful response.

```python
# Tries top 3 providers simultaneously
router = BackupModelRouter(parallel_attempts=3)
```

### 2. Circuit Breakers

Automatically stops using failing providers and periodically tests recovery.

```python
# Check provider health
status = router.get_health_status()
# Returns:
# {
#   "groq": {"circuit_state": "closed", "success_rate": 0.98, ...},
#   "openai": {"circuit_state": "open", "success_rate": 0.0, ...}
# }
```

### 3. Caching

Caches identical requests to save money and latency.

```python
router = BackupModelRouter(cache_enabled=True, cache_ttl_seconds=300)
# Second identical request returns instantly from cache
```

### 4. Tier Selection

Filter providers by quality/speed tier:

```python
# Only use fast/cheap providers (tier 1)
result = await router.complete("Quick question", tier=1)

# Use best quality (tier 3)
result = await router.complete("Complex analysis", tier=3)
```

### 5. Health Checks

Active health monitoring:

```python
results = await router.health_check()
# {Provider.GROQ: True, Provider.OPENAI: False, ...}
```

## Environment Setup

```bash
# Add to your .env or export:
export GROQ_API_KEY="gsk_..."
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export TOGETHER_API_KEY="..."
export MOONSHOT_API_KEY="..."
export GOOGLE_API_KEY="..."
```

## Testing

```bash
# Run all tests
python dgc_backup_models_test.py

# Run with pytest
pytest dgc_backup_models_test.py -v

# Run only unit tests (no API calls)
pytest dgc_backup_models_test.py -v -m "not integration"

# Run integration tests (requires API keys)
pytest dgc_backup_models_test.py -v -m integration
```

## Architecture

```
User Request
     │
     ▼
┌─────────────────┐
│  Cache Check    │◄──────┐
└─────────────────┘       │
     │                    │
     ▼                    │
┌─────────────────┐       │
│ Get Available   │       │
│  Providers      │       │
└─────────────────┘       │
     │                    │
     ▼                    │
┌─────────────────┐       │
│ Circuit Breaker │       │
│   Filter        │       │
└─────────────────┘       │
     │                    │
     ▼                    │
┌─────────────────┐       │
│  Parallel Call  │       │
│   (Race them)   │       │
└─────────────────┘       │
     │                    │
     ▼                    │
┌─────────────────┐       │
│ Return First    │       │
│   Success       │───────┘
└─────────────────┘
```

## Performance Tips

1. **Use caching** for repeated queries
2. **Set tier=1** for speed-critical paths
3. **Set tier=3** for quality-critical paths
4. **Use Groq** for fastest responses (< 100ms typical)
5. **Use Moonshot** for complex reasoning tasks

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No providers available | Check API keys in environment |
| All requests failing | Check circuit breaker status |
| High latency | Reduce tier, enable caching |
| Rate limit errors | Router handles this automatically |
| Inconsistent results | Check which provider responded |

## Integration Example

```python
# In your application
from dgc_backup_models import BackupModelRouter, Provider

class MyAgent:
    def __init__(self):
        self.llm = BackupModelRouter(
            cache_enabled=True,
            parallel_attempts=3
        )
    
    async def think(self, prompt: str) -> str:
        result = await self.llm.complete(
            prompt,
            preferred_provider=Provider.GROQ,
            tier=2,
            max_tokens=500
        )
        return result.content
    
    async def deep_think(self, prompt: str) -> str:
        result = await self.llm.complete(
            prompt,
            tier=3,  # Best quality
            max_tokens=2000
        )
        return result.content
```

JSCA! Jai Ma 🪷
