# Test Schema Structure Documentation

## Overview
The `test_schema_structure.py` module provides structural and API tests for the url2md package without requiring external API dependencies. It verifies schema file integrity, code structure compliance, package organization, and configuration correctness to ensure the system meets architectural requirements.

## Dependencies and Imports
- **json**: For schema file parsing and validation
- **re**: For regular expression pattern matching (imported but not used in current tests)
- **pathlib.Path**: For file system path operations
- **pytest**: Testing framework for assertions and test management

## Schema Module Tests

### `test_schema_modules()`
Tests Pydantic-based schema module structure and field definitions.
- **Purpose**: Verify AI operation schema modules contain required class creation functions and structure
- **Schema Modules Tested**:
  - `schema.create_summarize_schema_class()` - For content summarization operations
  - `schema.create_classify_schema_class()` - For content classification operations
  - `schema.create_translate_schema_class()` - For translation operations
- **Schema Validation**:
  - **summarize schema**: Required fields `['title', 'summary_one_line', 'summary_detailed', 'tags', 'is_valid_content']`
  - **classify schema**: Required fields `['themes', 'classification_summary']`
  - **translate schema**: Required fields `['translations']`
- **Validation Process**:
  1. Import schema module dynamically
  2. Call schema class creation function
  3. Generate JSON schema using `model_json_schema()`
  4. Extract `required` and `properties` fields
  5. Compare against expected field sets
  6. Test language parameter functionality with type-safe classes
- **Key Assertions**: Required fields and properties match expected structure exactly

## API Structure Tests

### `test_models_api()`
Tests URLInfo data model API structure.
- **Purpose**: Verify core data model exports required classes and functions
- **API Classes Tested**: `URLInfo` class definition
- **API Functions Tested**: `load_urls_from_file()` function definition
- **Validation Method**: Source code parsing for class/function definitions
- **Key Assertions**: All required API components present in source code

### `test_cache_api()`
Tests Cache module API structure and methods.
- **Purpose**: Verify cache system provides expected interface
- **API Classes Tested**: `Cache`, `CacheResult` class definitions
- **Cache Methods Tested**:
  - `get_content_path()` - Content file path generation
  - `get_summary_path()` - Summary file path generation
  - `fetch_and_cache_url()` - URL fetching and caching
  - `load()` - Cache data loading
  - `save()` - Cache data persistence
- **Validation Method**: Source code scanning for method definitions
- **Key Assertions**: All core cache methods present and callable

## Command Module Tests

### `test_command_modules()`
Tests command module structure compliance with centralized architecture.
- **Purpose**: Verify command modules follow expected architectural patterns
- **Modules Tested**: `fetch.py`, `summarize.py`, `classify.py`, `report.py`
- **Architecture Validation**: Each module must exist and contain core functions
- **Required Functions by Module**:
  - **fetch.py**: `fetch_urls()` function
  - **summarize.py**: `summarize_urls()` function
  - **classify.py**: `extract_tags()` function
  - **report.py**: `generate_markdown_report()` function
- **Design Pattern**: Function modules (no standalone execution) supporting centralized CLI
- **Key Assertions**: Core functions present, supporting centralized command architecture

### `test_main_entry_point()`
Tests main entry point structure and command handlers.
- **Purpose**: Verify main.py contains all required command handlers
- **Handler Functions Tested**:
  - `run_fetch()` - Fetch command handler
  - `run_summarize()` - Summarize command handler
  - `run_classify()` - Classify command handler
  - `run_report()` - Report command handler
  - `run_workflow()` - Workflow command handler
- **Entry Point**: `main()` function as primary entry point
- **Centralized Pattern**: All command routing through single main module
- **Key Assertions**: All command handlers and main function present

## Package Structure Tests

### `test_package_structure()`
Tests overall package file organization and required components.
- **Purpose**: Verify complete package contains all necessary files
- **Required Files Tested**:
  - **Core Modules**: `__init__.py`, `main.py`, `urlinfo.py`, `cache.py`
  - **Command Modules**: `fetch.py`, `summarize.py`, `classify.py`, `report.py`
  - **Utility Modules**: `utils.py`, `download.py`
  - **Configuration**: `pyproject.toml`
  - **Documentation**: `README.md`, `CLAUDE.md`
- **Validation Method**: File existence verification
- **Key Assertions**: All required files present in package

### `test_pyproject_configuration()`
Tests pyproject.toml configuration correctness.
- **Purpose**: Verify package configuration meets requirements
- **Configuration Elements Tested**:
  - **Package Name**: `name = "url2md"`
  - **License**: `CC0-1.0` license specification
  - **Entry Point**: `url2md = "url2md.main:main"` console script
  - **Dependencies**: `google-genai` for Gemini API integration
- **Validation Method**: Text content verification in TOML file
- **Key Assertions**: All critical configuration elements present and correct

## Testing Patterns and Approaches

### Static Analysis Testing
Tests use source code analysis rather than runtime execution:
- File existence verification
- Text pattern matching for API definitions
- JSON schema parsing and validation
- Configuration file content verification

### Architecture Compliance Testing
Tests verify adherence to design patterns:
- **Centralized CLI**: Main module handles all command routing
- **Function Modules**: Command modules provide functions, not standalone execution
- **Clean Separation**: Business logic separated from CLI concerns

### Dependency Verification
Tests confirm required dependencies are properly configured:
- External package dependencies specified
- Internal module structure supports expected imports
- Entry point configuration enables proper installation

### Schema Module Access Testing
Tests verify proper schema module handling:
- Schema modules importable via dynamic imports
- Schema functions callable with parameters
- Schema generation works correctly
- Language parameter support verified

## Key Implementation Details

### Schema Structure Requirements
Tests enforce specific schema structure:
- **Required Fields**: Must be present and match expected sets
- **Properties**: Must align with required fields
- **Function Interface**: Must be callable with expected parameters
- **Field Consistency**: Properties and required fields must match
- **Language Support**: Must support optional language parameters

### API Surface Testing
Tests verify public API remains stable:
- Critical classes and functions always available
- Method signatures maintained
- Import paths consistent

### Centralized Architecture Validation
Tests enforce architectural decisions:
- No `if __name__ == "__main__":` blocks in command modules
- Core functions present but no standalone execution
- All CLI logic centralized in main.py

### Configuration Compliance
Tests verify deployment requirements:
- Entry point properly configured for console script installation
- License specified for legal compliance
- Dependencies specified for proper installation

## Testing Strategy

The schema structure test suite employs a **static validation approach**:

### File System Validation
- Verify all required files present
- Check file accessibility and readability
- Validate directory structure

### Content Structure Validation
- Import and validate schema modules
- Call schema functions and validate output
- Verify source code contains required definitions
- Check configuration file completeness

### Architecture Pattern Validation
- Ensure centralized command architecture maintained
- Verify function module pattern compliance
- Check API consistency and stability

### Dependency Chain Validation
- Verify all imports can be resolved
- Check external dependency specifications
- Validate entry point configuration

This comprehensive structural testing ensures the url2md package maintains architectural integrity, API stability, and deployment readiness without requiring external service dependencies or runtime execution.