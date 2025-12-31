"""File-based caching service with TTL (Time To Live)"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Import will be available after config is created
try:
    from config import settings
    cache_ttl = settings.CACHE_TTL_SECONDS
except ImportError:
    cache_ttl = 86400  # Default 24 hours


# Create cache directory
cache_dir = Path("cache")
cache_dir.mkdir(exist_ok=True)


async def get_cache(key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached data if it exists and hasn't expired
    
    Args:
        key: Cache key (e.g., "profile:torvalds")
    
    Returns:
        Cached data if valid, None if expired or not found
    """
    cache_file = cache_dir / f"{key}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check TTL
        cached_at = data.get("_cached_at", 0)
        now = datetime.now().timestamp()
        age = now - cached_at
        
        if age < cache_ttl:
            return data["data"]
        else:
            # Cache expired, delete file
            cache_file.unlink()
            return None
    except Exception as e:
        print(f"⚠️ Cache read error for {key}: {e}")
        return None


async def set_cache(key: str, data: Dict[str, Any]):
    """
    Store data in cache with timestamp
    
    Args:
        key: Cache key
        data: Data to cache
    """
    cache_file = cache_dir / f"{key}.json"
    
    try:
        cache_data = {
            "_cached_at": datetime.now().timestamp(),
            "data": data
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, default=str)
    except Exception as e:
        print(f"⚠️ Cache write error for {key}: {e}")


async def clear_cache_by_key(key: str):
    """Delete specific cache entry"""
    cache_file = cache_dir / f"{key}.json"
    if cache_file.exists():
        cache_file.unlink()


async def clear_all_cache():
    """Clear entire cache directory"""
    for cache_file in cache_dir.glob("*.json"):
        cache_file.unlink()
