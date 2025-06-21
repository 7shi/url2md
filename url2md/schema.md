# schema.py

## Overview

The `schema.py` module provides Pydantic-based schema generation for all AI operations in url2md. It consolidates schema definitions for summarization, classification, and translation operations into a single module, offering complete type safety, IDE support, and multi-language capabilities while maintaining clean separation of concerns.

This module replaced the previous JSON file-based approach and later dictionary-based implementation with native Python class definitions using Pydantic models, providing modern type-safe development experience.

## Functions

### `create_summarize_schema_class(language: Optional[str] = None) -> Type[BaseModel]`

Creates a Pydantic schema class for URL content summarization operations.

**Parameters:**
- `language`: Optional language code for localized output descriptions

**Returns:**
- Pydantic BaseModel class for summarization output with full type safety

**Generated Schema Structure:**
```python
class SummarizeResult(BaseModel):
    title: str = Field(description="Page title (appropriate title inferred from content)")
    summary_one_line: str = Field(description="Concise one-line summary within 50 characters")
    summary_detailed: str = Field(description="Detailed summary of 200-400 characters...")
    tags: List[str] = Field(description="List of tags representing the content...")
    is_valid_content: bool = Field(description="Whether the content is meaningful...")
```

**Usage:**
```python
# Basic usage
schema_class = create_summarize_schema_class()

# With language support
schema_class_jp = create_summarize_schema_class(language='Japanese')

# Integration with llm7shi
config = config_from_schema(schema_class)
```

### `create_classify_schema_class(language: Optional[str] = None) -> Type[BaseModel]`

Creates a Pydantic schema class for tag classification operations.

**Parameters:**
- `language`: Optional language code for localized output descriptions

**Returns:**
- Pydantic BaseModel class for classification output with full type safety

**Generated Schema Structure:**
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

**Usage:**
```python
# Basic usage
schema_class = create_classify_schema_class()

# With language support
schema_class_en = create_classify_schema_class(language='English')

# Type-safe data access
result = schema_class(**response_data)
for theme in result.themes:
    print(f"Theme: {theme.theme_name}, Tags: {len(theme.tags)}")
```

### `create_translate_schema_class(terms: List[str]) -> Type[BaseModel]`

Creates a Pydantic schema class for term translation operations based on provided terms.

**Parameters:**
- `terms`: List of terms to be translated (each becomes a required field)

**Returns:**
- Pydantic BaseModel class for translation output with type safety

**Generated Schema Structure:**
```python
# Dynamic field generation based on terms
class TranslationDict(BaseModel):
    term1: str = Field(description="Translation of 'term1'")
    term2: str = Field(description="Translation of 'term2'")
    # ... dynamic fields for each term
    
class TranslateResult(BaseModel):
    translations: TranslationDict
```

**Usage:**
```python
# Dynamic schema creation
terms = ['Summary', 'Themes', 'Total URLs']
schema_class = create_translate_schema_class(terms)

# Type-safe usage
result = schema_class(**response_data)
print(result.translations.Summary)  # Full IDE completion
```

## Key Features

### 1. Complete Type Safety
- **Pydantic Models**: Native Python class definitions with type annotations
- **IDE Support**: Full autocomplete, type checking, and validation across all schemas
- **Field Validation**: Built-in Pydantic validation for all fields and nested structures
- **Type Hints**: Complete typing support throughout the codebase

### 2. Dynamic Language Support
- **Language Parameter**: Pass language code to get localized field descriptions (summarize/classify)
- **Conditional Descriptions**: Adds " in {language}" to relevant description fields
- **Content Localization**: All user-facing text fields support target language output
- **Fallback Behavior**: English descriptions when no language specified

### 3. Flexible Schema Generation
- **Static Schemas**: Summarize and classify use predefined structures with language variations
- **Dynamic Schemas**: Translate uses `create_model` for runtime field generation
- **Nested Models**: Complex hierarchical structures for classification
- **Clean API**: Consistent function interface across all schema types

### 4. Performance Optimized
- **Direct Class Generation**: No JSON parsing or file I/O overhead
- **Pydantic Performance**: Optimized validation and serialization
- **Memory Efficient**: Native Python object structure with proper nesting
- **Caching**: Pydantic's built-in class caching mechanisms

## Architecture

### Schema Types

1. **Summarization Schema**
   - Fixed structure with 5 fields
   - Character limits for summaries
   - Content validity assessment
   - Multi-language support

2. **Classification Schema**
   - Nested model structure (Theme, ClassificationSummary)
   - Hierarchical data organization
   - Processing metadata tracking
   - Multi-language support

3. **Translation Schema**
   - Dynamic field generation
   - Runtime class creation with `create_model`
   - Flexible term handling
   - API compatibility optimized

