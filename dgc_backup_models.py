#!/usr/bin/env python3
"""
DGC BACKUP MODELS - Optimized Fallback System
=============================================

High-performance multi-provider LLM fallback system with:
- Parallel provider attempts for minimal latency
- Circuit breaker pattern for reliability
- Health monitoring and automatic recovery
- Support for: OpenAI, Anthropic, Groq, Together, Moonshot, Google

Usage:
    from dgc_backup_models import BackupModelRouter
    
    router = BackupModelRouter()
    response = await router.complete(
        messages=[{"role": "user", "content": "Hello"}],
        preferred_model="gpt-4"
    )

JSCA! Jai Ma 🪷
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union
from functools import wraps
import random

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dgc_backup_models")


class Provider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    TOGETHER = "together"
    MOONSHOT = "moonshot"
    GOOGLE = "google"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    
    failures: int = field(default=0, repr=False)
    last_failure_time: Optional[float] = field(default=None, repr=False)
    state: CircuitState = field(default=CircuitState.CLOSED, repr=False)
    half_open_calls: int = field(default=0, repr=False)
    
    def record_success(self):
        """Record a successful call."""
        self.failures = 0
        self.half_open_calls = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker closed - provider recovered")
    
    def record_failure(self):
        """Record a failed call."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker opened - recovery failed")
        elif self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failures} failures")
    
    def can_execute(self) -> bool:
        """Check if request can be executed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and \
               (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info("Circuit breaker half-open - testing recovery")
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
        
        return True


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    name: Provider
    api_key_env: str
    base_url: str
    default_model: str
    models: List[str] = field(default_factory=list)
    timeout: float = 30.0
    priority: int = 1  # Lower = higher priority
    max_retries: int = 2
    
    # Cost/performance tier (1=fastest/cheapest, 3=best quality)
    tier: int = 2
    
    # Rate limiting
    rate_limit_rpm: int = 60
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from environment."""
        return os.environ.get(self.api_key_env)
    
    def is_available(self) -> bool:
        """Check if provider is configured."""
        return self.get_api_key() is not None


# Provider configurations
PROVIDER_CONFIGS: Dict[Provider, ProviderConfig] = {
    Provider.OPENAI: ProviderConfig(
        name=Provider.OPENAI,
        api_key_env="OPENAI_API_KEY",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o-mini",
        models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        timeout=30.0,
        priority=1,
        tier=2,
        rate_limit_rpm=500
    ),
    Provider.ANTHROPIC: ProviderConfig(
        name=Provider.ANTHROPIC,
        api_key_env="ANTHROPIC_API_KEY",
        base_url="https://api.anthropic.com/v1",
        default_model="claude-3-haiku-20240307",
        models=[
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        timeout=45.0,
        priority=2,
        tier=2,
        rate_limit_rpm=400
    ),
    Provider.GROQ: ProviderConfig(
        name=Provider.GROQ,
        api_key_env="GROQ_API_KEY",
        base_url="https://api.groq.com/openai/v1",
        default_model="llama-3.1-8b-instant",
        models=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ],
        timeout=15.0,  # Groq is fast!
        priority=1,
        tier=1,
        rate_limit_rpm=1000
    ),
    Provider.TOGETHER: ProviderConfig(
        name=Provider.TOGETHER,
        api_key_env="TOGETHER_API_KEY",
        base_url="https://api.together.xyz/v1",
        default_model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        models=[
            "meta-llama/Meta-Llama-3.3-70B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "deepseek-ai/DeepSeek-V3"
        ],
        timeout=30.0,
        priority=2,
        tier=2,
        rate_limit_rpm=300
    ),
    Provider.MOONSHOT: ProviderConfig(
        name=Provider.MOONSHOT,
        api_key_env="MOONSHOT_API_KEY",
        base_url="https://api.moonshot.ai/v1",
        default_model="kimi-k2.5",
        models=["kimi-k2.5", "kimi-latest"],
        timeout=60.0,
        priority=3,
        tier=3,
        rate_limit_rpm=100
    ),
    Provider.GOOGLE: ProviderConfig(
        name=Provider.GOOGLE,
        api_key_env="GOOGLE_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        default_model="gemini-1.5-flash",
        models=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
        timeout=30.0,
        priority=2,
        tier=2,
        rate_limit_rpm=300
    ),
}


