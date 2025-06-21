# translate_schema.py

## Overview

The `translate_schema.py` module provides code-based JSON schema generation for translation operations. It dynamically creates schemas based on the terms to be translated, replacing the complex template-based approach with clean Python functions for maximum flexibility.

## Functions

### `build_translate_schema(terms: List[str]) -> Dict[str, Any]`

Builds a JSON schema for term translation operations based on the provided terms list.

**Parameters:**
- `terms`: List of terms to be translated (each becomes a required property)

**Returns:**
- Dictionary containing the complete JSON schema for translation output

**Schema Structure:**
The schema creates a nested structure:

```json
{
  "type": "object",
  "properties": {
    "translations": {
      "type": "object", 
      "properties": {
        "term1": {"type": "string", "description": "Translation of 'term1'"},
        "term2": {"type": "string", "description": "Translation of 'term2'"},
        ...
      },
      "required": ["term1", "term2", ...],
      "additionalProperties": false
    }
  },
  "required": ["translations"],
  "additionalProperties": false
}
```

## Key Features

### 1. Dynamic Schema Generation
- **Term-Based Properties**: Each input term becomes a schema property
- **Required Validation**: All terms marked as required fields
- **Flexible Length**: Supports any number of terms
- **No Hardcoding**: Completely dynamic based on input

### 2. Strict Validation
- **additionalProperties: false**: Prevents extra fields in response
- **Required Fields**: Ensures all requested terms are translated
- **Type Safety**: All translations must be strings
- **Nested Structure**: Clean organization under 'translations' key

### 3. Self-Documenting
- **Descriptive Fields**: Each property describes what it translates
- **Clear Structure**: Intuitive nested organization
- **Validation Ready**: Compatible with JSON Schema validators

## Dependencies

### Internal Dependencies
- `typing`: List and Dict type hints

### External Dependencies
None - Pure Python implementation

## Design Patterns Used

1. **Dynamic Builder**: Constructs schema based on runtime input
2. **Template Method**: Consistent structure with variable content
3. **Factory Pattern**: Creates different schemas for different term sets

## Important Implementation Details

1. **Dynamic Property Generation**:
   ```python
   properties = {}
   for term in terms:
       properties[term] = {
           "type": "string",
           "description": f"Translation of '{term}'"
       }
   ```

2. **Validation Strategy**:
   - Nested structure prevents flat key conflicts
   - `additionalProperties: false` enforces strict compliance
   - Required array matches input terms exactly

3. **Performance Characteristics**:
   - O(n) complexity where n = number of terms
   - Minimal memory overhead
   - No file I/O or external dependencies

4. **Error Prevention**:
   - Type hints prevent incorrect usage
   - Clear structure reduces implementation errors
   - Self-validating through schema compliance

## Usage Examples

```python
# Basic translation schema
terms = ['Summary', 'Themes', 'Total URLs']
schema = build_translate_schema(terms)

# Integration with translation system
from .translate_schema import build_translate_schema
from llm7shi import build_schema_from_json

schema_dict = build_translate_schema(['Hello', 'World'])
schema = build_schema_from_json(schema_dict)

# Expected LLM response format:
{
  "translations": {
    "Hello": "こんにちは",
    "World": "世界"
  }
}
```

## Migration Notes

This module replaces the previous template-based approach that used:
- `schemas/translate.json` with placeholders
- Complex string replacement logic
- Template processing with ```translation_properties``` markers

### Before (Complex Template):
```json
{
  "properties": {
    "translations": {
      "properties": {
        ```translation_properties```
      },
      "required": [```translation_required```]
    }
  }
}
```

### After (Clean Code):
```python
def build_translate_schema(terms: List[str]) -> Dict[str, Any]:
    properties = {}
    for term in terms:
        properties[term] = {
            "type": "string",
            "description": f"Translation of '{term}'"
        }
    return {/* clean structure */}
```

## Integration Points

- **translate.py**: Primary consumer for schema generation
- **classify.py**: Uses for report term translations
- **translation_cache.py**: Works with translation caching system
- **Testing**: Direct import for validation tests

## Benefits Over Previous Approach

1. **Elimination of Complexity**: No template processing required
2. **Type Safety**: Full Python type checking support
3. **Performance**: No file I/O or string manipulation overhead
4. **Maintainability**: Single source of truth in version control
5. **Flexibility**: Supports any term list without pre-configuration
6. **Debugging**: Clear error traces in Python code