### Design Patterns Used

1. **Factory Pattern**: Creates schema classes with different configurations
2. **Builder Pattern**: Constructs complex schemas incrementally
3. **Strategy Pattern**: Different description strategies based on language parameter
4. **Composite Pattern**: Nested model structure for classification
5. **Dynamic Class Factory**: Runtime class generation for translations

## Dependencies

### Internal Dependencies
- `typing`: Optional, List, Type type hints
- `pydantic`: BaseModel, Field, create_model

### External Dependencies
- **pydantic**: Modern data validation and serialization library

## Integration Points

- **summarize.py**: Uses `create_summarize_schema_class` for content analysis
- **classify.py**: Uses `create_classify_schema_class` for tag organization
- **translate.py**: Uses `create_translate_schema_class` for term translation
- **llm7shi**: Direct integration with `config_from_schema(PydanticClass)`
- **Translation Cache**: Works seamlessly with translation caching system
- **Testing**: Type-safe schema validation across all operations

## Migration History

### Evolution Path
1. **Phase 1**: JSON files → Code-based dictionary generation
2. **Phase 2**: Dictionary-based → Pydantic class generation
3. **Phase 3**: Separate modules → Consolidated schema.py module

### Before (Dict-Based Example):
```python
def build_summarize_schema(language: Optional[str] = None) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": f"Page title{lang_suffix}..."
            },
            # ... nested dictionary definitions
        }
    }
```

### After (Pydantic-Based):
```python
def create_summarize_schema_class(language: Optional[str] = None) -> Type[BaseModel]:
    class SummarizeResult(BaseModel):
        title: str = Field(description=f"Page title{lang_suffix}...")
        # ... typed field definitions
    
    return SummarizeResult
```

## Benefits

1. **Complete Type Safety**: Full IDE support and compile-time validation
2. **Performance**: No JSON schema parsing or file I/O overhead
3. **Developer Experience**: Autocomplete, type checking, and inline documentation
4. **Maintainability**: Clear class definitions instead of nested dictionaries
5. **Validation**: Built-in Pydantic validation with detailed error messages
6. **Integration**: Direct compatibility with modern Python tooling
7. **Debugging**: Clear stack traces and error messages
8. **Documentation**: Self-documenting through type annotations and Field descriptions
9. **Consolidation**: Single source of truth for all schema definitions

## Usage Guidelines

### Content Analysis (Summarization)
- **Character Limits**: One-line (50 chars), detailed (200-400 chars)
- **Quality Assessment**: `is_valid_content` filters meaningless content
- **Tag System**: Flexible categorization (linguistics, mathematics, physics, programming)
- **Title Extraction**: Appropriate title inferred from content

### Tag Organization (Classification)
- **Theme Structure**: Name, description, and associated tags
- **Processing Metadata**: Track total tags processed and themes created
- **Methodology Documentation**: Explain classification approach
- **Hierarchical Organization**: Nested models for complex structures

### Term Translation
- **Dynamic Fields**: Each term becomes a typed field
- **Flexible Structure**: Adapts to any list of terms
- **Type Safety**: Full validation and IDE support
- **API Compatibility**: Optimized for Gemini API constraints

## Technical Notes

- **Pydantic v2 Compatibility**: Uses modern `model_json_schema()` method
- **Gemini API Constraints**: Avoids `extra='forbid'` for API compatibility
- **Dynamic Class Generation**: `create_model` enables runtime type safety
- **Nested Validation**: Complex hierarchical structures with full validation
- **Language Neutrality**: Technical fields remain consistent across languages
- **Performance**: O(1) for static schemas, O(n) for dynamic translation schemas

## Examples

### Complete Workflow Example
```python
from url2md.schema import (
    create_summarize_schema_class,
    create_classify_schema_class,
    create_translate_schema_class
)
from llm7shi import config_from_schema

# 1. Summarization with Japanese output
summarize_schema = create_summarize_schema_class(language='Japanese')
summarize_config = config_from_schema(summarize_schema)

# 2. Classification with English descriptions
classify_schema = create_classify_schema_class(language='English')
classify_config = config_from_schema(classify_schema)

# 3. Dynamic translation schema
terms_to_translate = ['Summary', 'Themes', 'Total URLs']
translate_schema = create_translate_schema_class(terms_to_translate)
translate_config = config_from_schema(translate_schema)

# Type-safe usage with full IDE support
summary_result = summarize_schema(**summary_data)
classification_result = classify_schema(**classification_data)
translation_result = translate_schema(**translation_data)
```

This consolidated module provides a clean, type-safe foundation for all AI-powered operations in url2md while maintaining the flexibility and performance benefits of the Pydantic-based approach.