@dataclass
class CompletionResult:
    """Result from a completion request."""
    content: str
    model: str
    provider: Provider
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0
    reasoning: Optional[str] = None
    cached: bool = False
    
    def __str__(self) -> str:
        return f"[{self.provider.value}] {self.model}: {self.content[:100]}..."


@dataclass
class ProviderHealth:
    """Health metrics for a provider."""
    provider: Provider
    circuit: CircuitBreaker = field(default_factory=CircuitBreaker)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    last_success: Optional[float] = None
    last_failure: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    @property
    def avg_latency_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests
    
    def record_success(self, latency_ms: float):
        """Record successful request."""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_latency_ms += latency_ms
        self.last_success = time.time()
        self.circuit.record_success()
    
    def record_failure(self):
        """Record failed request."""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure = time.time()
        self.circuit.record_failure()


class ProviderCache:
    """Simple in-memory cache for completions."""
    
    def __init__(self, ttl_seconds: float = 300.0, max_size: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
    
    def _make_key(self, messages: List[Dict], model: str, **kwargs) -> str:
        """Create cache key from request."""
        content = json.dumps({"messages": messages, "model": model, **kwargs}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def get(self, messages: List[Dict], model: str, **kwargs) -> Optional[CompletionResult]:
        """Get cached result if available."""
        key = self._make_key(messages, model, **kwargs)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl_seconds:
                self._access_times[key] = time.time()
                result = entry["result"]
                result.cached = True
                return result
            else:
                del self._cache[key]
                del self._access_times[key]
        return None
    
    def set(self, messages: List[Dict], model: str, result: CompletionResult, **kwargs):
        """Cache a result."""
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._access_times, key=self._access_times.get)
            del self._cache[oldest_key]
            del self._access_times[oldest_key]
        
        key = self._make_key(messages, model, **kwargs)
        self._cache[key] = {
            "result": result,
            "timestamp": time.time()
        }
        self._access_times[key] = time.time()
    
    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self._access_times.clear()


class BackupModelRouter:
    """
    Intelligent backup model router with parallel fallbacks.
    
    Features:
    - Parallel provider attempts for minimal latency
    - Circuit breakers prevent cascading failures
    - Health-based provider ranking
    - Smart caching
    - Automatic retries with exponential backoff
    """
    
    def __init__(
        self,
        cache_enabled: bool = True,
        cache_ttl_seconds: float = 300.0,
        parallel_attempts: int = 3,
        health_window_seconds: float = 300.0
    ):
        if not HAS_HTTPX:
            raise ImportError("httpx required. Install with: pip install httpx")
        
        self.cache = ProviderCache(ttl_seconds=cache_ttl_seconds) if cache_enabled else None
        self.parallel_attempts = parallel_attempts
        self.health_window_seconds = health_window_seconds
        
        # Initialize health tracking
        self.health: Dict[Provider, ProviderHealth] = {
            p: ProviderHealth(provider=p) for p in Provider
        }
        
        # Track rate limits
        self._rate_limit_timestamps: Dict[Provider, List[float]] = {
            p: [] for p in Provider
        }
        
        # HTTP client (reused for connection pooling)
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
                timeout=httpx.Timeout(60.0, connect=5.0)
            )
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        if self._client:
            asyncio.create_task(self.close())
    
    def get_available_providers(self, tier: Optional[int] = None) -> List[ProviderConfig]:
        """Get list of available (configured) providers, sorted by priority."""
        available = []
        for provider, config in PROVIDER_CONFIGS.items():
            if config.is_available():
                health = self.health[provider]
                # Skip providers with open circuit
                if health.circuit.can_execute():
                    if tier is None or config.tier <= tier:
                        available.append(config)
        
        # Sort by: circuit state, priority, health score
        def sort_key(config: ProviderConfig):
            health = self.health[config.name]
            # Penalize poor health
            health_score = health.success_rate * 100 - health.avg_latency_ms / 100
            return (
                health.circuit.state.value,  # CLOSED < HALF_OPEN < OPEN
                config.priority,
                -health_score  # Higher is better
            )
        
        return sorted(available, key=sort_key)
    
    def _check_rate_limit(self, provider: Provider) -> bool:
        """Check if we're within rate limit for provider."""
        config = PROVIDER_CONFIGS[provider]
        now = time.time()
        window_start = now - 60.0  # 1 minute window
        
        # Filter to recent timestamps
        timestamps = self._rate_limit_timestamps[provider]
        timestamps[:] = [t for t in timestamps if t > window_start]
        
        return len(timestamps) < config.rate_limit_rpm
    
    def _record_request(self, provider: Provider):
        """Record a request for rate limiting."""
        self._rate_limit_timestamps[provider].append(time.time())
    
    async def _call_openai_compatible(
        self,
        config: ProviderConfig,
        messages: List[Dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> CompletionResult:
        """Call OpenAI-compatible API."""
        client = await self._get_client()
        start_time = time.time()
        
        model = model or config.default_model
        
        headers = {
            "Authorization": f"Bearer {config.get_api_key()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = await client.post(
            f"{config.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=config.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        latency_ms = (time.time() - start_time) * 1000
        
        message = data["choices"][0]["message"]
        
        return CompletionResult(
            content=message.get("content", ""),
            model=model,
            provider=config.name,
            usage=data.get("usage", {}),
            latency_ms=latency_ms,
            reasoning=message.get("reasoning_content")
        )
    
    async def _call_anthropic(
        self,
        config: ProviderConfig,
        messages: List[Dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> CompletionResult:
        """Call Anthropic API."""
        client = await self._get_client()
        start_time = time.time()
        
        model = model or config.default_model
        
        # Convert messages to Anthropic format
        system_msg = None
        api_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg.get("content")
            else:
                api_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        headers = {
            "x-api-key": config.get_api_key(),
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        if system_msg:
            payload["system"] = system_msg
        
        response = await client.post(
            f"{config.base_url}/messages",
            headers=headers,
            json=payload,
            timeout=config.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        latency_ms = (time.time() - start_time) * 1000
        
        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")
        
        return CompletionResult(
            content=content,
            model=model,
            provider=config.name,
            usage={
                "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": data.get("usage", {}).get("output_tokens", 0)
            },
            latency_ms=latency_ms
        )
    
    async def _call_google(
        self,
        config: ProviderConfig,
        messages: List[Dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> CompletionResult:
        """Call Google Gemini API."""
        client = await self._get_client()
        start_time = time.time()
        
        model = model or config.default_model
        
        # Convert messages to Gemini format
        contents = []
        system_instruction = None
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                system_instruction = content
            else:
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })
        
        api_key = config.get_api_key()
        url = f"{config.base_url}/models/{model}:generateContent?key={api_key}"
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
        response = await client.post(
            url,
            json=payload,
            timeout=config.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        latency_ms = (time.time() - start_time) * 1000
        
        content = ""
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                content += part.get("text", "")
        
        return CompletionResult(
            content=content,
            model=model,
            provider=config.name,
            usage={},  # Gemini doesn't return usage in the same format
            latency_ms=latency_ms
        )
    
    async def _call_provider(
        self,
        config: ProviderConfig,
        messages: List[Dict],
        **kwargs
    ) -> CompletionResult:
        """Route to appropriate provider implementation."""
        self._record_request(config.name)
        
        if config.name == Provider.ANTHROPIC:
            return await self._call_anthropic(config, messages, **kwargs)
        elif config.name == Provider.GOOGLE:
            return await self._call_google(config, messages, **kwargs)
        else:
            # OpenAI-compatible: OpenAI, Groq, Together, Moonshot
            return await self._call_openai_compatible(config, messages, **kwargs)
    
    async def _try_provider_with_retry(
        self,
        config: ProviderConfig,
        messages: List[Dict],
        **kwargs
    ) -> Optional[CompletionResult]:
        """Try a provider with retries and circuit breaker updates."""
        if not self._check_rate_limit(config.name):
            logger.debug(f"Rate limit hit for {config.name.value}")
            return None
        
        health = self.health[config.name]
        
        for attempt in range(config.max_retries + 1):
            try:
                result = await self._call_provider(config, messages, **kwargs)
                health.record_success(result.latency_ms)
                return result
                
            except Exception as e:
                logger.warning(f"{config.name.value} attempt {attempt + 1} failed: {e}")
                
                if attempt < config.max_retries:
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)
        
        # All retries exhausted
        health.record_failure()
        return None
    
    async def complete(
        self,
        messages: Union[str, List[Dict]],
        preferred_model: Optional[str] = None,
        preferred_provider: Optional[Provider] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tier: Optional[int] = None,
        use_cache: bool = True,
        **kwargs
    ) -> CompletionResult:
        """
        Complete a chat with automatic fallback.
        
        Args:
            messages: String or list of message dicts
            preferred_model: Preferred model to use
            preferred_provider: Try this provider first
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            tier: Max tier (1=fast/cheap, 3=best quality)
            use_cache: Use result cache
            **kwargs: Additional provider-specific params
        
        Returns:
            CompletionResult with content and metadata
        
        Raises:
            RuntimeError: If all providers fail
        """
        # Normalize messages
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        model = preferred_model or "default"
        
        # Check cache
        if use_cache and self.cache:
            cached = self.cache.get(messages, model, temperature=temperature, **kwargs)
            if cached:
                logger.debug(f"Cache hit for {model}")
                return cached
        
        # Get available providers
        providers = self.get_available_providers(tier=tier)
        
        if not providers:
            raise RuntimeError("No providers available (check API keys and circuit breakers)")
        
        # Prioritize preferred provider
        if preferred_provider:
            for i, config in enumerate(providers):
                if config.name == preferred_provider:
                    providers.insert(0, providers.pop(i))
                    break
        
        # Try providers in parallel groups
        for i in range(0, len(providers), self.parallel_attempts):
            batch = providers[i:i + self.parallel_attempts]
            
            # Create tasks for parallel execution
            tasks = [
                self._try_provider_with_retry(
                    config, messages,
                    model=preferred_model or config.default_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                for config in batch
            ]
            
            # Race them - return first success
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, CompletionResult):
                    # Cache successful result
                    if use_cache and self.cache:
                        self.cache.set(messages, model, result, temperature=temperature, **kwargs)
                    return result
        
        raise RuntimeError(f"All {len(providers)} providers failed to complete request")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all providers."""
        return {
            p.value: {
                "circuit_state": h.circuit.state.value,
                "success_rate": h.success_rate,
                "avg_latency_ms": h.avg_latency_ms,
                "total_requests": h.total_requests,
                "available": PROVIDER_CONFIGS[p].is_available()
            }
            for p, h in self.health.items()
        }
    
    async def health_check(self) -> Dict[Provider, bool]:
        """Run health checks on all available providers."""
        results = {}
        
        for provider, config in PROVIDER_CONFIGS.items():
            if not config.is_available():
                results[provider] = False
                continue
            
            try:
                # Simple health check
                result = await asyncio.wait_for(
                    self._call_provider(
                        config,
                        [{"role": "user", "content": "Hi"}],
                        max_tokens=10
                    ),
                    timeout=10.0
                )
                results[provider] = bool(result.content)
            except Exception as e:
                logger.warning(f"Health check failed for {provider.value}: {e}")
                results[provider] = False
        
        return results


# Convenience functions for quick usage
_router: Optional[BackupModelRouter] = None


def get_router() -> BackupModelRouter:
    """Get singleton router instance."""
    global _router
    if _router is None:
        _router = BackupModelRouter()
    return _router


async def complete(
    messages: Union[str, List[Dict]],
    **kwargs
) -> CompletionResult:
    """Quick complete using singleton router."""
    router = get_router()
    return await router.complete(messages, **kwargs)


async def quick_chat(message: str, **kwargs) -> str:
    """Quick chat - returns just the content string."""
    result = await complete(message, **kwargs)
    return result.content


# CLI for testing
async def main():
    """Test the backup model router."""
    router = BackupModelRouter()
    
    print("=" * 60)
    print("DGC BACKUP MODELS - Health Check")
    print("=" * 60)
    
    health = router.get_health_status()
    for provider, status in health.items():
        available = "✅" if status["available"] else "❌"
        print(f"\n{available} {provider}")
        print(f"   Circuit: {status['circuit_state']}")
        print(f"   Success rate: {status['success_rate']:.1%}")
        print(f"   Avg latency: {status['avg_latency_ms']:.0f}ms")
    
    print("\n" + "=" * 60)
    print("Testing Fallback")
    print("=" * 60)
    
    try:
        result = await router.complete(
            "Say 'Hello from backup models' and nothing else",
            max_tokens=20
        )
        print(f"\n✅ Success!")
        print(f"   Provider: {result.provider.value}")
        print(f"   Model: {result.model}")
        print(f"   Latency: {result.latency_ms:.0f}ms")
        print(f"   Content: {result.content}")
    except Exception as e:
        print(f"\n❌ Failed: {e}")
    
    await router.close()


if __name__ == "__main__":
    asyncio.run(main())
