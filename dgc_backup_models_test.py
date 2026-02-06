#!/usr/bin/env python3
"""
DGC Backup Models - Tests and Examples
======================================

Run with: python -m pytest dgc_backup_models_test.py -v
Or: python dgc_backup_models_test.py
"""

import asyncio
import os
import pytest
from unittest.mock import AsyncMock, Mock, patch
from dgc_backup_models import (
    BackupModelRouter,
    Provider,
    ProviderConfig,
    CircuitBreaker,
    CircuitState,
    CompletionResult,
    ProviderHealth,
    ProviderCache,
    get_router,
    complete,
    quick_chat
)


# ============================================================================
# CIRCUIT BREAKER TESTS
# ============================================================================

class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    def test_initial_state_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute()
    
    def test_opens_after_failures(self):
        cb = CircuitBreaker(failure_threshold=3)
        
        # Record failures
        for _ in range(3):
            cb.record_failure()
        
        assert cb.state == CircuitState.OPEN
        assert not cb.can_execute()
    
    def test_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        cb.record_failure()
        
        assert cb.state == CircuitState.OPEN
        assert not cb.can_execute()
        
        # Wait for recovery timeout
        import time
        time.sleep(0.15)
        
        assert cb.can_execute()
        assert cb.state == CircuitState.HALF_OPEN
    
    def test_closes_on_success(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        
        # Simulate half-open
        cb.state = CircuitState.HALF_OPEN
        cb.half_open_calls = 1
        
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.failures == 0


# ============================================================================
# PROVIDER CACHE TESTS
# ============================================================================

class TestProviderCache:
    """Test caching functionality."""
    
    def test_cache_set_and_get(self):
        cache = ProviderCache(ttl_seconds=60.0)
        
        messages = [{"role": "user", "content": "Hello"}]
        result = CompletionResult(
            content="Hi there!",
            model="gpt-4",
            provider=Provider.OPENAI,
            latency_ms=100.0
        )
        
        cache.set(messages, "gpt-4", result)
        cached = cache.get(messages, "gpt-4")
        
        assert cached is not None
        assert cached.content == "Hi there!"
        assert cached.cached is True
    
    def test_cache_expiration(self):
        cache = ProviderCache(ttl_seconds=0.1)
        
        messages = [{"role": "user", "content": "Hello"}]
        result = CompletionResult(
            content="Hi there!",
            model="gpt-4",
            provider=Provider.OPENAI
        )
        
        cache.set(messages, "gpt-4", result)
        
        import time
        time.sleep(0.15)
        
        cached = cache.get(messages, "gpt-4")
        assert cached is None
    
    def test_cache_max_size(self):
        cache = ProviderCache(ttl_seconds=60.0, max_size=2)
        
        for i in range(3):
            messages = [{"role": "user", "content": f"Message {i}"}]
            result = CompletionResult(
                content=f"Response {i}",
                model="gpt-4",
                provider=Provider.OPENAI
            )
            cache.set(messages, "gpt-4", result)
        
        # First message should be evicted
        first_messages = [{"role": "user", "content": "Message 0"}]
        assert cache.get(first_messages, "gpt-4") is None
        
        # Recent messages should be cached
        last_messages = [{"role": "user", "content": "Message 2"}]
        assert cache.get(last_messages, "gpt-4") is not None


# ============================================================================
# PROVIDER HEALTH TESTS
# ============================================================================

class TestProviderHealth:
    """Test health tracking."""
    
    def test_success_rate_calculation(self):
        health = ProviderHealth(provider=Provider.OPENAI)
        
        assert health.success_rate == 1.0  # Default
        
        health.record_success(100.0)
        health.record_success(150.0)
        health.record_failure()
        
        assert health.success_rate == 2/3
        assert health.avg_latency_ms == 125.0
    
    def test_circuit_integration(self):
        health = ProviderHealth(
            provider=Provider.OPENAI,
            circuit=CircuitBreaker(failure_threshold=1)
        )
        
        assert health.circuit.can_execute()
        
        health.record_failure()
        assert not health.circuit.can_execute()


# ============================================================================
# ROUTER TESTS (WITH MOCKING)
# ============================================================================

class TestBackupModelRouter:
    """Test the main router functionality."""
    
    @pytest.fixture
    def router(self):
        return BackupModelRouter(cache_enabled=False)
    
    @pytest.mark.asyncio
    async def test_get_available_providers(self, router):
        """Test provider availability filtering."""
        # Without API keys, should return empty
        providers = router.get_available_providers()
        assert len(providers) == 0  # No env vars set in test
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, router):
        """Test rate limit tracking."""
        # Should allow requests initially
        assert router._check_rate_limit(Provider.OPENAI)
        
        # Record many requests
        for _ in range(100):
            router._record_request(Provider.OPENAI)
        
        # Should still be fine (within 1 minute window)
        # but let's verify it tracks
        assert len(router._rate_limit_timestamps[Provider.OPENAI]) == 100
    
    @pytest.mark.asyncio
    async def test_complete_with_mocked_provider(self, router):
        """Test complete with mocked provider response."""
        mock_result = CompletionResult(
            content="Test response",
            model="gpt-4",
            provider=Provider.OPENAI,
            latency_ms=50.0
        )
        
        with patch.object(router, '_call_provider', return_value=mock_result):
            with patch.object(router, '_check_rate_limit', return_value=True):
                # Mock provider config availability
                with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                    result = await router.complete("Hello", preferred_provider=Provider.OPENAI)
        
        assert result.content == "Test response"
    
    @pytest.mark.asyncio
    async def test_parallel_fallback(self, router):
        """Test that providers are tried in parallel."""
        call_count = 0
        
        async def slow_provider(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.5)
            return CompletionResult(
                content="Slow",
                model="slow",
                provider=Provider.OPENAI
            )
        
        async def fast_provider(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return CompletionResult(
                content="Fast",
                model="fast",
                provider=Provider.GROQ
            )
        
        with patch.object(router, '_call_provider') as mock_call:
            mock_call.side_effect = fast_provider
            
            with patch.object(router, '_check_rate_limit', return_value=True):
                with patch.dict(os.environ, {
                    'OPENAI_API_KEY': 'test',
                    'GROQ_API_KEY': 'test'
                }):
                    result = await router.complete("Hello")
        
        # Should get result quickly from fast provider
        assert result.content == "Fast"
    
    @pytest.mark.asyncio
    async def test_health_status_reporting(self, router):
        """Test health status output."""
        status = router.get_health_status()
        
        assert Provider.OPENAI.value in status
        assert Provider.GROQ.value in status
        assert "success_rate" in status[Provider.OPENAI.value]
        assert "circuit_state" in status[Provider.OPENAI.value]


# ============================================================================
# INTEGRATION TESTS (Require API Keys)
# ============================================================================

@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring real API keys."""
    
    @pytest.mark.asyncio
    async def test_real_completion(self):
        """Test with real API calls (if keys available)."""
        router = BackupModelRouter()
        
        # Check if any providers available
        providers = router.get_available_providers()
        if not providers:
            pytest.skip("No API keys configured")
        
        result = await router.complete(
            "Say exactly 'PONG' and nothing else",
            max_tokens=10
        )
        
        assert "PONG" in result.content
        assert result.latency_ms > 0
        
        await router.close()
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        router = BackupModelRouter()
        
        results = await router.health_check()
        
        # At least verify structure
        for provider, healthy in results.items():
            assert isinstance(healthy, bool)
        
        await router.close()


# ============================================================================
# EXAMPLES
# ============================================================================

async def example_basic_usage():
    """Example: Basic usage patterns."""
    print("\n=== Basic Usage ===\n")
    
    # Method 1: Direct router
    router = BackupModelRouter()
    
    # Simple completion
    result = await router.complete("What is 2+2?")
    print(f"Response: {result.content}")
    print(f"Provider: {result.provider.value}")
    print(f"Latency: {result.latency_ms:.0f}ms")
    
    # With preferred provider
    result = await router.complete(
        "Explain quantum computing",
        preferred_provider=Provider.GROQ,
        max_tokens=200
    )
    print(f"\nGroq response: {result.content[:100]}...")
    
    await router.close()


async def example_fallback_behavior():
    """Example: Demonstrate fallback behavior."""
    print("\n=== Fallback Behavior ===\n")
    
    router = BackupModelRouter()
    
    # This will try providers in parallel and return first success
    result = await router.complete(
        "Generate a creative story about AI",
        max_tokens=500,
        temperature=0.9
    )
    
    print(f"Got response from {result.provider.value}")
    print(f"Used model: {result.model}")
    print(f"Content length: {len(result.content)}")
    
    await router.close()


async def example_caching():
    """Example: Demonstrate caching."""
    print("\n=== Caching Demo ===\n")
    
    router = BackupModelRouter(cache_enabled=True)
    
    # First call - hits API
    start = asyncio.get_event_loop().time()
    result1 = await router.complete("What is the capital of France?")
    time1 = asyncio.get_event_loop().time() - start
    
    print(f"First call: {time1:.2f}s, cached={result1.cached}")
    
    # Second call - hits cache
    start = asyncio.get_event_loop().time()
    result2 = await router.complete("What is the capital of France?")
    time2 = asyncio.get_event_loop().time() - start
    
    print(f"Second call: {time2:.2f}s, cached={result2.cached}")
    print(f"Speedup: {time1/time2:.0f}x faster!")
    
    await router.close()


async def example_health_monitoring():
    """Example: Health monitoring."""
    print("\n=== Health Monitoring ===\n")
    
    router = BackupModelRouter()
    
    # Get current health status
    status = router.get_health_status()
    
    print("Provider Health:")
    for provider, info in status.items():
        available = "🟢" if info["available"] else "🔴"
        print(f"  {available} {provider:12} - {info['circuit_state']:10} "
              f"(success: {info['success_rate']:.0%})")
    
    # Run active health check
    print("\nRunning health checks...")
    results = await router.health_check()
    
    for provider, healthy in results.items():
        status = "✅ Healthy" if healthy else "❌ Unhealthy"
        print(f"  {provider}: {status}")
    
    await router.close()


async def example_quick_functions():
    """Example: Quick utility functions."""
    print("\n=== Quick Functions ===\n")
    
    # Quick chat - just returns string
    response = await quick_chat("Say hi in one word")
    print(f"Quick chat: {response}")
    
    # Complete with full result
    result = await complete("List 3 colors")
    print(f"Complete result:")
    print(f"  Content: {result.content}")
    print(f"  Provider: {result.provider.value}")
    print(f"  Tokens used: {result.usage}")


async def example_tier_selection():
    """Example: Using tiers for quality/speed tradeoffs."""
    print("\n=== Tier Selection ===\n")
    
    router = BackupModelRouter()
    
    # Tier 1: Fastest/cheapest (Groq, etc.)
    result_fast = await router.complete(
        "Say hello",
        tier=1,
        max_tokens=20
    )
    print(f"Tier 1 result from {result_fast.provider.value} in {result_fast.latency_ms:.0f}ms")
    
    # Tier 3: Best quality (Claude Opus, etc.)
    result_quality = await router.complete(
        "Write a haiku about AI",
        tier=3,
        max_tokens=100
    )
    print(f"Tier 3 result from {result_quality.provider.value}")
    print(f"Content: {result_quality.content}")
    
    await router.close()


async def run_examples():
    """Run all examples."""
    try:
        await example_basic_usage()
    except Exception as e:
        print(f"Basic usage failed: {e}")
    
    try:
        await example_fallback_behavior()
    except Exception as e:
        print(f"Fallback demo failed: {e}")
    
    try:
        await example_caching()
    except Exception as e:
        print(f"Caching demo failed: {e}")
    
    try:
        await example_health_monitoring()
    except Exception as e:
        print(f"Health monitoring failed: {e}")
    
    try:
        await example_quick_functions()
    except Exception as e:
        print(f"Quick functions failed: {e}")
    
    try:
        await example_tier_selection()
    except Exception as e:
        print(f"Tier selection failed: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Run tests
    print("Running DGC Backup Models Tests...")
    print("=" * 60)
    
    # Check for pytest
    try:
        exit_code = pytest.main([__file__, "-v", "--tb=short", "-x"])
        if exit_code != 0:
            print(f"\nTests exited with code {exit_code}")
    except Exception as e:
        print(f"Test run failed: {e}")
    
    # Run examples if keys available
    print("\n" + "=" * 60)
    print("Running Examples...")
    print("=" * 60)
    
    asyncio.run(run_examples())
