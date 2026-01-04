"""
Shared VISA resource cache to avoid repeated slow scans.
Each device class was doing its own pyvisa.ResourceManager().list_resources()
which takes ~2 seconds each. This module caches the result.
"""

import time
import pyvisa

_cached_rm = None
_cached_urls = None
_cache_time = 0
_CACHE_TTL = 5.0  # Cache valid for 5 seconds


def get_visa_resources(force_refresh=False):
    """
    Get VISA ResourceManager and list of resources.
    Results are cached for CACHE_TTL seconds.

    Returns:
        tuple: (ResourceManager, list of resource URLs)
    """
    global _cached_rm, _cached_urls, _cache_time

    now = time.time()

    if not force_refresh and _cached_rm is not None and (now - _cache_time) < _CACHE_TTL:
        return _cached_rm, _cached_urls

    _cached_rm = pyvisa.ResourceManager()
    _cached_urls = _cached_rm.list_resources()
    _cache_time = now

    return _cached_rm, _cached_urls


def invalidate_cache():
    """Force next call to do a fresh scan."""
    global _cache_time
    _cache_time = 0
