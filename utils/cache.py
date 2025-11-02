"""
Local file-based cache system for transcripts and analysis results.
Persists across app restarts, unlike Streamlit's in-memory cache.
"""
import os
import json
import time
from typing import Optional, Any
from pathlib import Path


CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def get_cache_file(cache_type: str, key: str) -> Path:
    """Get the cache file path for a given type and key."""
    # Sanitize key for filename
    safe_key = "".join(c for c in key if c.isalnum() or c in ('-', '_'))[:50]
    return CACHE_DIR / f"{cache_type}_{safe_key}.json"


def load_from_cache(cache_type: str, key: str, ttl: int) -> Optional[Any]:
    """
    Load cached data if it exists and is still valid.
    
    Args:
        cache_type: Type of cache ('transcript' or 'analysis')
        key: Cache key (video_id)
        ttl: Time to live in seconds
    
    Returns:
        Cached data if valid, None otherwise
    """
    cache_file = get_cache_file(cache_type, key)
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Check if cache is expired
        current_time = time.time()
        cache_time = cache_data.get('timestamp', 0)
        
        if current_time - cache_time > ttl:
            # Cache expired, delete file
            cache_file.unlink()
            return None
        
        # Cache is valid
        return cache_data.get('data')
    
    except (json.JSONDecodeError, KeyError, IOError) as e:
        # Cache file corrupted or unreadable, delete it
        if cache_file.exists():
            cache_file.unlink()
        return None


def save_to_cache(cache_type: str, key: str, data: Any) -> None:
    """
    Save data to cache file.
    
    Args:
        cache_type: Type of cache ('transcript' or 'analysis')
        key: Cache key (video_id)
        data: Data to cache
    """
    cache_file = get_cache_file(cache_type, key)
    
    cache_data = {
        'timestamp': time.time(),
        'data': data
    }
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        # Failed to write cache, but don't raise error
        pass


def clear_cache(cache_type: Optional[str] = None) -> None:
    """
    Clear cache files.
    
    Args:
        cache_type: If provided, only clear this cache type ('transcript' or 'analysis')
                   If None, clear all caches
    """
    if cache_type:
        pattern = f"{cache_type}_*.json"
    else:
        pattern = "*.json"
    
    for cache_file in CACHE_DIR.glob(pattern):
        try:
            cache_file.unlink()
        except IOError:
            pass


def get_cache_size() -> dict:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache size info
    """
    cache_files = list(CACHE_DIR.glob("*.json"))
    total_size = sum(f.stat().st_size for f in cache_files if f.exists())
    
    transcript_count = len(list(CACHE_DIR.glob("transcript_*.json")))
    analysis_count = len(list(CACHE_DIR.glob("analysis_*.json")))
    
    return {
        'total_files': len(cache_files),
        'transcript_files': transcript_count,
        'analysis_files': analysis_count,
        'total_size_mb': round(total_size / (1024 * 1024), 2)
    }

