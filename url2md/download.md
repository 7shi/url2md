# download.py

## Overview

The `download.py` module provides Playwright-based dynamic rendering for web content fetching. It can handle JavaScript-heavy websites that require dynamic rendering to access their full content. The module includes both a reusable API and a standalone command-line interface.

## Constants

### `PLAYWRIGHT_AVAILABLE`
Boolean flag indicating whether Playwright is installed and available.

### `user_agent`
Standard Chrome user agent string used for requests.

### `text_types`
List of MIME types that should be treated as text content:
- application/json
- application/xml
- application/xhtml+xml
- application/javascript
- application/ecmascript
- application/x-httpd-php
- application/x-sh
- application/x-yaml

## Functions

### `is_text(content_type: str) -> bool`

Determines if a content type should be treated as text.

**Parameters:**
- `content_type`: MIME type string

**Returns:**
- True if content should be treated as text

**Logic:**
- Returns True for any type starting with 'text/'
- Returns True for specific application types in text_types list

### `download(url: str) -> tuple[str, bytes]`

Fetches content after dynamic rendering using Playwright.

**Parameters:**
- `url`: URL to fetch

**Returns:**
- Tuple of (content_type: str, content: bytes)

**Process:**
1. Launches headless Chromium browser
2. Sets custom user agent
3. Navigates to URL with networkidle wait
4. Checks for HTTP errors (status >= 400)
5. Determines content type from response headers
6. For text content: waits 2 seconds, then gets full page content
7. For binary content: gets response body directly
8. Closes browser and returns results

**Error Handling:**
- Raises exception for HTTP 4xx/5xx status codes
- Format: "HTTP {status}: {status_text}"

### `main()`

Command-line interface for the download module.

**Arguments:**
- `url`: URL to fetch (required)
- `-o, --output`: Optional output filename

**Behavior:**
- Checks Playwright availability
- Fetches URL with dynamic rendering
- Shows content type and size
- Saves to file if output specified
- Shows content preview for text types (first 1000 chars)

## Key Design Patterns Used

1. **Context Manager Pattern**: Uses Playwright's sync context manager
2. **Content Type Detection**: Separate handling for text vs binary
3. **Command Line Interface**: Standard argparse pattern
4. **Availability Check**: Graceful handling of missing dependencies

## Dependencies

### Internal Dependencies
None - this is a leaf module

### External Dependencies
- `playwright.sync_api`: For browser automation (optional)
- `argparse`: Command-line argument parsing
- `sys`: System operations

## Important Implementation Details

1. **Playwright Configuration**:
   - Uses Chromium browser (most compatible)
   - Headless mode (no GUI)
   - Custom user agent (Chrome-like)
   - Network idle wait (ensures content loaded)

2. **Content Type Handling**:
   - Extracts content-type from response headers
   - Strips charset info (splits on semicolon)
   - Defaults to "text/html" if no content-type

3. **Dynamic Content Strategy**:
   - For text: Additional 2-second wait after network idle
   - Gets full page content (post-JavaScript execution)
   - For binary: Uses direct response body

4. **Error Management**:
   - HTTP errors converted to exceptions
   - Browser automatically closed via context manager
   - Clear error messages for missing Playwright

5. **Installation Guidance**:
   - Shows exact commands for Playwright setup
   - Handles both package and browser installation

6. **Performance Considerations**:
   - Browser launched per request (stateless)
   - Minimal wait times (2 seconds max)
   - Direct binary transfer for non-text content

7. **CLI Features**:
   - File output support
   - Content preview for text
   - Progress feedback
   - Clear success/error reporting

8. **Flexibility**:
   - Can be used as library (download function)
   - Standalone CLI tool (main function)
   - Graceful fallback when Playwright unavailable