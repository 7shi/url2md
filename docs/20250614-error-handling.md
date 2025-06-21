# Error Handling Guidelines

This document outlines the error handling policies and patterns used in the url2md package.

## Core Principles

### 1. Fail Fast vs. Graceful Degradation

**Fail Fast** - For user-specified inputs and critical system operations:
- Invalid command line arguments
- Missing or inaccessible user-specified files
- Schema file corruption
- Cache metadata corruption

**Graceful Degradation** - For optional or recoverable operations:
- Individual summary file read errors
- Non-critical data processing errors
- Permission errors during cache detection

### 2. Error Visibility vs. User Experience

**Development Phase (0.1.0)**: Prioritize error visibility over user-friendly messages
- Full stack traces help with debugging
- Detailed error information aids development
- Use `traceback.print_exc()` for comprehensive error reporting

**Production Considerations**: May need user-friendly error messages in future versions

## Error Handling Patterns

### 1. User Input Files

**Pattern**: Print detailed error → `sys.exit(1)`

```python
# URL files (-u/--urls-file)
# Classification files (-c/--class)
try:
    with open(user_file, 'r', encoding='utf-8') as f:
        data = process_file(f)
except Exception as e:
    print(f"Error: Cannot read file: {user_file}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)
```

**Rationale**: User-specified files should exist and be readable. File access errors indicate user error, not program bugs.

### 2. Output Files

**Pattern**: Print detailed error → Continue execution

```python
# Classification output (-o/--output in classify)
# Report output (-o/--output in report)
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"File saved: {output_file}")
except Exception as e:
    print(f"Error: Cannot write to file: {output_file}", file=sys.stderr)
    traceback.print_exc()
    # Continue execution - don't exit
```

**Rationale**: Save failures shouldn't stop the entire process. The work may still be valuable even if output fails.

### 3. Critical System Data

**Pattern**: Print detailed error → `sys.exit(1)`

```python
# Cache metadata (cache.tsv)
# Schema files
try:
    with open(critical_file, 'r', encoding='utf-8') as f:
        data = process_critical_data(f)
except Exception as e:
    print(f"Error: Cannot open critical file: {critical_file}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)
```

**Rationale**: Corruption of cache metadata or missing schema files indicates serious system problems that cannot be recovered from.

### 4. Individual Data Items

**Pattern**: Print warning → Continue processing

```python
# Individual summary files
# Individual URL processing
for item in items:
    try:
        process_item(item)
    except Exception as e:
        print(f"Warning: Failed to process {item}", file=sys.stderr)
        traceback.print_exc()
        continue  # Process remaining items
```

**Rationale**: Failure of individual items shouldn't stop batch processing. Log errors for debugging but continue with remaining work.

### 5. Permission and Access Errors

**Pattern**: Silent skip → Continue

```python
# Cache directory detection
# File system traversal
try:
    if path.exists():
        return path
except Exception:
    pass  # Skip inaccessible paths
```

**Rationale**: Permission errors during optional operations (like cache detection) should not interrupt the process.

## Error Reporting Function

### `traceback.print_exc()`

Python's built-in error reporting that provides:
- Full stack trace showing the call hierarchy
- File names and line numbers for each level
- Function names throughout the call stack
- Source code lines that caused the error
- Complete exception details

**Usage**:
```python
try:
    risky_operation()
except Exception as e:
    print("Error: Operation failed", file=sys.stderr)
    traceback.print_exc()
```

**Output Example**:
```
Error: Operation failed
Traceback (most recent call last):
  File "/path/to/main.py", line 45, in main
    run_command(args)
  File "/path/to/file.py", line 123, in function_name
    risky_operation()
  File "/path/to/utils.py", line 67, in risky_operation
    raise ValueError("invalid input")
ValueError: invalid input
```

## File Operation Categories

### USER_INPUT Files
- URL files (`-u/--urls-file`)
- Classification files (`-c/--class`)
- **Policy**: Error → `sys.exit(1)`

### OUTPUT Files  
- Classification results (`-o/--output` in classify)
- Report files (`-o/--output` in report)
- **Policy**: Error → Log and continue

### CACHE_DATA Files
- `cache.tsv` metadata: Error → `sys.exit(1)`
- Individual summary files: Error → Log and continue
- Content files: Error → Store in URLInfo and continue

### RESOURCE Files
- JSON schema files
- **Policy**: Error → `sys.exit(1)`

## Exception Handling Guidelines

### 1. Generic vs. Specific Exceptions

**Prefer specific exceptions** when the handling differs:
```python
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    # Handle JSON-specific error
    return structured_error_response(e)
except Exception as e:
    # Handle other errors
    log_unexpected_error(e)
```

**Use generic Exception** when handling is the same:
```python
try:
    with open(file_path, 'r') as f:
        content = f.read()
except Exception as e:  # FileNotFoundError, PermissionError, etc.
    print("Error: File access failed", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)
```

### 2. Avoid Unnecessary Exception Conversion

**Bad**:
```python
try:
    response = requests.get(url)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    raise Exception(f"HTTP error: {e}")  # Loses specific exception type
except requests.exceptions.Timeout:
    raise Exception("Request timeout")  # Loses specific exception type
```

**Good**:
```python
response = requests.get(url)
response.raise_for_status()  # Let natural exceptions propagate
```

**Rationale**: Specific exceptions like `requests.exceptions.HTTPError`, `requests.exceptions.Timeout` provide more information than generic `Exception`. Converting them loses debugging information and prevents callers from handling specific error types appropriately.

### 3. Exception Suppression

