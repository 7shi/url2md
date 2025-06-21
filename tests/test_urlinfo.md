# Test URLInfo Module Documentation

## Overview
The `test_urlinfo.py` module provides comprehensive unit tests for the URLInfo data model and URL loading functionality. It validates data creation, serialization, deserialization, domain extraction, content fetching, and file loading operations that form the foundation of url2md's data handling system.

## Test Class Structure

### `TestURLInfo`
Tests the core URLInfo data class functionality including creation, serialization, and content fetching.

### `TestLoadUrlsFromFile`
Tests the URL loading functionality from files and stdin.

## Dependencies and Imports
- **tempfile**: For creating temporary test files
- **pathlib.Path**: For file system operations
- **pytest**: Testing framework with exception handling
- **unittest.mock**: For mocking external dependencies (patch, mock_open)
- **url2md.urlinfo**: URLInfo class and load_urls_from_file function being tested

## URLInfo Data Model Tests

### `TestURLInfo.test_urlinfo_creation()`
Tests URLInfo object creation and automatic field generation.
- **Purpose**: Verify URLInfo properly initializes with post-processing
- **Test Data**: Complete URLInfo with realistic metadata
- **Auto-Generated Fields**:
  - **Hash**: MD5 hash generated from URL
  - **Domain**: Extracted from URL (example.com)
- **Validation**:
  - Hash length is 32 characters (MD5 format)
  - Domain correctly extracted from URL
  - All provided fields preserved
- **Key Assertions**: Hash generated, domain extracted correctly

### `TestURLInfo.test_urlinfo_tsv_serialization()`
Tests bidirectional TSV serialization and deserialization.
- **Purpose**: Verify URLInfo can round-trip through TSV format without data loss
- **Test Process**:
  1. Create URLInfo with complete data including error field
  2. Serialize to TSV line using `to_tsv_line()`
  3. Deserialize back using `from_tsv_line()`
  4. Compare original and reconstructed objects
- **Fields Tested**: All URLInfo fields including URL, hash, filename, dates, status, content type, size, error
- **Key Assertions**: Perfect round-trip fidelity, no data corruption

### `TestURLInfo.test_urlinfo_error_escaping()`
Tests proper escaping of special characters in error messages.
- **Purpose**: Ensure TSV format integrity with problematic characters
- **Test Input**: Error message with tabs and newlines: `'Error with\ttab and\nnewline'`
- **Expected Behavior**: Special characters replaced with spaces in TSV output
- **TSV Format Protection**: Tab separators preserved, content sanitized
- **Key Assertions**: No tabs or newlines in error field, TSV structure maintained

### `TestURLInfo.test_urlinfo_invalid_tsv()`
Tests error handling for malformed TSV input.
- **Purpose**: Verify robust handling of invalid data
- **Error Cases**:
  - Too few fields in TSV line
  - Empty TSV line
- **Expected Behavior**: ValueError raised for invalid input
- **Key Assertions**: Appropriate exceptions raised for malformed data

### `TestURLInfo.test_urlinfo_domain_extraction()`
Tests domain extraction algorithm with various URL formats.
- **Purpose**: Verify domain extraction handles different URL patterns
- **Test Cases**:
  - `'https://example.com/path'` → `'example.com'`
  - `'http://subdomain.example.org'` → `'subdomain.example.org'`
  - `'https://Example.COM/path'` → `'example.com'` (lowercase normalization)
  - `'invalid-url'` → `''` (graceful failure)
- **Key Features**: Case normalization, graceful error handling
- **Key Assertions**: Correct domain extraction for valid URLs, empty string for invalid URLs

### `TestURLInfo.test_urlinfo_domain_extraction_error_handling()`
Tests domain extraction error handling with mocked failures.
- **Purpose**: Verify graceful handling of parsing exceptions
- **Test Strategy**: Mock urlparse to raise exceptions
- **Error Logging**: Capture stderr to verify error messages logged
- **Expected Behavior**: Empty domain on parsing failure, error logged
- **Key Assertions**: Exception handled gracefully, appropriate error logging

### `TestURLInfo.test_urlinfo_empty_url_handling()`
Tests handling of empty URL input.
- **Purpose**: Verify empty URLs handled without errors
- **Expected Behavior**: Empty domain, no error logging
- **Key Assertion**: Empty URL results in empty domain gracefully

## Content Fetching Tests

### `TestURLInfo.test_fetch_content_requests()`
Tests content fetching using requests library with mocked responses.
- **Purpose**: Verify HTTP content fetching works correctly
- **Mocking Strategy**: Mock requests.get with controlled response
- **Mock Response Setup**:
  - Content: `b'test content'`
  - Headers: `{'content-type': 'text/html; charset=utf-8'}`
  - Successful HTTP status
- **Test Verification**:
  - Content retrieved correctly
  - Content type updated from response headers
  - Proper User-Agent header sent
- **Key Assertions**: Content matches expected, headers properly processed

