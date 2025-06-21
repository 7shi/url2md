# fetch.py

## Overview

The `fetch.py` module implements the URL fetching and caching command functionality. It provides batch URL fetching with progress tracking, domain throttling, retry logic, and comprehensive statistics reporting. The module supports both standard HTTP requests and dynamic rendering via Playwright.

## Functions

### `show_statistics(cache: Cache, urls: List[str], attempted_urls: List[str]) -> None`

Displays comprehensive fetch statistics after processing URLs.

**Parameters:**
- `cache`: Cache instance for accessing URL information
- `urls`: Complete list of URLs that were requested
- `attempted_urls`: URLs that were actually attempted in this session

**Statistics Shown:**
- Total URLs count
- Successful fetches
- Error count
- Skipped count
- Error details for attempted URLs only

### `fetch_urls(urls: List[str], cache_dir: Path, use_playwright: bool = False, force: bool = False, retry: bool = False, throttle_seconds: int = 5) -> None`

Main function for fetching multiple URLs and caching them.

**Parameters:**
- `urls`: List of URLs to fetch
- `cache_dir`: Directory for cache storage
- `use_playwright`: Enable Playwright for dynamic rendering
- `force`: Force re-fetch even if already cached successfully
- `retry`: Retry previously failed URLs
- `throttle_seconds`: Seconds to wait between requests to same domain

**Process Flow:**
1. Filters URLs based on force/retry flags
2. Shows skip summary if applicable
3. Displays progress bar during fetching
4. Applies domain throttling
5. Shows final statistics

## Key Design Patterns Used

1. **Filter Pattern**: Pre-filters URLs based on cache status and flags
2. **Progress Tracking**: Uses tqdm for visual progress indication
3. **Statistics Pattern**: Separates statistics calculation and display
4. **Delegation Pattern**: Delegates actual fetching to Cache class

## Dependencies

### Internal Dependencies
- `.cache`: Cache class for storage and fetching
- `.download`: Imports PLAYWRIGHT_AVAILABLE flag

### External Dependencies
- `pathlib`: For path operations
- `typing`: For type hints
- `tqdm`: For progress bar display

## Important Implementation Details

1. **URL Filtering Logic**:
   - `force=True`: Fetches all URLs regardless of status
   - `retry=True`: Includes previously failed URLs
   - Default: Skips successful URLs, skips errors unless retry flag

2. **Skip Categories**:
   - Successful: Already cached with success status
   - Errors: Previously failed (skipped unless --retry)
   - Tracks counts for user feedback

3. **Progress Display**:
   - Shows current URL (truncated to 50 chars)
   - Updates status (✅ Success or ❌ Error)
   - Real-time progress tracking

4. **Playwright Handling**:
   - Checks availability before use
   - Falls back to requests if unavailable
   - Warns user about fallback

5. **Statistics Separation**:
   - Only shows error details for current session
   - Prevents showing old errors from previous runs
   - Comprehensive counts for all URLs

6. **Early Exit Optimization**:
   - Returns early if no URLs to fetch
   - Shows statistics even for fully cached sets

7. **Domain Throttling**:
   - Respects throttle_seconds parameter
   - Implemented in Cache class
   - Prevents rapid requests to same domain

8. **Error Reporting**:
   - Shows URL and error message
   - Only for URLs attempted in current session
   - Formatted with ❌ emoji for clarity