**Only suppress exceptions when**:
- The operation is optional (cache detection, permission checks)
- Fallback behavior is appropriate (HTML parsing errors)
- The error is expected and handled (individual item failures in batch processing)

**Never suppress exceptions for**:
- User-specified files
- Critical system operations
- Unexpected errors without proper fallback

### 4. Removing Unnecessary Try-Catch Blocks

**Bad** - Unnecessary fallback complexity:
```python
try:
    from PIL import Image
    # GIF processing logic
    converted_data = process_gif(image)
    return converted_data
except Exception as e:
    print("Error: GIF conversion error", file=sys.stderr)
    traceback.print_exc()
    # Complex fallback to original file upload
    return fallback_upload(original_file)
```

**Good** - Let natural exceptions propagate:
```python
from PIL import Image
# GIF processing logic
converted_data = process_gif(image)
return converted_data
```

**Rationale**: If GIF processing fails, it's better to fail fast with a clear error than to silently fall back to potentially less optimal behavior. This makes debugging easier and ensures users are aware of issues.

### 5. Localized vs. Broad Exception Handling

**Core Principle**: **Try-catch should be localized, not used as broad safety nets**

**Bad** - Broad exception handling that obscures problems:
```python
def complex_function():
    try:
        # 50 lines of complex logic
        step1_data = fetch_data()
        step2_data = transform_data(step1_data)
        step3_data = validate_data(step2_data)
        step4_data = process_data(step3_data)
        return save_data(step4_data)
    except Exception as e:
        print("Error: Something went wrong", file=sys.stderr)
        traceback.print_exc()
        return None
```

**Good** - Localized exception handling for specific operations:
```python
def complex_function():
    # Let natural exceptions propagate for most operations
    step1_data = fetch_data()
    step2_data = transform_data(step1_data)
    step3_data = validate_data(step2_data)
    step4_data = process_data(step3_data)
    
    # Only catch exceptions for specific operations that need special handling
    try:
        return save_data(step4_data)
    except PermissionError as e:
        print("Error: Cannot save data - permission denied", file=sys.stderr)
        traceback.print_exc()
        print("Check file permissions and try again", file=sys.stderr)
        sys.exit(1)
```

**Rationale**: 
- **Debugging clarity**: When an exception is caught locally, you know exactly where the problem occurred
- **Error specificity**: You can handle specific error types appropriately
- **Stack trace preservation**: Natural propagation preserves the full call stack
- **Problem isolation**: Issues in one step don't mask issues in other steps

#### When Broad Exception Handling Becomes Problematic

**Symptoms of overly broad exception handling**:
- Error messages like "Something went wrong" without specific context
- Debugging requires adding print statements to isolate the problem
- Different error types get the same generic handling
- Stack traces point to the catch block, not the actual problem
- Silent failures where problems are logged but not addressed

#### The Localization Strategy

**Prefer specific, localized try-catch for**:
- File operations with known failure modes
- Network operations with timeout/connectivity issues
- Data parsing operations with format-specific errors
- Operations requiring cleanup (using finally blocks)

**Avoid broad try-catch for**:
- Entire function bodies
- Multiple unrelated operations
- Operations where you can't provide meaningful error handling
- Debugging and development phases

## Main Function Error Handling

The main function uses minimal error handling to ensure full stack traces are visible:

```python
def main() -> int:
    # ... setup code ...
    
    # Run subcommand - let errors propagate for debugging
    run_subcommand(args)
    return 0
```

**Rationale**: In development phase (0.1.0), full stack traces provide maximum debugging information. KeyboardInterrupt and other signals propagate naturally.

## Command Line Argument Validation

Command line argument validation should happen early and fail fast:

```python
# Weight specification validation
try:
    theme_name, weight_str = weight_spec.rsplit(':', 1)
    weight = float(weight_str)
except ValueError as e:
    print(f"Error: Invalid weight specification: {weight_spec}", file=sys.stderr)
    sys.exit(1)
```

**Rationale**: Invalid arguments indicate user error and should be caught immediately with clear error messages.

## Future Considerations

As the package matures beyond version 0.1.0:

1. **User-Friendly Mode**: Consider adding a `--user-friendly` flag that suppresses stack traces for end users
2. **Structured Logging**: Implement proper logging levels (DEBUG, INFO, WARNING, ERROR)
3. **Error Codes**: Define specific exit codes for different error categories
4. **Configuration**: Allow users to configure error handling behavior

## Testing Error Handling

Error handling should be tested to ensure:
- Appropriate error messages are displayed
- Correct exit codes are returned
- Process continues or stops as expected
- No sensitive information is leaked in error messages

### Test Patterns by Error Type

**System Exit Errors** (User input files, critical system data):
```python
def test_file_read_error():
    with pytest.raises(SystemExit) as exc_info:
        load_invalid_file("nonexistent.txt")
    assert exc_info.value.code == 1
```

**Natural Exception Propagation** (Main function, command validation):
```python
def test_init_command_conflict():
    with pytest.raises(ValueError, match="Cannot specify both"):
        run_init_with_conflicting_args()
```

**Graceful Degradation** (Optional operations):
```python
def test_optional_operation_failure():
    # Should not raise exception, but may log warnings
    result = optional_operation_with_failure()
    assert result is not None  # Fallback behavior
```

### Testing Changes After Error Handling Refactoring

When refactoring error handling patterns:

1. **Update test expectations**: Change from return code assertions to exception assertions
2. **Test specific exception types**: Verify that specific exceptions propagate correctly
3. **Test error message content**: Ensure error messages are informative and actionable
4. **Test stderr output**: Verify that `traceback.print_exc()` produces expected stack trace format