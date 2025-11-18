#!/usr/bin/env python3
"""
Redis Caching Layer for LGS Question Generation
Implements intelligent caching with cache key strategies and pre-generation pools
"""

import json
import hashlib
import time
import pickle
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import asyncio
from datetime import datetime, timedelta
import logging

try:
    import redis
    from redis.asyncio import Redis as AsyncRedis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available - using in-memory cache fallback")

@dataclass
class CacheConfig:
    """Redis cache configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    default_ttl: int = 3600  # 1 hour
    max_memory_cache_size: int = 1000

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Dict[str, Any]
    created_at: float
    access_count: int
    quality_score: float
    cache_key: str

class InMemoryCache:
    """Fallback in-memory cache when Redis is unavailable"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.access_log: Dict[str, float] = {}
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache entry"""
        try:
            # Serialize the value
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            
            # Check if we need to evict entries
            if len(self.cache) >= self.max_size:
                await self._evict_lru()
            
            self.cache[key] = CacheEntry(
                data=value,
                created_at=time.time(),
                access_count=0,
                quality_score=0.5,
                cache_key=key
            )
            self.access_log[key] = time.time()
            return True
        except Exception as e:
            logging.error(f"Cache set error: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cache entry"""
        try:
            entry = self.cache.get(key)
            if entry:
                # Check TTL (simple expiration)
                if time.time() - entry.created_at < 3600:  # 1 hour default
                    entry.access_count += 1
                    self.access_log[key] = time.time()
                    return entry.data
                else:
                    # Expired
                    del self.cache[key]
                    if key in self.access_log:
                        del self.access_log[key]
            return None
        except Exception:
            return None
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return key in self.cache
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_log:
            del self.access_log[key]
        return True
    
    async def _evict_lru(self):
        """Evict least recently used entries"""
        if not self.access_log:
            return
        
        # Remove 10% of entries (LRU)
        evict_count = max(1, len(self.cache) // 10)
        sorted_keys = sorted(self.access_log.items(), key=lambda x: x[1])
        
        for key, _ in sorted_keys[:evict_count]:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_log:
                del self.access_log[key]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_accesses = sum(entry.access_count for entry in self.cache.values())
        return {
            'cache_type': 'in_memory',
            'total_keys': len(self.cache),
            'total_accesses': total_accesses,
            'avg_quality_score': sum(entry.quality_score for entry in self.cache.values()) / len(self.cache) if self.cache else 0
        }

class RedisCache:
    """Redis-based cache implementation"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client = None
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'errors': 0
        }
    
    async def connect(self) -> bool:
        """Connect to Redis"""
        try:
            self.redis_client = AsyncRedis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            return True
        except Exception as e:
            logging.error(f"Redis connection failed: {e}")
            return False
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set cache entry with optional TTL"""
        try:
            if not self.redis_client:
                return False
            
            ttl = ttl or self.config.default_ttl
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            
            # Set with expiration
            result = await self.redis_client.setex(key, ttl, serialized_value)
            
            # Store metadata
            metadata_key = f"{key}:meta"
            metadata = {
                'created_at': time.time(),
                'access_count': 0,
                'quality_score': value.get('confidence', 0.5) if isinstance(value, dict) else 0.5
            }
            await self.redis_client.setex(metadata_key, ttl, json.dumps(metadata))
            
            self._stats['sets'] += 1
            return result
        except Exception as e:
            self._stats['errors'] += 1
            logging.error(f"Redis set error: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cache entry"""
        try:
            if not self.redis_client:
                return None
            
            # Get value
            value = await self.redis_client.get(key)
            if value is None:
                self._stats['misses'] += 1
                return None
            
            # Update access count
            metadata_key = f"{key}:meta"
            metadata_str = await self.redis_client.get(metadata_key)
            if metadata_str:
                metadata = json.loads(metadata_str)
                metadata['access_count'] += 1
                await self.redis_client.setex(metadata_key, self.config.default_ttl, json.dumps(metadata))
            
            self._stats['hits'] += 1
            
            # Try to parse as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            self._stats['errors'] += 1
            logging.error(f"Redis get error: {e}")
            return None
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            if not self.redis_client:
                return False
            return await self.redis_client.exists(key) > 0
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry"""
        try:
            if not self.redis_client:
                return False
            
            result = await self.redis_client.delete(key)
            await self.redis_client.delete(f"{key}:meta")  # Delete metadata too
            return result > 0
        except Exception:
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        try:
            if not self.redis_client:
                return {'cache_type': 'redis', 'status': 'disconnected'}
            
            info = await self.redis_client.info()
            hit_rate = self._stats['hits'] / (self._stats['hits'] + self._stats['misses']) * 100 if (self._stats['hits'] + self._stats['misses']) > 0 else 0
            
            return {
                'cache_type': 'redis',
                'status': 'connected',
                'total_keys': info.get('db0', {}).get('keys', 0),
                'memory_usage': info.get('used_memory_human', 'Unknown'),
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': hit_rate,
                'sets': self._stats['sets'],
                'errors': self._stats['errors']
            }
        except Exception as e:
            return {'cache_type': 'redis', 'status': 'error', 'error': str(e)}

class QuestionCacheManager:
    """High-level cache manager for question generation"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.cache: Union[RedisCache, InMemoryCache] = None
        self.is_redis = False
        
        # Pre-generation pools
        self.pregeneration_pools: Dict[str, List[Dict]] = {}
        self.pool_refill_thresholds = {
            'high_frequency': 10,  # Refill when < 10 questions left
            'medium_frequency': 5,
            'low_frequency': 2
        }
    
    async def initialize(self) -> bool:
        """Initialize cache backend"""
        if REDIS_AVAILABLE:
            redis_cache = RedisCache(self.config)
            if await redis_cache.connect():
                self.cache = redis_cache
                self.is_redis = True
                print("✅ Redis cache initialized")
                return True
        
        # Fallback to in-memory cache
        self.cache = InMemoryCache(self.config.max_memory_cache_size)
        self.is_redis = False
        print("⚠️ Using in-memory cache (Redis unavailable)")
        return True
    
    def generate_cache_key(self, subject: str, topic: str, learning_outcome: str, difficulty: str) -> str:
        """Generate cache key for question parameters"""
        key_data = f"{subject}:{topic}:{learning_outcome}:{difficulty}"
        key_hash = hashlib.md5(key_data.encode('utf-8')).hexdigest()
        return f"question:{key_hash}"
    
    def generate_pool_key(self, subject: str, difficulty: str) -> str:
        """Generate key for pre-generation pools"""
        return f"pool:{subject}:{difficulty}"
    
    async def get_cached_question(self, subject: str, topic: str, learning_outcome: str, difficulty: str) -> Optional[Dict]:
        """Get cached question if available"""
        if not self.cache:
            return None
        
        cache_key = self.generate_cache_key(subject, topic, learning_outcome, difficulty)
        return await self.cache.get(cache_key)
    
    async def cache_question(self, question: Dict, subject: str, topic: str, learning_outcome: str, difficulty: str, ttl: int = None) -> bool:
        """Cache a generated question"""
        if not self.cache:
            return False
        
        cache_key = self.generate_cache_key(subject, topic, learning_outcome, difficulty)
        
        # Add cache metadata
        cached_question = {
            **question,
            'cached_at': time.time(),
            'cache_key': cache_key
        }
        
        return await self.cache.set(cache_key, cached_question, ttl)
    
    async def get_from_pool(self, subject: str, difficulty: str) -> Optional[Dict]:
        """Get question from pre-generation pool"""
        pool_key = self.generate_pool_key(subject, difficulty)
        
        if pool_key in self.pregeneration_pools and self.pregeneration_pools[pool_key]:
            question = self.pregeneration_pools[pool_key].pop(0)
            
            # Check if pool needs refilling
            remaining = len(self.pregeneration_pools[pool_key])
            frequency = self._determine_frequency(subject, difficulty)
            threshold = self.pool_refill_thresholds.get(frequency, 5)
            
            if remaining < threshold:
                # Schedule pool refill (would trigger background task in production)
                await self._schedule_pool_refill(subject, difficulty)
            
            return question
        
        return None
    
    async def add_to_pool(self, questions: List[Dict], subject: str, difficulty: str) -> bool:
        """Add questions to pre-generation pool"""
        pool_key = self.generate_pool_key(subject, difficulty)
        
        if pool_key not in self.pregeneration_pools:
            self.pregeneration_pools[pool_key] = []
        
        self.pregeneration_pools[pool_key].extend(questions)
        
        # Limit pool size (keep most recent)
        max_pool_size = 50
        if len(self.pregeneration_pools[pool_key]) > max_pool_size:
            self.pregeneration_pools[pool_key] = self.pregeneration_pools[pool_key][-max_pool_size:]
        
        return True
    
    def _determine_frequency(self, subject: str, difficulty: str) -> str:
        """Determine frequency category for subject/difficulty combination"""
        # Simple heuristic - in production, this would use actual usage statistics
        high_frequency_subjects = ['Türkçe', 'Matematik']
        
        if subject in high_frequency_subjects and difficulty == 'ORTA':
            return 'high_frequency'
        elif subject in high_frequency_subjects:
            return 'medium_frequency'
        else:
            return 'low_frequency'
    
    async def _schedule_pool_refill(self, subject: str, difficulty: str):
        """Schedule background pool refill (placeholder for production implementation)"""
        print(f"📋 Scheduling pool refill for {subject} - {difficulty}")
        # In production, this would trigger a background task or queue job
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        if not self.cache:
            return {'status': 'not_initialized'}
        
        cache_stats = await self.cache.get_stats()
        
        # Add pool statistics
        pool_stats = {}
        for pool_key, questions in self.pregeneration_pools.items():
            pool_stats[pool_key] = {
                'size': len(questions),
                'avg_confidence': sum(q.get('confidence', 0) for q in questions) / len(questions) if questions else 0
            }
        
        return {
            'cache_backend': cache_stats,
            'pregeneration_pools': pool_stats,
            'total_pooled_questions': sum(len(questions) for questions in self.pregeneration_pools.values())
        }
    
    async def clear_cache(self, pattern: Optional[str] = None) -> bool:
        """Clear cache entries (for maintenance)"""
        if not self.cache:
            return False
        
        if self.is_redis and pattern:
            try:
                # Redis-specific pattern clearing
                redis_client = self.cache.redis_client
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)
                return True
            except Exception as e:
                logging.error(f"Cache clear error: {e}")
                return False
        else:
            # Clear entire cache for in-memory implementation
            if hasattr(self.cache, 'cache'):
                self.cache.cache.clear()
                self.cache.access_log.clear()
            return True
    
    async def warm_up_cache(self, common_combinations: List[Dict]) -> Dict[str, int]:
        """Pre-warm cache with common question combinations"""
        results = {'success': 0, 'failed': 0}
        
        for combo in common_combinations:
            try:
                # This would typically generate and cache questions
                # For now, just create cache entries
                cache_key = self.generate_cache_key(
                    combo['subject'],
                    combo['topic'],
                    combo.get('learning_outcome', ''),
                    combo['difficulty']
                )
                
                # Placeholder question for warming
                placeholder_question = {
                    'stem': f"Placeholder question for {combo['subject']} - {combo['difficulty']}",
                    'subject': combo['subject'],
                    'difficulty_level': combo['difficulty'],
                    'cached_at': time.time(),
                    'is_placeholder': True
                }
                
                if await self.cache.set(cache_key, placeholder_question):
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                logging.error(f"Cache warm-up error for {combo}: {e}")
                results['failed'] += 1
        
        return results

# Global cache manager instance
cache_manager: Optional[QuestionCacheManager] = None

async def get_cache_manager() -> QuestionCacheManager:
    """Get global cache manager instance"""
    global cache_manager
    
    if cache_manager is None:
        cache_manager = QuestionCacheManager()
        await cache_manager.initialize()
    
    return cache_manager

async def warm_up_common_questions():
    """Warm up cache with most common question types"""
    manager = await get_cache_manager()
    
    # Common combinations based on LGS patterns
    common_combinations = [
        {'subject': 'Türkçe', 'topic': 'Okuma Anlama', 'difficulty': 'ORTA'},
        {'subject': 'Türkçe', 'topic': 'Dil Bilgisi', 'difficulty': 'KOLAY'},
        {'subject': 'Matematik', 'topic': 'Sayılar', 'difficulty': 'ORTA'},
        {'subject': 'Matematik', 'topic': 'Cebir', 'difficulty': 'ZOR'},
        {'subject': 'Fen Bilimleri', 'topic': 'Fizik', 'difficulty': 'ORTA'},
        {'subject': 'Sosyal Bilgiler', 'topic': 'Tarih', 'difficulty': 'KOLAY'},
    ]
    
    results = await manager.warm_up_cache(common_combinations)
    print(f"🔥 Cache warm-up completed: {results['success']} success, {results['failed']} failed")
    
    return results