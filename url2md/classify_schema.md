# classify_schema.py

## Overview

The `classify_schema.py` module provides Pydantic-based schema generation for tag classification operations. It defines type-safe nested models for AI-powered tag classification with multi-language support, replacing the previous JSON file-based approach with native Python class definitions and complete IDE support.

## Functions

### `create_classify_schema_class(language: Optional[str] = None) -> Type[BaseModel]`

Creates a Pydantic schema class for tag classification operations.

**Parameters:**
- `language`: Optional language code for localized output descriptions

**Returns:**
- Pydantic BaseModel class for classification output with full type safety

**Generated Schema Structure:**
The schema creates nested Pydantic models with the following structure:

```python
class Theme(BaseModel):
    theme_name: str = Field(description="Name of the theme")
    theme_description: str = Field(description="Brief description of the theme")
    tags: List[str] = Field(description="List of tags belonging to this theme")

class ClassificationSummary(BaseModel):
    total_tags_processed: int = Field(description="Total number of tags processed")
    total_themes_created: int = Field(description="Number of themes created")
    classification_approach: str = Field(description="Explanation of classification approach...")

class ClassifyResult(BaseModel):
    themes: List[Theme] = Field(description="List of classified themes")
    classification_summary: ClassificationSummary
```

## Key Features

### 1. Complete Type Safety
- **Nested Pydantic Models**: Multi-level type-safe class hierarchy
- **IDE Support**: Full autocomplete, type checking, and validation
- **Field Validation**: Built-in Pydantic validation for all nested structures
- **Type Hints**: Complete typing support throughout the classification workflow

### 2. Dynamic Language Support
- **Language Parameter**: Pass language code to get localized field descriptions
- **Conditional Descriptions**: Adds " in {language}" to relevant description fields
- **Content Localization**: Theme names and descriptions support target language
- **Fallback Behavior**: English descriptions when no language specified

### 3. Hierarchical Classification Structure
- **Theme Organization**: Structured classification with theme-based grouping
- **Tag Association**: Each theme contains its associated tags
- **Metadata Tracking**: Processing statistics and methodology explanation
- **Validation**: Comprehensive validation of nested data structures

### 4. Performance Optimized
- **Direct Class Generation**: No JSON parsing or file I/O overhead
- **Pydantic Performance**: Optimized validation and serialization
- **Memory Efficient**: Native Python object structure with proper nesting
- **Caching**: Pydantic's built-in class caching mechanisms

## Dependencies

### Internal Dependencies
- `typing`: Optional, Dict, Any, List, Type type hints
- `pydantic`: BaseModel, Field for schema definition

### External Dependencies
- **pydantic**: Modern data validation and serialization library

## Design Patterns Used

1. **Composite Pattern**: Nested model structure with Theme and ClassificationSummary
2. **Factory Pattern**: Creates schema classes with different language configurations
3. **Builder Pattern**: Constructs complex nested schema incrementally
4. **Strategy Pattern**: Different description strategies based on language parameter

## Important Implementation Details

1. **Nested Model Definitions**:
   - **Theme**: Individual classification category with metadata
   - **ClassificationSummary**: Processing statistics and methodology
   - **ClassifyResult**: Top-level container for complete classification

2. **Language Integration Strategy**:
   ```python
   lang_suffix = f" in {language}" if language else ""
   
   class Theme(BaseModel):
       theme_name: str = Field(description=f"Name of the theme{lang_suffix}")
       theme_description: str = Field(description=f"Brief description of the theme{lang_suffix}")
   ```

3. **Type Safety Implementation**:
   - All fields properly typed with Python type hints
   - Nested models ensure structural validation
   - Field descriptions provide comprehensive documentation
   - Return type annotation ensures correct usage

4. **Performance Characteristics**:
   - O(1) complexity for schema generation
   - No file I/O operations
   - Direct memory allocation for nested structures
   - Pydantic's optimized validation for complex objects

## Usage Examples

