# urlinfo.py

## Overview

This module contains the core data models for the url2md package, primarily the `URLInfo` class which represents cached URL information. It also provides utilities for loading URLs from files and fetching content from URLs.

## Classes

### `URLInfo` (dataclass)

The main data structure representing information about a cached URL.

#### Attributes
- `url`: The original URL
- `filename`: Name of the cached content file
- `fetch_date`: Date when the content was fetched
- `status`: HTTP status code or error status
- `content_type`: MIME type of the content
- `size`: Size of the content in bytes
- `error`: Error message if fetch failed (optional)
- `hash`: MD5 hash of the URL (auto-generated)
- `domain`: Domain extracted from URL (auto-generated)

#### Methods

##### `__post_init__()`
Automatically called after initialization to:
- Generate MD5 hash from the URL
- Extract domain from the URL using `urlparse`
- Handles errors gracefully, setting empty domain on failure

##### `to_tsv_line()` → str
Serializes the URLInfo object to a TSV (Tab-Separated Values) line:
- Escapes tabs and newlines in error messages
- Returns formatted string with all fields tab-separated
- Format: `url\thash\tfilename\tfetch_date\tstatus\tcontent_type\tsize\terror`

##### `from_tsv_line(line: str)` → URLInfo (classmethod)
Deserializes a URLInfo object from a TSV line:
- Parses tab-separated values
- Handles optional error field
- Overrides auto-generated hash with stored value
- Validates minimum required fields

##### `fetch_content(use_playwright: bool = False)` → str | bytes
Fetches content from the URL with smart method selection:
- **Playwright mode**: 
  - Detects binary files by extension and MIME type
  - Falls back to requests for binary files
  - Handles Playwright failures with automatic fallback
- **Requests mode**: Direct HTTP fetch
- Updates `content_type` from response headers

##### `_fetch_content_requests()` → bytes (private)
Internal method for fetching content using the requests library:
- Sets custom User-Agent header
- 30-second timeout
- Extracts content type from response headers
- Returns raw response content

## Functions

### `load_urls_from_file(filepath: str)` → list[str]

Loads URLs from a file or standard input.

#### Parameters
- `filepath`: Path to file containing URLs, or '-' for stdin

#### Features
- Skips empty lines and comments (lines starting with '#')
- Handles both file and stdin input modes
- Comprehensive error handling with stack traces
- Exits with status 1 on file read errors

#### Returns
List of URLs as strings

## Design Patterns

### Dataclass with Post-Init
- Uses `@dataclass` for clean attribute definition
- `__post_init__` for derived attributes (hash, domain)
- Immutable design with calculated fields

### TSV Serialization
- Human-readable format for cache storage
- Robust escaping for special characters
- Backward-compatible deserialization

### Smart Content Fetching
- Intelligent method selection based on content type
- Graceful fallback mechanisms
- Consistent error handling

### Error Handling
- Detailed error messages with stack traces
- Fail-fast for critical errors (file reading)
- Graceful degradation for non-critical errors (domain extraction)

## Dependencies

### External
- `requests`: HTTP library for content fetching
- `hashlib`: MD5 hash generation
- `mimetypes`: MIME type detection

### Internal
- `download`: Playwright-based download functionality
- Constants: `PLAYWRIGHT_AVAILABLE`, `user_agent`, `is_text()`

## Usage Examples

The module is typically used through the Cache class for persistence:
- Creating URLInfo objects when fetching new URLs
- Serializing/deserializing to/from cache.tsv
- Loading URL lists from files for batch processing