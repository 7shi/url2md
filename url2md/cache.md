# cache.py

## Overview

The `cache.py` module implements the core caching functionality for the url2md package. It manages URL caching, file storage, metadata management, and provides interfaces for fetching and storing web content with domain-based throttling.

## Classes and Their Methods

### CacheResult

A dataclass representing the result of cache operations.

**Attributes:**
- `success` (bool): Whether the operation was successful
- `url_info` (URLInfo): URLInfo object containing metadata
- `downloaded` (bool): Whether content was newly downloaded

### Cache

The main cache management class that extends TSVManager for TSV file operations.

**Methods:**

#### `__init__(self, cache_dir: Path = Path("cache"))`
Initializes the cache with specified directory. Creates necessary subdirectories, initializes TSV manager and translation cache, and loads existing data.

#### `content_dir` (property)
Returns the path to the content directory where fetched files are stored.

#### `create_summary_directory() -> Path`
Creates and returns the summary directory for storing JSON summaries.

#### `get_summary_path(url_info: URLInfo) -> Optional[Path]`
Generates the path for a summary JSON file based on URLInfo's filename. Returns None if no filename exists.

#### `load() -> None`
Loads data from cache.tsv file. Exits with error if the file cannot be opened. Parses TSV lines into URLInfo objects and populates the entries dictionary.

#### `save() -> None`
Saves current cache data to cache.tsv file. Converts URLInfo objects to TSV format and uses atomic file operations for safety.

#### `add(url_info: URLInfo) -> None`
Adds a new URLInfo entry to the cache and updates domain access time for throttling.

#### `get(url: str) -> Optional[URLInfo]`
Retrieves URLInfo for a given URL. Returns None if not found.

#### `exists(url: str) -> bool`
Checks if a URL exists in the cache.

#### `get_all() -> List[URLInfo]`
Returns all URLInfo entries as a list.

#### `get_content_path(url_info: URLInfo) -> Path`
Constructs the full path to a cached content file.

#### `wait_for_domain_throttle(domain: str, wait_seconds: int = 5)`
Implements domain-based throttling by waiting if the last access to the domain was too recent.

#### `find_available_filename(url_info: URLInfo)`
Finds an available filename that doesn't collide with existing files. Uses content type to determine appropriate extension and adds counters if collisions occur.

#### `fetch_and_cache_url(url: str, use_playwright: bool = False, throttle_seconds: int = 5) -> CacheResult`
The main method for fetching and caching URLs. Checks if content is already cached, handles retries for failed URLs, implements domain throttling, and saves content with appropriate metadata.

## Key Design Patterns Used

1. **Inheritance Pattern**: Cache extends TSVManager to reuse TSV file operations
2. **Composition Pattern**: Contains TranslationCache instance for translation management
3. **Factory Pattern**: Creates URLInfo objects from TSV data
4. **Atomic Operations**: Uses temporary files and rename for safe file writes

## Dependencies

### Internal Dependencies
- `.urlinfo`: URLInfo class for URL metadata
- `.tsv_manager`: TSVManager base class for TSV operations
- `.translation_cache`: TranslationCache for managing translations

### External Dependencies
- `mimetypes`: For MIME type detection and extension mapping
- `pathlib`: Path manipulation
- `datetime`: Timestamp management
- `time`: For throttling delays
- `dataclasses`: For CacheResult definition

## Important Implementation Details

1. **Error Handling**: Uses sys.exit(1) for critical errors (file access failures)
2. **Domain Throttling**: Tracks last access time per domain to prevent rapid requests
3. **Filename Collision Handling**: Automatically adds counters to filenames to avoid overwrites
4. **Content Type Cleaning**: Strips charset information from content-type headers
5. **Retry Logic**: Automatically retries URLs with error status or missing files
6. **Atomic Saves**: Uses temporary files to prevent corruption during saves
7. **File Organization**:
   - `cache/cache.tsv`: Main index file
   - `cache/content/`: Downloaded files
   - `cache/summary/`: JSON summaries
   - `cache/terms.tsv`: Translation cache