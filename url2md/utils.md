# utils.py

## Overview

The `utils.py` module provides HTML processing utilities and resource management functions for the url2md package. It includes functions for extracting content from HTML, cache directory discovery, and resource file access within the package structure.

## Constants

### `DEFAULT_CACHE_DIR`
Default cache directory name: "url2md-cache"

## Functions

### `extract_body_content(html_content: str) -> str`

Extracts innerHTML from body tag and removes script and style tags.

**Parameters:**
- `html_content`: Raw HTML content string

**Returns:**
- Processed HTML content with scripts and styles removed

**Processing Steps:**
1. Extracts content between `<body>` tags
2. Falls back to entire content if no body tag found
3. Removes all `<script>` and `<style>` tags and their content
4. Strips whitespace from result

**Error Handling:**
- Returns original content if any processing fails
- Uses case-insensitive matching for tags

### `extract_html_title(html_content: str) -> str`

Extracts title tag content from HTML.

**Parameters:**
- `html_content`: Raw HTML content string

**Returns:**
- Title text with HTML entities decoded, or empty string if no title

**Processing:**
- Case-insensitive title tag matching
- Decodes HTML entities using `html.unescape()`
- Strips whitespace from result

### `find_cache_dir() -> Path`

Finds cache directory by looking for cache.tsv in current or parent directories.

**Returns:**
- Path to directory containing cache.tsv

**Raises:**
- `ValueError`: If no cache.tsv found (requires explicit initialization)

**Search Strategy:**
1. Checks for default cache directory (url2md-cache) in current directory
2. Searches current directory and all parent directories
3. Looks for cache.tsv in any subdirectory
4. Returns first match found

**Error Handling:**
- Silently skips directories that can't be accessed
- Continues search if individual file checks fail

### `get_resource_path(filename: str) -> Path`

Gets path to a resource file in the package.

**Parameters:**
- `filename`: Resource filename relative to package root

**Returns:**
- Path object pointing to the resource file

**Implementation:**
- Uses `importlib.resources` for Python 3.9+ compatibility
- Accesses files within the url2md package
- Supports nested paths (e.g., "schemas/translate.json")

## Key Design Patterns Used

1. **Fallback Pattern**: Graceful degradation when HTML parsing fails
2. **Directory Search Pattern**: Hierarchical search for cache directories
3. **Resource Abstraction**: Package-relative resource access
4. **Error Tolerance**: Continues operation despite individual failures

## Dependencies

### Internal Dependencies
None - this is a utility module

### External Dependencies
- `re`: Regular expression operations
- `html`: HTML entity decoding
- `pathlib`: Path manipulation
- `importlib.resources`: Package resource access

## Important Implementation Details

1. **HTML Processing Safety**:
   - All HTML processing wrapped in try-catch
   - Returns original content on failure
   - Uses DOTALL and IGNORECASE flags for robustness

2. **Cache Directory Discovery**:
   - Prioritizes default cache directory name
   - Searches up directory tree
   - Requires actual cache.tsv file existence
   - Defensive programming against permission errors

3. **Resource Management**:
   - Uses modern importlib.resources API
   - Package-relative paths
   - Supports nested resource files

4. **Error Philosophy**:
   - HTML processing: Return original on error
   - Cache finding: Raise exception to force initialization
   - Resource access: Let exceptions propagate

5. **Regular Expressions**:
   - Body extraction: Handles nested tags and whitespace
   - Title extraction: Handles multi-line titles
   - Script/style removal: Removes complete tags

6. **Path Handling**:
   - Returns relative paths when possible
   - Handles both absolute and relative results
   - Cross-platform compatibility

7. **Initialization Support**:
   - Clear error message when cache not found
   - Guides user to run 'url2md init'
   - Supports both manual and automatic initialization