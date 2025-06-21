# tsv_manager.py

## Overview

The `tsv_manager.py` module provides base functionality for managing Tab-Separated Values (TSV) files. It serves as a foundation for other cache implementations in the url2md package, offering common TSV file operations with data sanitization and atomic file writing.

## Classes and Their Methods

### TSVManager

Base class for TSV file management that provides common operations for reading and writing TSV files.

**Attributes:**
- `_tsv_path` (Path): Path to the TSV file
- `header` (List[str]): Column headers for the TSV file
- `data` (List[List[str]]): Data rows as list of string lists

**Methods:**

#### `__init__(self, tsv_path: Path)`
Initializes the TSV manager with a file path. Sets up empty header and data lists.

#### `tsv_path` (property)
Returns the path to the TSV file.

#### `load() -> None`
Loads data from the TSV file. If the file doesn't exist, initializes empty header and data. Parses the first line as headers and subsequent lines as data rows.

#### `save() -> None`
Saves data to the TSV file using atomic operations:
1. Writes to a temporary file first
2. Sanitizes all field values to remove tabs and newlines
3. Deletes original file if it exists
4. Renames temporary file to target filename

## Functions

### `sanitize_tsv_field(value: str) -> str`
Sanitizes a field value for TSV format by replacing all newline characters and tabs with spaces.

**Parameters:**
- `value`: Field value to sanitize

**Returns:**
- Sanitized string safe for TSV format

## Key Design Patterns Used

1. **Base Class Pattern**: Designed as a base class for inheritance by specialized TSV handlers
2. **Atomic File Operations**: Uses temporary files and rename for safe writes
3. **Data Sanitization**: Ensures TSV format integrity by removing problematic characters
4. **Property Pattern**: Uses @property decorator for controlled access to file path

## Dependencies

### Internal Dependencies
None - this is a base module

### External Dependencies
- `pathlib`: For path manipulation and file operations
- `typing`: For type hints

## Important Implementation Details

1. **TSV Format Handling**:
   - Headers are stored in the first line
   - Data rows are tab-separated
   - All tabs and newlines in data are replaced with spaces

2. **File Safety**:
   - Uses `.tmp` extension for temporary files
   - Atomic rename operation prevents partial writes
   - Handles non-existent files gracefully

3. **Data Structure**:
   - Headers and data are kept as separate lists
   - Data is stored as List[List[str]] for flexibility
   - Empty files result in empty header and data lists

4. **Inheritance Design**:
   - Subclasses can override load() and save() for custom behavior
   - Protected _tsv_path attribute allows subclass access
   - Common sanitization logic is shared via utility function

5. **Error Handling**:
   - No explicit error handling - exceptions propagate to caller
   - This allows subclasses to implement their own error strategies