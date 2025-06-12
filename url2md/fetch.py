#!/usr/bin/env python3
"""
URL fetching and caching command

Fetch URLs and store them in cache with support for dynamic rendering.
"""

import argparse
import sys
from pathlib import Path
from typing import List

from tqdm import tqdm

from .cache import Cache
from .download import PLAYWRIGHT_AVAILABLE
from .models import load_urls_from_file


def show_statistics(cache: Cache, urls: List[str]) -> None:
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
    
    # Show error details
    if error_count > 0:
        print(f"\n=== Error Details ===")
        for url in urls:
            url_info = cache.get(url)
            if url_info and url_info.status == 'error':
                print(f"❌ {url}")
                print(f"   Error: {url_info.error}")


def fetch_urls(urls: List[str], cache_dir: Path, use_playwright: bool = False, 
               force: bool = False, throttle_seconds: int = 5) -> None:
    """
    Fetch multiple URLs and cache them
    
    Args:
        urls: List of URLs to fetch
        cache_dir: Cache directory path
        use_playwright: Whether to use Playwright for dynamic rendering
        force: Force re-fetch even if already cached
        throttle_seconds: Seconds to wait between requests to same domain
    """
    if not urls:
        print("No URLs provided")
        return
    
    cache = Cache(cache_dir)
    
    # Filter URLs if not forcing
    urls_to_fetch = []
    if force:
        urls_to_fetch = urls
    else:
        for url in urls:
            if not cache.exists(url) or cache.get(url).status != 'success':
                urls_to_fetch.append(url)
            else:
                print(f"⏭️  Skipping already cached: {url}")
    
    if not urls_to_fetch:
        print("All URLs already cached successfully")
        show_statistics(cache, urls)
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
    
    show_statistics(cache, urls)


def main(args: List[str] = None) -> int:
    """Main function for fetch command"""
    parser = argparse.ArgumentParser(
        description="Fetch URLs and store in cache",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://example.com"
  %(prog)s "https://example.com" --cache-dir custom_cache
  %(prog)s --file urls.txt
  %(prog)s -f urls.txt --playwright
  echo "https://example.com" | %(prog)s --file -
        """
    )
    
    parser.add_argument('urls', nargs='*', help='URLs to fetch (multiple allowed)')
    parser.add_argument('-f', '--file', help='URL list file (use - for stdin)')
    parser.add_argument('--cache-dir', type=Path, default=Path('cache'), 
                        help='Cache directory (default: cache)')
    parser.add_argument('--playwright', action='store_true', 
                        help='Use Playwright for dynamic rendering')
    parser.add_argument('--force', action='store_true', 
                        help='Force re-fetch even if already cached')
    parser.add_argument('--throttle', type=int, default=5, 
                        help='Seconds to wait between requests to same domain (default: 5)')
    parser.add_argument('--timeout', type=int, default=30, 
                        help='Request timeout in seconds (default: 30)')
    
    parsed_args = parser.parse_args(args)
    
    # Collect URLs
    urls = []
    
    if parsed_args.urls:
        urls.extend(parsed_args.urls)
    
    if parsed_args.file:
        try:
            file_urls = load_urls_from_file(parsed_args.file)
            urls.extend(file_urls)
        except Exception as e:
            print(f"Error loading URLs from file: {e}", file=sys.stderr)
            return 1
    
    if not urls:
        print("No URLs provided. Use --help for usage information.", file=sys.stderr)
        return 1
    
    # Remove duplicates while preserving order
    unique_urls = []
    seen = set()
    for url in urls:
        if url not in seen:
            unique_urls.append(url)
            seen.add(url)
    
    try:
        fetch_urls(
            unique_urls,
            parsed_args.cache_dir,
            use_playwright=parsed_args.playwright,
            force=parsed_args.force,
            throttle_seconds=parsed_args.throttle
        )
        return 0
    except KeyboardInterrupt:
        print("\nFetch interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())