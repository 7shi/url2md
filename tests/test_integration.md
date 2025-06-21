# Test Integration Module Documentation

## Overview
The `test_integration.py` module provides comprehensive integration tests for the url2md package, verifying that different components work together correctly. It tests command-line interface integration, module interactions, complete workflows, and schema compatibility across the entire system.

## Test Class Structure

### `TestCommandIntegration`
Tests command-line interface integration and main entry point functionality.

### `TestCacheIntegration` 
Tests integration between Cache and URLInfo components.

### `TestWorkflowIntegration`
Tests complete workflow scenarios and external dependencies.

### `TestModuleIntegration`
Tests module import structure and cross-module compatibility.

## Dependencies and Imports
- **tempfile**: For creating temporary test environments
- **os**: For directory operations and environment management
- **pathlib.Path**: For file system path handling
- **pytest**: Testing framework with exception handling
- **sys**: For system operations and argument manipulation
- **unittest.mock**: For mocking external dependencies (patch, Mock)
- **url2md.main**: Main entry point and command dispatcher
- **url2md.cache**: Cache functionality
- **url2md.urlinfo**: URL data models

## Command Integration Tests

### `test_main_help()`
Tests main help command functionality.
- **Purpose**: Verify help system works correctly
- **Test Method**: Mock sys.argv with `['url2md', '--help']`
- **Expected Behavior**: SystemExit with code 0 (success)
- **Key Assertion**: Help exits cleanly without errors

### `test_subcommand_help()`
Tests subcommand-specific help functionality.
- **Purpose**: Verify individual command help works
- **Test Case**: `['url2md', 'fetch', '--help']`
- **Expected Behavior**: SystemExit with code 0
- **Coverage**: Ensures help system works for all subcommands

### `test_no_command()`
Tests behavior when no command is provided.
- **Purpose**: Verify graceful handling of incomplete commands
- **Test Case**: `['url2md']` (no subcommand)
- **Expected Behavior**: Returns error code 1
- **Key Point**: Non-zero exit code indicates error condition

### `test_init_command_integration()`
Tests complete init command workflow.
- **Purpose**: Verify init command creates proper cache structure
- **Workflow**:
  1. Change to temporary directory
  2. Execute `url2md init test_cache`
  3. Verify cache structure created
- **Directory Structure Verified**:
  ```
  test_cache/
  ├── cache.tsv
  ├── content/
  └── summary/
  ```
- **Key Assertions**: All required directories and files exist

### `test_init_command_existing_cache_fails()`
Tests init command error handling for existing caches.
- **Purpose**: Prevent accidental cache overwriting
- **Workflow**: 
  1. Create cache successfully
  2. Attempt to create same cache again
- **Expected Behavior**: ValueError with "Cache already exists" message
- **Key Point**: Data protection through collision prevention

### `test_init_command_conflicting_args_fails()`
Tests argument validation for conflicting options.
- **Purpose**: Ensure clear argument parsing
- **Test Case**: Both `--cache-dir` and directory argument specified
- **Command**: `['url2md', '--cache-dir', 'foo', 'init', 'bar']`
- **Expected Behavior**: ValueError with "Cannot specify both" message

### `test_init_command_with_cache_dir_global_option()`
Tests init command with global --cache-dir option.
- **Purpose**: Verify global options work with init command
- **Command**: `['url2md', '--cache-dir', 'custom_cache', 'init']`
- **Expected Behavior**: Cache created in custom location
- **Key Assertion**: Custom cache directory used correctly

## Cache Integration Tests

### `test_cache_urlinfo_integration()`
Tests deep integration between Cache and URLInfo components.
- **Purpose**: Verify complete cache workflow with real data
- **Full Workflow Tested**:
  1. Create URLInfo with complete metadata
  2. Add to cache and save
  3. Create content file
  4. Create summary JSON file
  5. Verify all components work together
  6. Test cache reload functionality
- **File Operations**: Content file creation, summary JSON serialization
- **Data Integrity**: Cross-component data consistency

## Workflow Integration Tests

### `test_fetch_workflow_integration()`
Tests fetch command workflow integration with mocked dependencies.
- **Purpose**: Verify fetch command works through main entry point
- **Mocking Strategy**: Mock `Cache.fetch_and_cache_url()` to avoid network calls
- **Test Flow**: 
  1. Mock successful fetch result
  2. Execute fetch command via main()
  3. Verify command completes successfully