### `TestURLInfo.test_fetch_content_error_handling()`
Tests content fetching error handling.
- **Purpose**: Verify network errors properly propagated
- **Error Simulation**: Mock requests.get to raise "Connection timeout"
- **Expected Behavior**: Exception propagated to caller
- **Key Assertion**: Original exception message preserved

## URL Loading Tests

### `TestLoadUrlsFromFile.test_load_urls_from_regular_file()`
Tests loading URLs from standard text files.
- **Purpose**: Verify URL parsing from file with comments and empty lines
- **Test File Content**:
  ```
  # Comment line
  https://example1.com
  https://example2.com
  # Another comment
  
  https://example3.com
  ```
- **Expected Parsing**: Comments ignored, empty lines skipped, URLs extracted
- **Key Assertion**: Only valid URLs returned in correct order

### `TestLoadUrlsFromFile.test_load_urls_empty_file()`
Tests handling of empty input files.
- **Purpose**: Verify graceful handling of files with no content
- **Expected Behavior**: Empty list returned, no errors
- **Key Assertion**: Empty result for empty file

### `TestLoadUrlsFromFile.test_load_urls_comments_only()`
Tests files containing only comments.
- **Purpose**: Verify comment-only files handled correctly
- **Test Content**: Multiple comment lines with no URLs
- **Expected Behavior**: Empty list returned
- **Key Assertion**: Comments properly filtered out

### `TestLoadUrlsFromFile.test_load_urls_from_stdin()`
Tests URL loading from standard input.
- **Purpose**: Verify stdin input processing works
- **Stdin Simulation**: Mock stdin with iterator of lines
- **Test Input**: Mixed comments, empty lines, and URLs
- **Special Parameter**: File path `'-'` indicates stdin
- **Key Assertion**: URLs extracted correctly from stdin

### `TestLoadUrlsFromFile.test_load_urls_file_not_found()`
Tests error handling for non-existent files.
- **Purpose**: Verify appropriate error for missing files
- **Expected Behavior**: SystemExit with code 1
- **Error Handling**: Graceful termination with error code
- **Key Assertion**: System exit with failure code

### `TestLoadUrlsFromFile.test_load_urls_with_whitespace()`
Tests URL parsing with various whitespace scenarios.
- **Purpose**: Verify whitespace handling and normalization
- **Test Cases**: Leading/trailing spaces, tabs, mixed whitespace
- **Expected Behavior**: Whitespace stripped, clean URLs returned
- **Key Assertion**: All whitespace variations handled correctly

## Testing Patterns and Approaches

### Round-Trip Testing
Tests verify data integrity through complete serialization cycles:
- Object → TSV → Object
- No data loss or corruption
- Field-by-field comparison

### Mock-Based External Testing
External dependencies mocked for reliable testing:
- Network requests mocked to avoid external dependencies
- File system operations use real temporary files
- Standard input mocked for controlled testing

### Error Boundary Testing
Comprehensive error scenario coverage:
- Invalid input data
- Network failures
- File system errors
- Parsing exceptions

### Edge Case Testing
Thorough edge case coverage:
- Empty inputs
- Special characters
- Malformed data
- Boundary conditions

## Key Implementation Details

### Domain Extraction Algorithm
Tests verify sophisticated domain processing:
- URL parsing with error handling
- Case normalization (lowercase)
- Subdomain preservation
- Graceful failure for invalid URLs

### TSV Format Compliance
Tests ensure proper TSV handling:
- Tab-separated values
- Special character escaping
- Field order consistency
- Header compatibility

### Content Type Processing
Tests verify HTTP header processing:
- Content-Type header parsing
- Character encoding detection
- MIME type normalization

### File Processing Strategy
Tests verify flexible input handling:
- Regular files with path
- Standard input with '-' parameter
- Comment and whitespace filtering
- Unicode and encoding support

## Error Handling Strategies

### Graceful Degradation
Tests verify system continues operating with partial failures:
- Domain extraction failures → empty domain
- Network errors → exception propagation
- File errors → system exit with error code

### User-Friendly Error Messages
Tests verify appropriate error reporting:
- Clear error messages for common issues
- Proper logging for debugging
- Appropriate exit codes for automation

### Data Integrity Protection
Tests verify data protection mechanisms:
- Input validation before processing
- Sanitization of problematic characters
- Round-trip validation for serialization

## Testing Strategy

The URLInfo test suite employs a **comprehensive data lifecycle testing** approach:

### Data Model Testing
- Object creation and initialization
- Field validation and constraints
- Auto-generation of derived fields

### Serialization Testing
- Format compliance verification
- Round-trip integrity validation
- Error handling for malformed data

### External Integration Testing
- Network operation simulation
- File system operation validation
- Standard input/output handling

### Error Resilience Testing
- Exception handling verification
- Graceful degradation confirmation
- Error propagation validation

This thorough testing ensures URLInfo provides a robust foundation for the url2md system, handling real-world data variations and edge cases while maintaining data integrity throughout all operations.