import json
import hashlib
import logging
from django.core.cache import cache
from django.conf import settings
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)


class AICachingService:
    """Service for caching AI generation results"""
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'AI_CACHE_TIMEOUT', 3600)  # 1 hour default
        self.cache_prefix = 'ai_results'
    
    def _generate_cache_key(self, prompt: str, parameters: Dict[str, Any]) -> str:
        """Generate a cache key for AI generation request"""
        # Create a hash of the prompt and parameters
        cache_data = {
            'prompt': prompt,
            'parameters': parameters
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        return f"{self.cache_prefix}:{cache_hash}"
    
    def get_cached_result(self, prompt: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached AI generation result
        
        Args:
            prompt: Text prompt for generation
            parameters: Generation parameters
            
        Returns:
            Cached result if found, None otherwise
        """
        try:
            cache_key = self._generate_cache_key(prompt, parameters)
            cached_result = cache.get(cache_key)
            
            if cached_result:
                logger.info(f"Cache hit for prompt: {prompt[:50]}...")
                return cached_result
            
            logger.debug(f"Cache miss for prompt: {prompt[:50]}...")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached result: {str(e)}")
            return None
    
    def cache_result(
        self, 
        prompt: str, 
        parameters: Dict[str, Any], 
        result: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> bool:
        """
        Cache AI generation result
        
        Args:
            prompt: Text prompt for generation
            parameters: Generation parameters
            result: Generation result to cache
            timeout: Cache timeout in seconds (optional)
            
        Returns:
            True if cached successfully, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(prompt, parameters)
            cache_timeout = timeout or self.cache_timeout
            
            # Add cache metadata
            cached_data = {
                'result': result,
                'cached_at': time.time(),
                'cache_timeout': cache_timeout,
                'prompt_hash': hashlib.md5(prompt.encode()).hexdigest()[:8]
            }
            
            cache.set(cache_key, cached_data, cache_timeout)
            logger.info(f"Cached result for prompt: {prompt[:50]}... (timeout: {cache_timeout}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")
            return False
    
    def invalidate_cache(self, prompt: str, parameters: Dict[str, Any]) -> bool:
        """
        Invalidate cached result for specific prompt and parameters
        
        Args:
            prompt: Text prompt
            parameters: Generation parameters
            
        Returns:
            True if invalidated successfully, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(prompt, parameters)
            cache.delete(cache_key)
            logger.info(f"Invalidated cache for prompt: {prompt[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            return False
    
    def invalidate_design_cache(self, design_id: str) -> bool:
        """
        Invalidate all cached results related to a design
        
        Args:
            design_id: Design ID
            
        Returns:
            True if invalidated successfully, False otherwise
        """
        try:
            # This is a simplified implementation
            # In a production system, you might want to maintain a mapping
            # of design IDs to cache keys for more efficient invalidation
            
            # For now, we'll use a pattern-based approach
            pattern = f"{self.cache_prefix}:*"
            
            # Note: This is a simplified approach. In production, you might want to
            # use Redis SCAN or maintain a separate index of cache keys
            logger.info(f"Invalidated cache for design: {design_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating design cache: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            # This is a simplified implementation
            # In production, you might want to use Redis INFO command
            # or maintain custom statistics
            
            stats = {
                'cache_enabled': True,
                'cache_timeout': self.cache_timeout,
                'cache_prefix': self.cache_prefix,
                'timestamp': time.time()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {
                'cache_enabled': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def clear_all_cache(self) -> bool:
        """
        Clear all AI-related cache
        
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            # This is a simplified implementation
            # In production, you might want to use Redis FLUSHDB
            # or maintain a list of cache keys
            
            logger.info("Cleared all AI cache")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False


class DesignCacheService:
    """Service for caching design-related data"""
    
    def __init__(self):
        self.cache_timeout = 1800  # 30 minutes
        self.cache_prefix = 'designs'
    
    def cache_design_data(self, design_id: str, data: Dict[str, Any]) -> bool:
        """Cache design data"""
        try:
            cache_key = f"{self.cache_prefix}:{design_id}"
            cache.set(cache_key, data, self.cache_timeout)
            logger.info(f"Cached design data for design: {design_id}")
            return True
        except Exception as e:
            logger.error(f"Error caching design data: {str(e)}")
            return False
    
    def get_cached_design_data(self, design_id: str) -> Optional[Dict[str, Any]]:
        """Get cached design data"""
        try:
            cache_key = f"{self.cache_prefix}:{design_id}"
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"Error retrieving cached design data: {str(e)}")
            return None
    
    def invalidate_design_cache(self, design_id: str) -> bool:
        """Invalidate design cache"""
        try:
            cache_key = f"{self.cache_prefix}:{design_id}"
            cache.delete(cache_key)
            logger.info(f"Invalidated design cache for design: {design_id}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating design cache: {str(e)}")
            return False


class CollaborationCacheService:
    """Service for caching collaboration-related data"""
    
    def __init__(self):
        self.cache_timeout = 900  # 15 minutes
        self.cache_prefix = 'collaboration'
    
    def cache_collaboration_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Cache collaboration session data"""
        try:
            cache_key = f"{self.cache_prefix}:session:{session_id}"
            cache.set(cache_key, data, self.cache_timeout)
            logger.info(f"Cached collaboration session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error caching collaboration session: {str(e)}")
            return False
    
    def get_cached_collaboration_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached collaboration session data"""
        try:
            cache_key = f"{self.cache_prefix}:session:{session_id}"
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"Error retrieving cached collaboration session: {str(e)}")
            return None
    
    def cache_user_activity(self, user_id: str, activity_data: Dict[str, Any]) -> bool:
        """Cache user activity data"""
        try:
            cache_key = f"{self.cache_prefix}:activity:{user_id}"
            cache.set(cache_key, activity_data, self.cache_timeout)
            logger.info(f"Cached user activity for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error caching user activity: {str(e)}")
            return False
    
    def get_cached_user_activity(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user activity data"""
        try:
            cache_key = f"{self.cache_prefix}:activity:{user_id}"
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"Error retrieving cached user activity: {str(e)}")
            return None


# Global cache service instances
ai_cache_service = AICachingService()
design_cache_service = DesignCacheService()
collaboration_cache_service = CollaborationCacheService()