- **Key Assertion**: Mock called once, command returns success (0)

### `test_schema_module_integration()`
Tests Pydantic schema module accessibility and configuration generation.
- **Purpose**: Verify Pydantic schema modules can be loaded and used with type safety
- **Schema Modules Tested**:
  - `summarize_schema.create_summarize_schema_class()`
  - `classify_schema.create_classify_schema_class()`
  - `translate_schema.create_translate_schema_class()`
- **Operations Tested**:
  - Schema module imports
  - Pydantic class creation function calls
  - Schema class generation with language parameters
  - Config generation from Pydantic classes
  - Backward compatibility with dict-based schema functions
- **Integration Points**: Pydantic schema classes → llm7shi integration with `config_from_schema()`

## Module Integration Tests

### `test_all_imports()`
Tests that all modules can be imported without errors.
- **Purpose**: Verify package structure and import dependencies
- **Modules Tested**: All core url2md modules
- **Import Verification**: Both direct module imports and package exports
- **Key Exports Tested**: URLInfo, Cache, CacheResult from main package

### `test_command_module_integration()`
Tests command module interface consistency.
- **Purpose**: Verify all command modules follow expected patterns
- **Interface Requirements**: Each command module must have core functions
- **Functions Tested**:
  - `fetch.fetch_urls()`
  - `summarize.summarize_urls()`
  - `classify.extract_tags()`
  - `report.generate_markdown_report()`
- **Pattern Verification**: Centralized architecture compliance

### `test_utils_integration()`
Tests utility function integration and basic functionality.
- **Purpose**: Verify utility functions work correctly
- **Functions Tested**:
  - `extract_body_content()` - HTML body extraction
  - `extract_html_title()` - HTML title extraction
- **Functionality Testing**: Quick smoke tests with real HTML

### `test_download_integration()`
Tests download module integration and exports.
- **Purpose**: Verify download module provides expected interface
- **Exports Tested**:
  - `PLAYWRIGHT_AVAILABLE` - Boolean availability flag
  - `is_text()` - MIME type checking function
  - `user_agent` - User agent string
- **Functionality Testing**: MIME type detection with various content types

## Testing Patterns and Approaches

### Mock-Based Testing
Strategic use of mocking for external dependencies:
- Network operations mocked to avoid external dependencies
- File system operations tested with real temporary directories
- Command execution mocked where appropriate

### Workflow Simulation
Complete workflow testing from command line to file output:
- Argument parsing → command execution → file operations
- Cross-module data flow verification
- End-to-end process validation

### Interface Compliance Testing
Verification that modules follow architectural patterns:
- Function naming conventions
- Expected export interfaces
- Centralized vs distributed architecture compliance

### Environment Isolation
Tests use proper isolation techniques:
- Temporary directories for file operations
- Working directory changes with restoration
- System argument mocking without side effects

## Key Implementation Details

### Command Architecture Verification
Tests verify centralized command architecture:
- Main entry point handles all command routing
- Individual modules provide function interfaces
- No standalone execution in command modules

### Schema Integration Testing
Tests verify schema modules integrate properly with AI operations:
- Schema modules importable and functional
- Schema function calls work correctly
- Configuration generation succeeds
- Language parameter support verified
- Integration with llm7shi package functions

### Cross-Platform Compatibility
Tests use platform-agnostic approaches:
- pathlib.Path for all file operations
- Proper working directory handling
- Unicode and encoding awareness

### Error Propagation Testing
Tests verify errors propagate correctly:
- Command failures return appropriate exit codes
- Exceptions raised for invalid operations
- Error messages provide useful information

## Testing Strategy

The integration test suite employs a **layered integration approach**:

### Command Layer Testing
- CLI argument parsing and routing
- Global option handling
- Error message generation

### Module Layer Testing  
- Cross-module function calls
- Data structure compatibility
- Import dependency verification

### System Layer Testing
- File system operations
- External tool integration
- Configuration file handling

### Workflow Layer Testing
- Complete operation sequences
- Data flow between components
- Error handling across boundaries

This comprehensive integration testing ensures that url2md functions correctly as a complete system, with all components working together seamlessly while maintaining proper separation of concerns and architectural integrity.