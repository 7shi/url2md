# Test Cache I/O Operations Documentation

## Overview
The `test_cache_io.py` module focuses on testing the Input/Output operations and TSV file management functionality of the cache system. It verifies that cache data is correctly serialized to and deserialized from TSV files, ensuring data integrity across cache instances and proper handling of edge cases in file formats.

## Dependencies and Imports
- **tempfile**: For creating temporary directories during testing
- **pathlib.Path**: For file system path operations
- **url2md.cache**: Cache class being tested
- **url2md.urlinfo**: URLInfo data model for test data

## Test Functions

### `test_cache_tsv_save_and_load()`
Tests the complete TSV serialization and deserialization workflow.
- **Purpose**: Verify cache data correctly saved to and loaded from TSV files
- **Test Data**: URLInfo with complete metadata
- **Operations Tested**:
  - `cache.add()` - Adding URLInfo to cache
  - `cache.save()` - Persisting cache to TSV file
  - Direct TSV file content verification
  - Internal cache state verification
- **Expected TSV Format**:
  ```
  url	hash	filename	fetch_date	status	content_type	size	error
  https://example.com/test	910d8f18ffe4e3389648f2a252c38786	test.html	2023-01-01T00:00:00	success	text/html	1024	
  ```
- **Key Assertions**:
  - TSV content matches expected format exactly
  - Internal `_entries` dictionary contains 1 entry
  - Header fields match expected order
  - Data array contains correct values

### `test_cache_new_instance_loading()`
Tests cache data loading in a new Cache instance.
- **Purpose**: Verify data persistence across cache object lifecycle
- **Workflow**:
  1. Create cache instance → add URLInfo → save
  2. Create new cache instance from same directory
  3. Verify data loaded automatically
  4. Test data retrieval operations
- **Data Verification**:
  - Header loaded correctly
  - Data array populated with expected values
  - Internal entries dictionary reconstructed
  - URLInfo objects properly recreated with all fields
- **Key Assertions**: New instance contains identical data to original

### `test_tsv_empty_field_handling()`
Tests handling of empty fields in TSV data, particularly the error field.
- **Purpose**: Ensure empty fields serialize/deserialize correctly
- **Test Case**: URLInfo with empty error field (`error=''`)
- **TSV Verification**:
  - Empty error field appears as empty string in TSV
  - Line contains exactly 8 tab-separated fields
  - Last field (error) is empty but present
- **Reload Testing**: New cache instance correctly handles empty error field
- **Key Assertion**: Empty fields preserved as empty strings, not null

### `test_tsv_missing_columns_padding()`
Tests backward compatibility with TSV files missing newer columns.
- **Purpose**: Handle TSV files created by older versions gracefully
- **Test Scenario**: 
  - Manually create TSV with only 7 columns (missing error column)
  - Load with current cache implementation
- **Expected Behavior**:
  - Cache automatically pads missing columns with empty strings
  - Data row extended to 8 columns
  - URLInfo object created with default values for missing fields
- **Key Assertions**:
  - Data array padded to full 8 columns
  - Missing error field defaults to empty string
  - URLInfo reconstruction succeeds

## Testing Patterns and Approaches

### Direct File Content Verification
Tests read and verify the actual TSV file content:
- Exact string matching for TSV format
- Field-by-field verification
- Header row validation
- Data row structure validation

### Cross-Instance Persistence Testing
Tests verify data survives across object instances:
- Save operation in one instance
- Load operation in new instance
- Data integrity across the boundary

### Internal State Verification
Tests check internal cache state consistency:
- `_entries` dictionary population
- `header` field correctness
- `data` array structure
- Synchronization between internal representations

### Edge Case Testing
Comprehensive edge case coverage:
- Empty fields in data
- Missing columns in existing files
- Malformed TSV handling
- Character encoding issues

## Key Implementation Details

### TSV Format Specification
Tests verify exact TSV format compliance:
- **Header**: Fixed 8-column header row
- **Field Order**: `url`, `hash`, `filename`, `fetch_date`, `status`, `content_type`, `size`, `error`
- **Separators**: Tab characters between fields
- **Line Endings**: Standard newline characters
- **Encoding**: UTF-8 encoding throughout

### Data Type Handling
Tests ensure proper data type preservation:
- URLs as strings
- Hashes as 32-character hex strings
- File sizes as numeric strings
- Dates as ISO 8601 strings
- Empty fields as empty strings (not None)

### Backward Compatibility
Tests verify compatibility with older cache files:
- Missing columns automatically detected
- Rows padded to current column count
- Default values assigned to new fields
- No data loss during migration

### Hash Consistency
Tests verify hash values remain consistent:
- Same URLInfo generates same hash
- Hash appears correctly in TSV
- Hash used for identification after reload

## Testing Strategy

The test suite employs a **round-trip testing** approach:
1. **Create** URLInfo objects with known values
2. **Serialize** to TSV format via cache.save()
3. **Verify** TSV file content matches expectations
4. **Deserialize** by creating new cache instance
5. **Compare** retrieved data with original values

This approach ensures:
- **Data Integrity**: No data corruption during serialization/deserialization
- **Format Compliance**: TSV files meet exact specification
- **Backward Compatibility**: Older cache files continue to work
- **Edge Case Handling**: Unusual data values handled correctly

### File System Integration Testing
Tests verify proper file system operations:
- TSV files created in correct locations
- File permissions handled appropriately
- Directory structure maintained
- Atomic save operations (no partial writes)

The comprehensive I/O testing ensures the cache system maintains data integrity while providing flexibility for various deployment scenarios and backward compatibility with existing cache files.