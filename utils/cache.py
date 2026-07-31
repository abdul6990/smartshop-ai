"""
In-Memory Caching Layer
If Redis is not available, falls back to in-memory caching
"""
import json
import time
import asyncio
import inspect
from typing import Optional, Any, Callable
from functools import wraps
from utils.logger import app_logger
import os

class CacheManager:
    def __init__(self):
        """Initialize cache manager"""
        self.use_redis = os.getenv("REDIS_URL", "").strip() != ""
        self.redis_client = None
        self.memory_cache: dict = {}
        
        if self.use_redis:
            try:
                import redis
                self.redis_client = redis.from_url(os.getenv("REDIS_URL"), socket_connect_timeout=2, socket_timeout=2)
                self.redis_client.ping()
                app_logger.info("✅ Redis cache connected")
            except Exception as e:
                app_logger.warning(f"Redis not available, using memory cache: {e}")
                self.use_redis = False
                self.redis_client = None
                self.use_redis = False
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set cache value with TTL (in seconds)
        ttl: Time to live in seconds (default 5 minutes)
        """
        try:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            
            if self.use_redis and self.redis_client:
                self.redis_client.setex(key, ttl, serialized)
            else:
                # Memory cache with expiry time
                self.memory_cache[key] = {
                    "value": serialized,
                    "expires_at": time.time() + ttl
                }
            
            return True
        except Exception as e:
            app_logger.error(f"Cache set failed for {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.use_redis and self.redis_client:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            else:
                # Memory cache with expiry check
                if key in self.memory_cache:
                    entry = self.memory_cache[key]
                    if time.time() < entry["expires_at"]:
                        return json.loads(entry["value"])
                    else:
                        del self.memory_cache[key]
            
            return None
        except Exception as e:
            app_logger.error(f"Cache get failed for {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
            
            return True
        except Exception as e:
            app_logger.error(f"Cache delete failed for {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            
            app_logger.info("✅ Cache cleared")
            return True
        except Exception as e:
            app_logger.error(f"Cache clear failed: {e}")
            return False
    
    def get_or_compute(self, key: str, compute_fn: Callable, ttl: int = 300) -> Any:
        """
        Get from cache or compute and store
        Useful for lazy evaluation
        """
        # Try to get from cache
        cached = self.get(key)
        if cached is not None:
            app_logger.debug(f"🔄 Cache hit: {key}")
            return cached
        
        # Compute new value
        app_logger.debug(f"🔄 Cache miss: {key}, computing...")
        result = compute_fn()
        
        # Store in cache
        self.set(key, result, ttl)
        return result


# Global cache instance
cache = CacheManager()


# ────────── DECORATORS ──────────

def cached(ttl: int = 300, key_prefix: str = "cache"):
    """
    Decorator to cache function results (supports both sync and async functions)
    
    Usage:
        @cached(ttl=300, key_prefix="deals")
        async def get_deals():
            return await expensive_operation()
    """
    def decorator(func: Callable) -> Callable:
        # Check if function is async
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                # Build unique cache key
                cache_key = f"{key_prefix}:{func.__name__}"
                
                # Add args/kwargs to key if needed
                if args:
                    cache_key += f":{'_'.join(str(a) for a in args)}"
                if kwargs:
                    cache_key += f":{'_'.join(f'{k}={v}' for k, v in kwargs.items())}"
                
                # Try cache first
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    app_logger.debug(f"📦 Cache HIT: {cache_key}")
                    return cached_result
                
                # Compute and cache (await the async function)
                result = await func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                app_logger.debug(f"📦 Cache MISS (computed): {cache_key}")
                
                return result
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                # Build unique cache key
                cache_key = f"{key_prefix}:{func.__name__}"
                
                # Add args/kwargs to key if needed
                if args:
                    cache_key += f":{'_'.join(str(a) for a in args)}"
                if kwargs:
                    cache_key += f":{'_'.join(f'{k}={v}' for k, v in kwargs.items())}"
                
                # Try cache first
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    app_logger.debug(f"📦 Cache HIT: {cache_key}")
                    return cached_result
                
                # Compute and cache
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                app_logger.debug(f"📦 Cache MISS (computed): {cache_key}")
                
                return result
            return sync_wrapper
    return decorator


def cache_invalidate(key_prefix: str):
    """
    Decorator to invalidate cache when function succeeds (supports both sync and async)
    
    Usage:
        @cache_invalidate("deals")
        async def update_deals():
            return await save_deals()
    """
    def decorator(func: Callable) -> Callable:
        # Check if function is async
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                result = await func(*args, **kwargs)
                
                # Invalidate cache with this prefix
                if hasattr(cache, 'redis_client') and cache.redis_client:
                    # Redis: delete by pattern
                    keys = cache.redis_client.keys(f"{key_prefix}:*")
                    if keys:
                        cache.redis_client.delete(*keys)
                        app_logger.debug(f"🗑️ Invalidated {len(keys)} cache keys with prefix: {key_prefix}")
                else:
                    # Memory cache: delete matching keys
                    matching_keys = [k for k in cache.memory_cache.keys() if k.startswith(key_prefix)]
                    for k in matching_keys:
                        del cache.memory_cache[k]
                    if matching_keys:
                        app_logger.debug(f"🗑️ Invalidated {len(matching_keys)} cache keys with prefix: {key_prefix}")
                
                return result
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                result = func(*args, **kwargs)
                
                # Invalidate cache with this prefix
                if hasattr(cache, 'redis_client') and cache.redis_client:
                    # Redis: delete by pattern
                    keys = cache.redis_client.keys(f"{key_prefix}:*")
                    if keys:
                        cache.redis_client.delete(*keys)
                        app_logger.debug(f"🗑️ Invalidated {len(keys)} cache keys with prefix: {key_prefix}")
                else:
                    # Memory cache: delete matching keys
                    matching_keys = [k for k in cache.memory_cache.keys() if k.startswith(key_prefix)]
                    for k in matching_keys:
                        del cache.memory_cache[k]
                    if matching_keys:
                        app_logger.debug(f"🗑️ Invalidated {len(matching_keys)} cache keys with prefix: {key_prefix}")
                
                return result
            return sync_wrapper
    return decorator
