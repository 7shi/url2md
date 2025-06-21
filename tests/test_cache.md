# Test Cache Module Documentation

## Overview
The `test_cache.py` module provides comprehensive unit tests for the core caching functionality in url2md. It tests the `Cache` class and `CacheResult` data class, ensuring proper data storage, retrieval, persistence, and file management operations.

## Dependencies and Imports
- **tempfile**: For creating temporary directories during testing
- **pathlib.Path**: For file system path operations
- **pytest**: Testing framework for assertions and test management
- **url2md.cache**: Cache and CacheResult classes being tested
- **url2md.urlinfo**: URLInfo data model for test data creation

## Test Functions

### `test_cache_initialization()`
Tests basic Cache object initialization and directory structure creation.
- **Purpose**: Verify cache creates required directories (`content_dir`, TSV path parent)
- **Approach**: Uses temporary directory, creates Cache instance, checks directory existence
- **Key Assertions**: Content directory exists, cache directory exists

### `test_cache_data_operations()`
Tests core cache data operations: add, get, exists, and get_all.
- **Purpose**: Verify CRUD operations work correctly
- **Test Data**: URLInfo with complete metadata (URL, filename, date, status, content type, size)
- **Operations Tested**:
  - `cache.add()` - Adding URLInfo to cache
  - `cache.get()` - Retrieving URLInfo by URL
  - `cache.exists()` - Checking URL existence (positive and negative cases)
  - `cache.get_all()` - Retrieving all cached entries
- **Key Assertions**: Data integrity after storage/retrieval, proper hash generation

### `test_cache_persistence()`
Tests cache data persistence across different Cache instances.
- **Purpose**: Ensure data survives cache object recreation
- **Workflow**: Create cache → add data → save → create new cache instance → verify data loads
- **Key Assertions**: Data accessible in new instance, URL and metadata match

### `test_cache_tsv_format()`
Tests the TSV file format structure and content accuracy.
- **Purpose**: Verify TSV file structure meets expected format
- **File Structure Tested**:
  - Header row: `['url', 'hash', 'filename', 'fetch_date', 'status', 'content_type', 'size', 'error']`
  - Data rows with proper field mapping
- **Key Assertions**: Header matches expected format, data fields serialize correctly

### `test_summary_path_generation()`
Tests summary file path generation logic.
- **Purpose**: Verify summary paths generated correctly from URLInfo
- **Test Cases**:
  - Normal URLInfo with filename → generates `.json` path with matching stem
  - URLInfo with empty filename → returns None
- **Key Assertions**: Path has `.json` extension, stem matches filename stem, None for empty filename

### `test_content_path_generation()`
Tests content file path generation.
- **Purpose**: Verify content paths map to correct locations
- **Key Assertions**: Content path equals `content_dir / filename`

### `test_filename_collision_handling()`
Tests filename collision detection and resolution.
- **Purpose**: Ensure unique filenames when hash collisions occur
- **Workflow**:
  - Generate filename for URLInfo
  - Create file to simulate collision
  - Generate filename for URLInfo with same hash
  - Verify collision avoidance
- **Key Assertions**: Filenames differ when collision detected, counter added (`-1`)

### `test_domain_throttling()`
Tests domain-based request throttling functionality.
- **Purpose**: Verify throttling mechanism works without errors
- **Approach**: Smoke test with minimal wait time (0.1 seconds)
- **Note**: Timing not tested due to test environment constraints

### `test_cache_result()`
Tests the CacheResult data class functionality.
- **Purpose**: Verify CacheResult properly encapsulates operation results
- **Test Cases**:
  - Successful result with downloaded=True
  - Failed result with downloaded=False
- **Key Assertions**: Success/failure states, URLInfo association, download flags

## Testing Patterns and Approaches

### Temporary Directory Pattern
All tests use Python's `tempfile.TemporaryDirectory()` context manager to:
- Create isolated test environments
- Ensure cleanup after tests
- Avoid test interference

### Data Integrity Testing
Tests verify data survives the complete workflow:
1. Object creation
2. Serialization to TSV
3. File system persistence
4. Deserialization from TSV
5. Object recreation

### Error Handling
Tests include both positive and negative test cases:
- Valid operations (normal workflow)
- Invalid operations (non-existent URLs)
- Edge cases (empty filenames, collisions)

### Fixture-like Data Creation
Tests create consistent URLInfo objects with realistic metadata:
- HTTPS URLs with domains
- HTML content types
- Success status codes
- Reasonable file sizes
- Proper date formatting

## Key Implementation Details

### Hash-based Identification
Tests verify that URLInfo objects generate consistent MD5 hashes for identification and collision detection.

### TSV Format Compliance
Tests ensure TSV files maintain proper structure:
- Tab-separated values
- Consistent field ordering
- Proper escaping of special characters
- Header row preservation

### File System Integration
Tests verify proper integration with file system:
- Directory creation on demand
- Path generation following conventions
- File existence checking
- Cross-platform path handling

## Testing Strategy

The test suite employs a **comprehensive workflow testing** approach:
- Tests individual operations in isolation
- Tests complete workflows end-to-end
- Tests edge cases and error conditions
- Tests persistence and state management
- Uses realistic test data throughout

This ensures the Cache system works reliably in production scenarios while maintaining data integrity and proper file system integration.