# translate_schema.py

## Overview

The `translate_schema.py` module provides Pydantic-based schema generation for translation operations. It dynamically creates Pydantic classes using `create_model` based on the terms to be translated, offering complete type safety and IDE support while maintaining maximum flexibility.

## Functions

### `create_translate_schema_class(terms: List[str]) -> Type[BaseModel]`

Creates a Pydantic schema class for term translation operations based on the provided terms list.

**Parameters:**
- `terms`: List of terms to be translated (each becomes a required field)

**Returns:**
- Pydantic BaseModel class for translation output with type safety

**Generated Schema Structure:**
The schema creates a nested Pydantic model structure:

```python
class TranslationDict(BaseModel):
    term1: str = Field(description="Translation of 'term1'")
    term2: str = Field(description="Translation of 'term2'")
    # ... dynamic fields for each term
    
class TranslateResult(BaseModel):
    translations: TranslationDict
```

## Key Features

### 1. Dynamic Pydantic Class Generation
- **`create_model` Usage**: Dynamically generates classes at runtime
- **Type-Safe Fields**: Each term becomes a typed field with validation
- **Field Descriptions**: Automatic description generation for each term
- **Clean Structure**: Simple, focused schema without additional constraints

### 2. Complete Type Safety
- **IDE Support**: Full autocomplete and type checking
- **Compile-Time Validation**: Catches errors before runtime
- **Pydantic Validation**: Built-in data validation and serialization
- **Type Hints**: Full typing support throughout

### 3. Performance Optimized
- **Direct Class Generation**: No JSON parsing overhead
- **Memory Efficient**: Pydantic's optimized internal structure
- **Fast Validation**: Native Python validation speed
- **Cached Classes**: Pydantic's built-in class caching

## Dependencies

### Internal Dependencies
- `typing`: List, Type, Dict, Any type hints
- `pydantic`: BaseModel, Field, create_model, ConfigDict

### External Dependencies
- **pydantic**: Modern data validation and serialization library

## Design Patterns Used

1. **Dynamic Class Factory**: Creates classes based on runtime input
2. **Builder Pattern**: Constructs complex objects step by step
3. **Configuration Strategy**: Uses ConfigDict for validation control
4. **Type Factory**: Generates typed interfaces dynamically

## Important Implementation Details

1. **Dynamic Field Generation**:
   ```python
   translation_fields = {
       term: (str, Field(description=f"Translation of '{term}'"))
       for term in terms
   }
   ```

2. **Pydantic `create_model` Usage**:
   ```python
   TranslationDict = create_model(
       'TranslationDict',
       **translation_fields
   )
   ```

3. **Type Safety Strategy**:
   - Each field is properly typed as `str`
   - Field descriptions provide documentation
   - Clean structure optimized for Gemini API compatibility
   - Return type annotation ensures correct usage

4. **Performance Characteristics**:
   - O(n) complexity where n = number of terms
   - Pydantic's optimized class generation
   - No file I/O or template processing
   - Direct memory allocation

## Usage Examples

```python
# Basic translation schema class creation
terms = ['Summary', 'Themes', 'Total URLs']
TranslateSchema = create_translate_schema_class(terms)

# Integration with llm7shi
from llm7shi import config_from_schema

schema_class = create_translate_schema_class(['Hello', 'World'])
config = config_from_schema(schema_class)

# Type-safe usage with IDE support
result_data = {
    "translations": {
        "Hello": "こんにちは",
        "World": "世界"
    }
}

# Pydantic validation
result = schema_class(**result_data)
print(result.translations.Hello)  # Type-safe access with IDE completion
```

## Migration from Dict-Based Approach

This module migrated from dictionary-based JSON schema generation to Pydantic class generation.

### Before (Dict-Based):
```python
def build_translate_schema(terms: List[str]) -> Dict[str, Any]:
    properties = {}
    for term in terms:
        properties[term] = {
            "type": "string",
            "description": f"Translation of '{term}'"
        }
    return {
        "type": "object",
        "properties": {
            "translations": {
                "type": "object",
                "properties": properties,
                "required": terms,
                "additionalProperties": False
            }
        }
    }
```

### After (Pydantic-Based):
```python
def create_translate_schema_class(terms: List[str]) -> Type[BaseModel]:
    translation_fields = {
        term: (str, Field(description=f"Translation of '{term}'"))
        for term in terms
    }
    
    TranslationDict = create_model(
        'TranslationDict',
        **translation_fields
    )
    
    class TranslateResult(BaseModel):
        translations: TranslationDict
    
    return TranslateResult
```

## Integration Points

- **translate.py**: Primary consumer using `create_translate_schema_class`
- **classify.py**: Uses for report term translations
- **translation_cache.py**: Works with translation caching system
- **llm7shi**: Direct integration with `config_from_schema(PydanticClass)`
- **Testing**: Type-safe schema validation

## Benefits Over Previous Approach

1. **Complete Type Safety**: Full IDE support and compile-time validation
2. **Performance**: No JSON schema parsing overhead
3. **Developer Experience**: Autocomplete, type checking, and documentation
4. **Maintainability**: Clear class definitions instead of nested dictionaries
5. **Validation**: Built-in Pydantic validation with detailed error messages
6. **Integration**: Direct compatibility with modern Python tooling
7. **Debugging**: Clear stack traces and error messages in Python code
8. **Extensibility**: Easy to add validation rules and custom logic

## Technical Notes

- **Gemini API Compatibility**: Configuration options like `extra='forbid'` are avoided because they generate `additionalProperties: false` in the JSON schema, which is not supported by the Gemini API
- `create_model` enables dynamic field generation while maintaining type safety and API compatibility
- Each generated class is fully typed and provides IDE completion
- Compatible with all Pydantic v2 features and validation rules
- Schema structure is optimized for LLM integration without unnecessary constraints