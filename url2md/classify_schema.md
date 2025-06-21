# classify_schema.py

## Overview

The `classify_schema.py` module provides code-based JSON schema generation for tag classification operations. It defines the structure for AI-powered tag classification with multi-language support, replacing the previous JSON file-based approach with type-safe Python functions.

## Functions

### `build_classify_schema(language: Optional[str] = None) -> Dict[str, Any]`

Builds a JSON schema for tag classification operations.

**Parameters:**
- `language`: Optional language code for localized output descriptions

**Returns:**
- Dictionary containing the complete JSON schema for classification output

**Schema Structure:**
- **themes**: Array of theme objects with name, description, and tags
- **classification_summary**: Object with processing metadata and approach explanation

**Theme Object Properties:**
- `theme_name`: String - Name of the theme (localized if language specified)
- `theme_description`: String - Brief description (localized if language specified)  
- `tags`: Array of strings - Tags belonging to this theme

**Classification Summary Properties:**
- `total_tags_processed`: Integer - Total number of tags processed
- `total_themes_created`: Integer - Number of themes created
- `classification_approach`: String - Explanation of methodology (localized if language specified)

## Key Features

### 1. Dynamic Language Support
- **Language Parameter**: Pass language code to get localized field descriptions
- **Conditional Suffix**: Adds " in {language}" to relevant description fields
- **Fallback Behavior**: Empty suffix when no language specified

### 2. Type Safety
- **Static Typing**: All return types explicitly defined
- **Dictionary Construction**: Direct Python dict manipulation
- **No String Processing**: Eliminates JSON parsing errors

### 3. Schema Validation
- **Required Fields**: All necessary fields marked as required
- **Nested Validation**: Complex nested object structures properly defined
- **Array Constraints**: Proper typing for array elements

## Dependencies

### Internal Dependencies
- `typing`: Optional and Dict type hints

### External Dependencies
None - Pure Python implementation

## Design Patterns Used

1. **Builder Pattern**: Constructs complex schema incrementally
2. **Factory Pattern**: Creates schema objects based on parameters
3. **Strategy Pattern**: Different behavior based on language parameter

## Important Implementation Details

1. **Language Integration**:
   - Language suffix applied only to human-readable descriptions
   - Technical field names remain in English
   - Backwards compatible when no language specified

2. **Schema Structure**:
   - Follows JSON Schema specification
   - Supports nested object validation
   - Array items properly typed

3. **Performance**:
   - No file I/O operations
   - Direct dictionary construction
   - Minimal memory overhead

4. **Maintainability**:
   - Single source of truth for schema structure
   - Version controlled with code
   - IDE support for editing

## Usage Examples

```python
# Basic schema without language
schema = build_classify_schema()

# Schema with Japanese localization
schema_jp = build_classify_schema(language='Japanese')

# Integration with llm7shi
from llm7shi import build_schema_from_json, config_from_schema
schema_dict = build_classify_schema(language='English')
schema = build_schema_from_json(schema_dict)
config = config_from_schema(schema)
```

## Migration Notes

This module replaces the previous `schemas/classify.json` file and eliminates the need for:
- File-based schema loading
- String placeholder replacement
- Complex template processing
- Resource path management

The new approach provides better type safety, performance, and maintainability while maintaining full compatibility with existing functionality.