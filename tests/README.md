# url2md Test Suite Documentation

This directory contains comprehensive tests for the url2md package, ensuring reliability, correctness, and maintainability across all components.

## Overview

The test suite follows pytest conventions and covers all major functionality including:
- Core data models and cache management
- Content processing and AI integration
- Multi-language support and translation
- Report generation and CLI operations
- Integration testing across components

## Test Structure

```
tests/
├── README.md                       # This documentation
├── test_cache.py                   # Core cache functionality
├── test_cache_dir_detection.py     # Cache directory auto-detection
├── test_cache_io.py                # Cache I/O operations
├── test_cache_translate.py         # Cache-translation integration
├── test_integration.py             # Cross-component integration
├── test_report.py                  # Report generation
├── test_report_translations.py     # Report translation features
├── test_schema_structure.py        # Schema validation and structure
├── test_summarize.py               # AI summarization
├── test_translation_cache.py       # Translation caching system
├── test_urlinfo.py                 # URLInfo data models
└── test_utils.py                   # HTML processing utilities
```

## Test Documentation

### Core Data and Cache Management

#### [`test_cache.py`](test_cache.md)
**Cache functionality tests** - Comprehensive testing of the Cache class including initialization, data operations, persistence, TSV format handling, and file management. Covers cache creation, URL storage/retrieval, domain-based operations, and error handling scenarios.

#### [`test_cache_dir_detection.py`](test_cache_dir_detection.md)
**Cache directory auto-detection tests** - Tests the automatic cache directory discovery functionality that searches parent directories for existing cache.tsv files. Validates directory traversal logic, preference for url2md-cache directories, and fallback mechanisms.

#### [`test_cache_io.py`](test_cache_io.md)
**Cache I/O operations tests** - Focused testing of TSV serialization/deserialization, file format handling, and data integrity. Ensures proper handling of special characters, error recovery, and file format consistency.

#### [`test_translation_cache.py`](test_translation_cache.md)
**Translation cache tests** - Tests the persistent multilingual term storage system. Validates cache-first translation approach, TSV-based storage, language-specific term management, and integration with AI translation services.

### Content Processing

#### [`test_urlinfo.py`](test_urlinfo.md)
**URLInfo data model tests** - Tests the core URLInfo dataclass including TSV serialization/deserialization, domain extraction, hash generation, and content fetching capabilities. Covers both Playwright and requests-based content retrieval.

#### [`test_utils.py`](test_utils.md)
**HTML utility function tests** - Tests HTML content extraction, title processing, text minification, and resource management utilities. Validates BeautifulSoup integration and content cleaning functionality.

#### [`test_summarize.py`](test_summarize.md)
**AI summarization tests** - Tests AI-powered content summarization including Gemini API integration, schema validation, progress tracking, and structured output generation. Covers both successful operations and error handling.

### AI and Translation

#### [`test_cache_translate.py`](test_cache_translate.md)
**Cache-translation integration tests** - Tests the integration between cache management and translation systems. Validates multilingual workflow support, translation term caching, and cross-language consistency.

#### [`test_report_translations.py`](test_report_translations.md)
**Report translation functionality tests** - Specific testing of multilingual report generation including UI term translation, language-specific formatting, fallback mechanisms, and translation cache integration.

### Report Generation

#### [`test_report.py`](test_report.md)
**Report generation tests** - Comprehensive testing of Markdown report generation including tag matching, URL classification, theme-based organization, subsection creation, and URL tag priority ordering. Validates output format and content accuracy.

### System Integration

#### [`test_integration.py`](test_integration.md)
**Cross-component integration tests** - End-to-end testing covering CLI command execution, module interaction, workflow pipelines, and cross-component compatibility. Ensures all components work together correctly in real-world scenarios.

#### [`test_schema_structure.py`](test_schema_structure.md)
**Schema validation and structure tests** - Tests JSON schema compliance, API contracts, package organization, and structural integrity. Validates that all components adhere to expected interfaces and data formats.

## Testing Patterns and Approaches

### Test Organization
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Cross-component interaction testing  
- **End-to-End Tests**: Complete workflow validation
- **Error Handling**: Exception scenarios and edge cases

### Key Testing Strategies

#### Fixture-Based Testing
Most tests use pytest fixtures to set up test environments:
- Temporary directories for cache operations
- Mock data for consistent testing
- Isolated test environments to prevent interference

#### Parameterized Testing
Many tests use `@pytest.mark.parametrize` for comprehensive coverage:
- Multiple input scenarios
- Different data types and edge cases
- Cross-platform compatibility

#### Mock Integration
External dependencies are mocked when appropriate:
- AI API calls for predictable testing
- File system operations for error simulation
- Network requests for offline testing

#### Resource Management
Tests properly manage resources:
- Temporary file cleanup
- Cache directory isolation
- Resource path handling with `get_resource_path()`

## Running Tests

### Basic Test Execution
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_cache.py

# Run with verbose output
uv run pytest -v

# Run with coverage reporting
uv run pytest --cov=url2md --cov-report=html
```

### Test Categories
```bash
# Run only unit tests (fast)
uv run pytest -k "not integration"

# Run only integration tests
uv run pytest tests/test_integration.py

# Run cache-related tests
uv run pytest tests/test_cache*.py

# Run translation-related tests
uv run pytest -k "translate"
```

### Development Workflow
```bash
# Install development dependencies
uv sync --dev

# Run tests before committing
uv run pytest

# Run with coverage to identify gaps
uv run pytest --cov=url2md --cov-report=term-missing
```

## Test Coverage Areas

### Core Functionality (90%+ Coverage)
- ✅ Cache management and persistence
- ✅ URL info handling and serialization
- ✅ HTML processing and content extraction
- ✅ Translation caching and retrieval

### AI Integration (85%+ Coverage)
- ✅ Summarization with schema validation
- ✅ Classification and tag extraction
- ✅ Translation prompt generation
- ✅ Error handling for API failures

### Report Generation (95%+ Coverage)
- ✅ Markdown output formatting
- ✅ Multi-language support
- ✅ Theme organization and subsections
- ✅ URL classification and matching

### CLI and Integration (80%+ Coverage)
- ✅ Command-line argument parsing
- ✅ Workflow pipeline execution
- ✅ Cross-component communication
- ✅ Error propagation and handling

## Contributing to Tests

### Adding New Tests
1. Follow existing naming conventions (`test_*.py`)
2. Use descriptive test function names
3. Include both positive and negative test cases
4. Add docstrings explaining test purpose
5. Use appropriate fixtures and parameterization

### Test Documentation
When adding new test files:
1. Create corresponding `.md` documentation
2. Update this README with links and descriptions
3. Follow the established documentation patterns
4. Include testing strategy explanations

### Best Practices
- **Isolation**: Each test should be independent
- **Clarity**: Test names should explain what is being tested
- **Coverage**: Include edge cases and error conditions
- **Performance**: Keep tests fast and efficient
- **Maintenance**: Update tests when code changes

## Dependencies

### Testing Framework
- **pytest**: Primary testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities (if used)

### Test Utilities
- **tempfile**: Temporary directory management
- **pathlib**: Path handling and manipulation
- **json**: Data serialization for test fixtures
- **unittest.mock**: Mocking external dependencies

### Package Dependencies
Tests import and test all url2md modules:
- Core modules: `cache`, `urlinfo`, `utils`
- AI modules: `summarize`, `classify`, `translate`
- Report modules: `report`, `translation_cache`

This comprehensive test suite ensures the url2md package maintains high quality, reliability, and correctness across all functionality areas.