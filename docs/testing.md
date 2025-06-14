# Testing Guide

This document provides comprehensive guidelines for testing in the url2md project.

## Test Execution Workflow

Before making any changes to the codebase:
1. Run `uv run pytest` to ensure all tests pass
2. For development dependencies, use `uv sync --dev` if pytest is not available
3. Fix any failing tests before proceeding with new development
4. Run tests again after making changes to verify fixes

## Test Development Guidelines

### Naming and Structure
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Test edge cases and error conditions
- Follow the existing test patterns in the test suite

### File System Tests
- Use temporary directories for file system tests
- Clean up created files and directories after tests
- Use `pytest.tmp_path` fixture for temporary file operations

### External Dependencies
- Mock external dependencies appropriately
- Avoid making real API calls in unit tests
- Use fixtures to provide consistent test data

### Error Handling Tests
- **System Exit Tests**: Use `pytest.raises(SystemExit)` for `sys.exit(1)` cases
- **Exception Tests**: Use `pytest.raises(ExceptionType)` for natural propagation
- Test both error conditions and error message content

### Resource Access
- Use `get_resource_path()` for accessing schema files in tests
- Ensure test resources are included in the package distribution
- Test resource loading under different installation scenarios

## Testing Philosophy

### Comprehensive Coverage
- Test both successful operations and failure modes
- Verify error messages are helpful and actionable
- Test integration points between modules

### Test Isolation
- Each test should be independent and repeatable
- Avoid test interdependencies
- Use setup and teardown appropriately

### Performance Considerations
- Keep unit tests fast-running
- Use mocking to avoid slow operations
- Separate integration tests from unit tests

## Test Categories

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Focus on business logic correctness

### Integration Tests
- Test module interactions
- Verify data flow between components
- Test configuration and setup processes

### End-to-End Tests
- Test complete workflows
- Verify CLI command behavior
- Test with realistic data scenarios

## Running Tests

### Basic Commands
```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_specific.py

# Run tests matching pattern
uv run pytest -k "test_pattern"
```

### Test Coverage
```bash
# Run tests with coverage report
uv run pytest --cov=url2md

# Generate HTML coverage report
uv run pytest --cov=url2md --cov-report=html
```

For comprehensive testing philosophy and practices, see [NOTES.md](../NOTES.md#testing-philosophy-and-practices).