```python
# Basic schema class creation
ClassifySchema = create_classify_schema_class()

# Schema with Japanese localization
ClassifySchemaJP = create_classify_schema_class(language='Japanese')

# Integration with llm7shi
from llm7shi import config_from_schema

schema_class = create_classify_schema_class(language='English')
config = config_from_schema(schema_class)

# Type-safe usage with IDE support
result_data = {
    "themes": [
        {
            "theme_name": "Programming",
            "theme_description": "Software development and coding topics",
            "tags": ["python", "javascript", "programming"]
        },
        {
            "theme_name": "Mathematics",
            "theme_description": "Mathematical concepts and theories",
            "tags": ["algebra", "calculus", "statistics"]
        }
    ],
    "classification_summary": {
        "total_tags_processed": 6,
        "total_themes_created": 2,
        "classification_approach": "Grouped tags by subject domain and technical complexity"
    }
}

# Pydantic validation and type-safe access
result = schema_class(**result_data)
print(result.themes[0].theme_name)  # Full IDE completion
print(len(result.themes))  # Type-aware operations
for theme in result.themes:  # Type-safe iteration
    print(f"Theme: {theme.theme_name}, Tags: {len(theme.tags)}")
```

## Migration from Dict-Based Approach

This module migrated from dictionary-based JSON schema generation to Pydantic nested class generation.

### Before (Dict-Based):
```python
def build_classify_schema(language: Optional[str] = None) -> Dict[str, Any]:
    lang_suffix = f" in {language}" if language else ""
    
    return {
        "type": "object",
        "properties": {
            "themes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "theme_name": {
                            "type": "string",
                            "description": f"Name of the theme{lang_suffix}"
                        },
                        # ... nested dictionary definitions
                    },
                    "required": ["theme_name", "theme_description", "tags"]
                }
            },
            # ... more nested structures
        }
    }
```

### After (Pydantic-Based):
```python
def create_classify_schema_class(language: Optional[str] = None) -> Type[BaseModel]:
    lang_suffix = f" in {language}" if language else ""
    
    class Theme(BaseModel):
        theme_name: str = Field(description=f"Name of the theme{lang_suffix}")
        theme_description: str = Field(description=f"Brief description of the theme{lang_suffix}")
        tags: List[str] = Field(description="List of tags belonging to this theme")
    
    class ClassificationSummary(BaseModel):
        total_tags_processed: int = Field(description="Total number of tags processed")
        total_themes_created: int = Field(description="Number of themes created")
        classification_approach: str = Field(
            description=f"Explanation of classification approach and methodology{lang_suffix}"
        )
    
    class ClassifyResult(BaseModel):
        themes: List[Theme] = Field(description="List of classified themes")
        classification_summary: ClassificationSummary
    
    return ClassifyResult
```

## Integration Points

- **classify.py**: Primary consumer using `create_classify_schema_class`
- **llm7shi**: Direct integration with `config_from_schema(PydanticClass)`
- **Translation System**: Works seamlessly with multi-language workflows
- **Testing**: Type-safe schema validation with nested structure testing

## Benefits Over Previous Approach

1. **Complete Type Safety**: Full IDE support for nested structures and compile-time validation
2. **Performance**: No JSON schema parsing or file I/O overhead
3. **Developer Experience**: Autocomplete for nested objects, type checking, and inline documentation
4. **Maintainability**: Clear nested class definitions instead of complex dictionaries
5. **Validation**: Built-in Pydantic validation with detailed error messages for complex structures
6. **Integration**: Direct compatibility with modern Python tooling and frameworks
7. **Debugging**: Clear stack traces and error messages for nested object validation
8. **Documentation**: Self-documenting through type annotations and Field descriptions

## Classification Guidelines

### Theme Structure
- **Theme Name**: Concise, descriptive category names (localized when applicable)
- **Theme Description**: Brief explanations of theme scope and content (localized)
- **Tag Association**: Clear mapping of tags to appropriate themes

### Processing Metadata
- **Total Tags Processed**: Accurate count of input tags for validation
- **Total Themes Created**: Number of classification categories generated
- **Classification Approach**: Detailed methodology explanation (localized when applicable)

### Language Support
- **Localized Descriptions**: Theme names and descriptions support target language
- **Technical Fields**: Language-neutral technical metadata remains consistent
- **Backward Compatibility**: Fully compatible with existing multi-language classification workflows

## Technical Notes

- Uses nested Pydantic models for complex hierarchical validation
- Each generated class provides complete IDE support for nested access patterns
- Compatible with all Pydantic v2 features and validation rules
- Designed for seamless integration with AI-powered tag classification workflows
- Supports complex validation scenarios with multiple levels of nesting