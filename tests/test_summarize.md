# Test Summarize Module Documentation

## Overview
The `test_summarize.py` module provides comprehensive tests for the summarization functionality in url2md. It validates schema compliance, import structure, prompt generation, file operations, and AI integration through both direct testing and mocked scenarios, ensuring reliable content summarization operations.

## Dependencies and Imports
- **json**: For JSON data handling and schema validation
- **tempfile**: For creating temporary test directories
- **pathlib.Path**: For file system path operations
- **unittest.mock**: For mocking external dependencies (Mock, patch)
- **pytest**: Testing framework for assertions and test management
- **url2md.urlinfo**: URLInfo data model for test data
- **url2md.cache**: Cache functionality for summarization workflow
- **url2md.summarize**: Core summarization functions being tested

## Schema and Structure Tests

### `test_schema_validation()`
Tests the Pydantic summarization schema module structure and field requirements.
- **Purpose**: Verify `create_summarize_schema_class()` function generates correct type-safe field definitions
- **Schema Module**: `summarize_schema.create_summarize_schema_class()` function
- **Required Fields Tested**: `['title', 'summary_one_line', 'summary_detailed', 'tags', 'is_valid_content']`
- **Validation Process**:
  1. Import schema class creation function from summarize_schema module
  2. Call function to generate Pydantic schema class
  3. Generate JSON schema using `model_json_schema()`
  4. Extract required fields and properties
  5. Compare against expected field set
  6. Test language parameter functionality with type-safe classes
- **Key Assertions**: Required fields and properties match expected structure with full type safety
- **Language Testing**: Verifies language parameter correctly modifies field descriptions in Pydantic models

### `test_imports()`
Tests module import structure and availability.
- **Purpose**: Verify all summarization functions can be imported correctly
- **Functions Tested**:
  - `generate_summary_prompt()` - Prompt generation for AI
  - `summarize_content()` - Core content summarization
  - `summarize_urls()` - Batch URL summarization
- **Integration Testing**: Cache functionality import verification
- **Key Assertion**: All required functions importable without errors

## Content Processing Tests

### `test_mime_type_handling()`
Tests MIME type processing and fallback logic.
- **Purpose**: Verify content type handling for different input types
- **Test Cases**:
  - `"text/html"` → `"text/html"` (passthrough)
  - `"application/pdf"` → `"application/pdf"` (passthrough)
  - `"text/plain"` → `"text/plain"` (passthrough)
  - `""` → `"text/plain"` (empty string fallback)
  - `None` → `"text/plain"` (None fallback)
- **Fallback Logic**: `content_type or "text/plain"`
- **Key Assertion**: Proper fallback behavior for edge cases

### `test_prompt_generation()`
Tests AI prompt generation functionality.
- **Purpose**: Verify prompts contain all required elements for effective summarization
- **Input Parameters**: URL and content type
- **Required Elements in Generated Prompt**:
  - "structured JSON" - Output format specification
  - "summary_one_line" - Concise summary requirement
  - "summary_detailed" - Detailed summary requirement
  - "tags" - Tag extraction requirement
  - "is_valid_content" - Content validation requirement
  - URL value - Context for summarization
  - Content type - Processing guidance
- **Key Assertion**: All critical elements present in generated prompt

## File Operations Tests

### `test_file_operations()`
Tests file system operations and directory management.
- **Purpose**: Verify cache system properly handles summary file operations
- **Cache Operations Tested**:
  - `cache.create_summary_directory()` - Directory creation
  - `cache.get_summary_path()` - Path generation
  - Summary file existence checking
- **File Workflow**:
  1. Create cache with temporary directory
  2. Create summary directory
  3. Generate summary file path for URLInfo
  4. Test file existence detection
- **URLInfo Test Data**: Complete metadata with realistic values
- **Key Assertions**: Directory creation successful, file existence detection accurate

### `test_json_structure()`
Tests JSON summary data structure and persistence.
- **Purpose**: Verify summary data correctly serialized and stored
- **Summary Data Structure**:
  ```json
  {
    "title": ["Test Page Title"],
    "summary_one_line": "Concise test page summary",
    "summary_detailed": "Detailed summary...",
    "tags": ["test", "webpage", "technology"],
    "is_valid_content": true
  }
  ```
