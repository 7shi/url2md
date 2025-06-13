#!/usr/bin/env python3
"""
URL fetching and caching command

Fetch URLs and store them in cache with support for dynamic rendering.
"""

from pathlib import Path
from typing import List

from tqdm import tqdm

from .cache import Cache
from .download import PLAYWRIGHT_AVAILABLE


def show_statistics(cache: Cache, urls: List[str], attempted_urls: List[str]) -> None:
    """Display fetch statistics"""
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for url in urls:
        url_info = cache.get(url)
        if url_info:
            if url_info.status == 'success':
                success_count += 1
            elif url_info.status == 'error':
                error_count += 1
            else:
                skipped_count += 1
    
    print(f"\n=== Fetch Statistics ===")
    print(f"Total URLs: {len(urls)}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Skipped: {skipped_count}")
    
    # Show error details only for URLs that were actually attempted in this session
    attempted_errors = []
    for url in attempted_urls:
        url_info = cache.get(url)
        if url_info and url_info.status == 'error':
            attempted_errors.append(url)
    
    if attempted_errors:
        print(f"\n=== Error Details (This Session) ===")
        for url in attempted_errors:
            url_info = cache.get(url)
            print(f"❌ {url}")
            print(f"   Error: {url_info.error}")


def fetch_urls(urls: List[str], cache_dir: Path, use_playwright: bool = False, 
               force: bool = False, retry: bool = False, throttle_seconds: int = 5) -> None:
    """
    Fetch multiple URLs and cache them
    
    Args:
        urls: List of URLs to fetch
        cache_dir: Cache directory path
        use_playwright: Whether to use Playwright for dynamic rendering
        force: Force re-fetch even if already cached
        retry: Retry failed URLs (default: skip errors)
        throttle_seconds: Seconds to wait between requests to same domain
    """
    if not urls:
        print("No URLs provided")
        return
    
    cache = Cache(cache_dir)
    
    # Filter URLs based on force and retry flags
    urls_to_fetch = []
    skipped_success = 0
    skipped_errors = 0
    
    if force:
        urls_to_fetch = urls
    else:
        for url in urls:
            url_info = cache.get(url) if cache.exists(url) else None
            
            if not url_info:
                # Never cached - always fetch
                urls_to_fetch.append(url)
            elif url_info.status == 'success':
                # Already successful - skip
                skipped_success += 1
            elif url_info.status == 'error':
                # Has error - retry only if --retry flag is set
                if retry:
                    urls_to_fetch.append(url)
                else:
                    skipped_errors += 1
            else:
                # Other status - fetch
                urls_to_fetch.append(url)
    
    # Show skip summary
    if skipped_success > 0 or skipped_errors > 0:
        print(f"Skipped: {skipped_success} successful, {skipped_errors} errors")
    
    if not urls_to_fetch:
        print("All URLs already cached successfully")
        show_statistics(cache, urls, [])
        return
    
    print(f"Fetching {len(urls_to_fetch)} URLs...")
    if use_playwright:
        if PLAYWRIGHT_AVAILABLE:
            print("Using Playwright for dynamic rendering")
        else:
            print("Warning: Playwright not available, falling back to requests")
            use_playwright = False
    
    # Fetch URLs with progress bar
    with tqdm(total=len(urls_to_fetch), desc="Fetching") as pbar:
        for url in urls_to_fetch:
            pbar.set_description(f"Fetching: {url[:50]}...")
            
            result = cache.fetch_and_cache_url(
                url, 
                use_playwright=use_playwright,
                throttle_seconds=throttle_seconds
            )
            
            if result.success:
                pbar.set_postfix(status="✅ Success")
            else:
                pbar.set_postfix(status="❌ Error")
            
            pbar.update(1)
    
    show_statistics(cache, urls, urls_to_fetch)


