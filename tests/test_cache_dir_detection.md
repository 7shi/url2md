# Test Cache Directory Detection Documentation

## Overview
The `test_cache_dir_detection.py` module tests the automatic cache directory detection functionality in url2md. It verifies the `find_cache_dir()` utility function can locate existing cache directories in various directory structures, providing a seamless user experience when working with cached data.

## Test Class Structure

### `TestCacheDirectoryDetection`
A comprehensive test class that covers all cache directory detection scenarios using realistic directory structures and proper cleanup.

## Dependencies and Imports
- **tempfile**: For creating temporary test directory structures
- **pathlib.Path**: For file system path operations
- **pytest**: Testing framework with exception testing capabilities
- **os**: For directory navigation (getcwd, chdir)
- **url2md.utils**: Contains `find_cache_dir()` and `DEFAULT_CACHE_DIR` being tested

## Test Methods

### `test_find_cache_in_current_directory()`
Tests cache detection in the current working directory.
- **Purpose**: Verify cache found when `cache.tsv` exists in current directory
- **Setup**: Creates `my_custom_cache/cache.tsv` in temp directory
- **Workflow**: Changes to temp directory → calls `find_cache_dir()` → verifies correct path returned
- **Key Assertion**: Returned path resolves to the cache directory containing `cache.tsv`

### `test_find_cache_in_parent_directory()`
Tests cache detection in parent directory when not found locally.
- **Purpose**: Verify upward directory traversal to find cache
- **Setup**: Creates `url2md_cache/cache.tsv` in parent, works from subdirectory
- **Workflow**: 
  1. Create parent cache directory with `cache.tsv`
  2. Create subdirectory
  3. Change to subdirectory
  4. Call `find_cache_dir()`
- **Key Assertion**: Parent's cache directory found and returned

### `test_find_cache_in_grandparent_directory()`
Tests cache detection traversing multiple directory levels.
- **Purpose**: Verify cache found at deeper ancestor levels
- **Setup**: Creates `data_cache/cache.tsv` at root, works from `subdir/nested/`
- **Directory Structure**:
  ```
  temp_dir/
  ├── data_cache/
  │   └── cache.tsv
  └── subdir/
      └── nested/    (working from here)
  ```
- **Key Assertion**: Grandparent's cache directory located correctly

### `test_no_cache_found_raises_error()`
Tests error handling when no cache directory exists.
- **Purpose**: Verify proper error when cache cannot be located
- **Setup**: Empty temporary directory (no cache directories)
- **Expected Behavior**: Raises `ValueError` with message "No cache directory found"
- **Testing Pattern**: Uses `pytest.raises()` with message matching

### `test_cache_dir_without_tsv_ignored()`
Tests that directories without `cache.tsv` are ignored.
- **Purpose**: Ensure only valid cache directories (with `cache.tsv`) are detected
- **Setup**: Creates `cache/` directory but no `cache.tsv` file inside
- **Expected Behavior**: Raises `ValueError` as if no cache found
- **Key Point**: Directory name alone insufficient—must contain `cache.tsv`

### `test_find_cache_from_within_cache_dir()`
Tests cache detection when running from within cache directory structure.
- **Purpose**: Handle case where user runs commands from inside cache directory
- **Setup**: Creates `mycache/cache.tsv` and `mycache/content/` subdirectory
- **Workflow**: Changes to `content/` directory → calls `find_cache_dir()`
- **Key Assertion**: Returns parent cache directory, not content subdirectory

### `test_prefer_current_cache_directory()`
Tests preference for default cache directory name when multiple caches exist.
- **Purpose**: Verify default cache directory preferred over alternatives
- **Setup**: Creates both `DEFAULT_CACHE_DIR` and `other_cache` with `cache.tsv`
- **Directory Structure**:
  ```
  temp_dir/
  ├── url2md_cache/      (default name)
  │   └── cache.tsv
  └── other_cache/       (alternative name)
      └── cache.tsv
  ```
- **Expected Behavior**: Returns `Path(DEFAULT_CACHE_DIR)` (relative path)
- **Key Point**: Default cache directory takes precedence when multiple options exist

## Testing Patterns and Approaches

### Directory Navigation Pattern
All tests follow a consistent pattern for safe directory navigation:
```python
original_cwd = os.getcwd()
try:
    os.chdir(target_directory)
    # Test operations
finally:
    os.chdir(original_cwd)  # Always restore
```

### Temporary Directory Isolation
Each test creates isolated temporary directory structures:
- Prevents test interference
- Ensures clean state for each test
- Automatic cleanup via context managers

### Realistic Directory Structures
Tests create realistic directory hierarchies that mirror actual usage:
- Parent/child relationships
- Multiple directory levels
- Mixed cache and non-cache directories
- Content subdirectories

### Error Condition Testing
Comprehensive error scenarios:
- No cache directories exist
- Invalid cache directories (missing `cache.tsv`)
- Empty directories
- Permission or access issues

## Key Implementation Details

### Cache Validation Requirements
Tests verify that cache detection requires:
- Directory containing `cache.tsv` file
- File must exist and be readable
- Directory name can be arbitrary (not just default name)

### Search Algorithm Testing
Tests verify the search algorithm:
1. **Current Directory**: Check for any directory with `cache.tsv`
2. **Parent Traversal**: Walk up directory tree
3. **Preference Logic**: Prefer default cache directory name
4. **Stop Conditions**: Error when no cache found

### Path Resolution
Tests ensure proper path resolution:
- Absolute paths resolved correctly
- Relative paths maintained when appropriate
- Cross-platform path handling

### Working Directory Management
Tests handle working directory changes safely:
- Always restore original directory
- Handle potential exceptions during directory changes
- Verify operations work from various starting locations

## Edge Cases Covered

### Multiple Cache Directories
Tests behavior when multiple valid cache directories exist at the same level—ensures consistent, predictable selection.

### Nested Cache Scenarios
Tests detection when running from within cache directory structure (e.g., from `cache/content/` subdirectory).

### Name Variations
Tests that cache directory names can vary (`my_custom_cache`, `data_cache`, `url2md_cache`) as long as they contain `cache.tsv`.

### File System Boundaries
Tests appropriate traversal limits and error handling when no cache found within reasonable directory depth.

## Testing Strategy

The test suite uses a **hierarchical directory simulation** approach:
- Creates realistic directory structures
- Tests from various working directory positions  
- Verifies correct upward traversal behavior
- Ensures graceful error handling
- Tests preference and priority logic

This comprehensive approach ensures the cache detection system works reliably across different project structures and user workflows, providing intuitive behavior regardless of where users run url2md commands.