- **File Operations**:
  1. Create cache and summary directory
  2. Generate summary file path
  3. Save JSON data with UTF-8 encoding
  4. Verify file creation and content accuracy
- **Key Assertions**: JSON file created, content matches input data exactly

## AI Integration Tests

### `test_summarize_content_mock()`
Tests AI content summarization with mocked dependencies.
- **Purpose**: Verify summarization workflow without external API calls
- **Mocking Strategy**:
  - `mock_build_schema` - Schema building function
  - `mock_config` - Configuration generation
  - `mock_generate` - AI content generation
- **Mock Response**: JSON-formatted summary data matching expected schema
- **Test Workflow**:
  1. Setup mocked dependencies
  2. Create test content file
  3. Call `summarize_content()` with test URLInfo
  4. Verify successful operation and data structure
- **Key Assertions**: 
  - Successful operation (success=True, error=None)
  - Title field converted to list format
  - All expected summary fields present

## Filtering and Selection Tests

### `test_filter_functions()`
Tests URL filtering functions for selective summarization.
- **Purpose**: Verify URL selection mechanisms work correctly
- **Filter Functions Tested**:
  - `filter_url_infos_by_urls()` - Filter by URL list
  - `filter_url_infos_by_hash()` - Filter by content hash
- **Test Setup**:
  - Create cache with multiple URLInfo objects
  - Different URLs, filenames, and sizes
  - Realistic metadata for each entry
- **Filter Operations**:
  - **URL Filtering**: Select specific URLs from cache
  - **Hash Filtering**: Select by content hash
  - **Empty Filter**: Return all entries when no filter specified
- **Key Assertions**: 
  - Correct URLs returned by URL filter
  - Correct entries returned by hash filter
  - All entries returned when no filter applied

## Testing Patterns and Approaches

### Schema-Driven Testing
Tests verify compliance with code-based schema requirements:
- Schema function import and execution
- Field presence validation
- Data type compliance
- Language parameter functionality
- Required vs optional field handling

### Mock-Based AI Testing
Tests use comprehensive mocking for AI operations:
- External API calls mocked to avoid dependencies
- Response format controlled for predictable testing
- Error scenarios testable without API limits

### File System Integration Testing
Tests verify proper file system integration:
- Temporary directories for isolation
- Path generation correctness
- File existence and content verification
- Cross-platform path handling

### Workflow Simulation Testing
Tests simulate complete summarization workflows:
- Cache creation → content processing → summary generation
- File operations → AI processing → result storage
- Error handling throughout the pipeline

## Key Implementation Details

### Summary Data Format
Tests verify standardized summary data structure:
- **Title**: List format (even for single titles)
- **Summaries**: One-line and detailed versions
- **Tags**: List of descriptive keywords
- **Validation**: Boolean content validity flag

### Cache Integration
Tests verify seamless cache system integration:
- Summary directory management
- File path generation following conventions
- URLInfo object compatibility
- Content file relationship

### AI Prompt Engineering
Tests verify effective prompt construction:
- Clear output format specification
- Required field enumeration
- Context information inclusion
- Processing guidance provision

### Error Handling
Tests verify robust error handling:
- File operation failures
- AI processing errors
- Invalid content scenarios
- Resource availability issues

## Edge Cases Covered

### Content Type Variations
Tests handle various content types and edge cases:
- Standard web content types
- Unknown or missing content types
- Fallback behavior for edge cases

### File System Edge Cases
Tests handle file system variations:
- Non-existent directories
- Path generation with special characters
- Cross-platform compatibility

### Data Structure Edge Cases
Tests handle data variations:
- Empty or missing fields
- Unicode content in various languages
- Large content processing

## Testing Strategy

The summarize test suite employs a **layered validation approach**:

### Schema Layer Testing
- Code-based schema function testing
- Schema generation verification
- Field requirement validation
- Language parameter validation
- Data structure consistency

### Function Layer Testing
- Individual function behavior verification
- Parameter handling validation
- Return value structure confirmation

### Integration Layer Testing
- Cache system integration validation
- File operations coordination
- AI workflow simulation

### System Layer Testing
- Complete workflow validation
- Error propagation verification
- Resource management testing

This comprehensive testing ensures the summarization system reliably processes web content, generates high-quality summaries through AI integration, and maintains data integrity throughout the pipeline while handling edge cases gracefully.