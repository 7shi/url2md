# summarize_schema.py

## Overview

The `summarize_schema.py` module provides Pydantic-based schema generation for URL content summarization operations. It defines type-safe models for AI-powered content analysis with multi-language support, replacing the previous JSON file-based approach with native Python class definitions and complete IDE support.

## Functions

### `create_summarize_schema_class(language: Optional[str] = None) -> Type[BaseModel]`

Creates a Pydantic schema class for URL content summarization operations.

**Parameters:**
- `language`: Optional language code for localized output descriptions

**Returns:**
- Pydantic BaseModel class for summarization output with full type safety

**Generated Schema Structure:**
The schema creates a typed Pydantic model with the following structure:

```python
class SummarizeResult(BaseModel):
    title: str = Field(description="Page title (appropriate title inferred from content)")
    summary_one_line: str = Field(description="Concise one-line summary within 50 characters")
    summary_detailed: str = Field(description="Detailed summary of 200-400 characters...")
    tags: List[str] = Field(description="List of tags representing the content...")
    is_valid_content: bool = Field(description="Whether the content is meaningful...")
```

## Key Features

### 1. Complete Type Safety
- **Pydantic Models**: Native Python class definitions with type annotations
- **IDE Support**: Full autocomplete, type checking, and validation
- **Field Validation**: Built-in Pydantic validation for all fields
- **Type Hints**: Complete typing support throughout the codebase

### 2. Dynamic Language Support
- **Language Parameter**: Pass language code to get localized field descriptions
- **Conditional Descriptions**: Adds " in {language}" to relevant description fields
- **Content Localization**: All text fields support target language output
- **Fallback Behavior**: English descriptions when no language specified

### 3. Content Analysis Structure
- **Multi-level Summaries**: Both concise and detailed summary fields with character limits
- **Semantic Tagging**: Flexible typed tag system for content categorization
- **Quality Assessment**: Built-in content validity detection
- **Title Extraction**: Dedicated field for page title information

### 4. Performance Optimized
- **Direct Class Generation**: No JSON parsing or file I/O overhead
- **Pydantic Performance**: Optimized validation and serialization
- **Memory Efficient**: Native Python object structure
- **Caching**: Pydantic's built-in class caching mechanisms

## Dependencies

### Internal Dependencies
- `typing`: Optional, Dict, Any, List, Type type hints
- `pydantic`: BaseModel, Field for schema definition

### External Dependencies
- **pydantic**: Modern data validation and serialization library

## Design Patterns Used

1. **Factory Pattern**: Creates schema classes with different language configurations
2. **Builder Pattern**: Constructs schema incrementally based on parameters
3. **Strategy Pattern**: Different description strategies based on language parameter
4. **Template Method**: Consistent schema structure with variable content

## Important Implementation Details

1. **Field Definitions**:
   - **title**: Appropriate title inferred from content analysis (localized)
   - **summary_one_line**: Character-limited (50 chars) for display consistency (localized)
   - **summary_detailed**: 200-400 characters including topics, educational value (localized)
   - **tags**: List[str] with examples (linguistics, mathematics, physics, programming)
   - **is_valid_content**: Boolean filter for error pages and empty content

2. **Language Integration Strategy**:
   ```python
   lang_suffix = f" in {language}" if language else ""
   
   title: str = Field(
       description=f"Page title{lang_suffix} (appropriate title inferred from content)"
   )
   ```

3. **Type Safety Implementation**:
   - All fields properly typed with Python type hints
   - Field descriptions provide documentation
   - Return type annotation ensures correct usage
   - Pydantic handles validation automatically

4. **Performance Characteristics**:
   - O(1) complexity for schema generation
   - No file I/O operations
   - Direct memory allocation
   - Pydantic's optimized validation

## Usage Examples

```python
# Basic schema class creation
SummarizeSchema = create_summarize_schema_class()

# Schema with Japanese localization
SummarizeSchemaJP = create_summarize_schema_class(language='Japanese')

# Integration with llm7shi
from llm7shi import config_from_schema

schema_class = create_summarize_schema_class(language='English')
config = config_from_schema(schema_class)

# Type-safe usage with IDE support
result_data = {
    "title": "Example Article",
    "summary_one_line": "Brief summary of the content",
    "summary_detailed": "Detailed analysis of the content including main topics...",
    "tags": ["programming", "tutorial", "python"],
    "is_valid_content": True
}

# Pydantic validation and type-safe access
result = schema_class(**result_data)
print(result.title)  # Full IDE completion and type checking
print(len(result.tags))  # Type-aware operations
```

## Migration from Dict-Based Approach

This module migrated from dictionary-based JSON schema generation to Pydantic class generation.

### Before (Dict-Based):
```python
def build_summarize_schema(language: Optional[str] = None) -> Dict[str, Any]:
    lang_suffix = f" in {language}" if language else ""
    
    return {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": f"Page title{lang_suffix} (appropriate title inferred from content)"
            },
            # ... more nested dictionary definitions
        },
        "required": ["title", "summary_one_line", "summary_detailed", "tags", "is_valid_content"]
    }
```

### After (Pydantic-Based):
```python
def create_summarize_schema_class(language: Optional[str] = None) -> Type[BaseModel]:
    lang_suffix = f" in {language}" if language else ""
    
    class SummarizeResult(BaseModel):
        title: str = Field(
            description=f"Page title{lang_suffix} (appropriate title inferred from content)"
        )
        summary_one_line: str = Field(
            description=f"Concise one-line summary{lang_suffix} within 50 characters"
        )
        summary_detailed: str = Field(
            description=f"Detailed summary{lang_suffix} of 200-400 characters..."
        )
        tags: List[str] = Field(
            description=f"List of tags{lang_suffix} representing the content..."
        )
        is_valid_content: bool = Field(
            description="Whether the content is meaningful (not error pages or empty pages)"
        )
    
    return SummarizeResult
```

## Integration Points

- **summarize.py**: Primary consumer using `create_summarize_schema_class`
- **llm7shi**: Direct integration with `config_from_schema(PydanticClass)`
- **Testing**: Type-safe schema validation and testing
- **Multi-language**: Works seamlessly with translation system

## Benefits Over Previous Approach

1. **Complete Type Safety**: Full IDE support and compile-time validation
2. **Performance**: No JSON schema parsing or file I/O overhead
3. **Developer Experience**: Autocomplete, type checking, and inline documentation
4. **Maintainability**: Clear class definitions instead of nested dictionaries
5. **Validation**: Built-in Pydantic validation with detailed error messages
6. **Integration**: Direct compatibility with modern Python tooling
7. **Debugging**: Clear stack traces and error messages in Python code
8. **Documentation**: Self-documenting through type annotations and Field descriptions

## Content Analysis Guidelines

### Character Limits and Expectations
- **One-line summary**: 50 characters maximum for display consistency
- **Detailed summary**: 200-400 characters range including main topics
- **Tags**: Relevant content categories (e.g., linguistics, mathematics, physics, programming)

### Quality Assessment
- **is_valid_content**: Filters out error pages, empty content, and meaningless responses
- **Educational Value**: Emphasis on academic and educational content assessment
- **Technical Fields**: Identification and categorization of technical content

### Language Support
- **Localized Descriptions**: All user-facing content fields support target language
- **Technical Fields**: Language-neutral validation fields remain consistent
- **Backward Compatibility**: Fully compatible with existing multi-language workflows

## Technical Notes

- Uses standard Pydantic Field definitions for maximum compatibility
- Each generated class is fully typed and provides complete IDE support
- Compatible with all Pydantic v2 features and validation rules
- Designed for seamless integration with LLM-based content analysis workflows