# summarize_schema.py

## Overview

The `summarize_schema.py` module provides code-based JSON schema generation for URL content summarization operations. It defines the structure for AI-powered content analysis with multi-language support, replacing the previous JSON file-based approach with type-safe Python functions.

## Functions

### `build_summarize_schema(language: Optional[str] = None) -> Dict[str, Any]`

Builds a JSON schema for URL content summarization operations.

**Parameters:**
- `language`: Optional language code for localized output descriptions

**Returns:**
- Dictionary containing the complete JSON schema for summarization output

**Schema Structure:**
The schema defines the following required properties:

- **title**: String - Page title inferred from content (localized if language specified)
- **summary_one_line**: String - Concise one-line summary within 50 characters (localized)
- **summary_detailed**: String - Detailed 200-400 character summary (localized)
- **tags**: Array of strings - Content representation tags (localized)
- **is_valid_content**: Boolean - Whether content is meaningful (not error/empty pages)

## Key Features

### 1. Dynamic Language Support
- **Language Parameter**: Pass language code to get localized field descriptions
- **Conditional Suffix**: Adds " in {language}" to relevant description fields
- **Content Localization**: All text fields support target language output
- **Fallback Behavior**: English descriptions when no language specified

### 2. Content Analysis Structure
- **Multi-level Summaries**: Both concise and detailed summary fields
- **Semantic Tagging**: Flexible tag system for content categorization
- **Quality Assessment**: Built-in content validity detection
- **Title Extraction**: Dedicated field for page title information

### 3. Type Safety
- **Static Typing**: All return types explicitly defined
- **Dictionary Construction**: Direct Python dict manipulation
- **Schema Validation**: Compatible with JSON Schema validators

## Dependencies

### Internal Dependencies
- `typing`: Optional and Dict type hints

### External Dependencies
None - Pure Python implementation

## Design Patterns Used

1. **Builder Pattern**: Constructs schema incrementally based on parameters
2. **Factory Pattern**: Creates schema objects with different configurations
3. **Template Method**: Consistent schema structure with variable content

## Important Implementation Details

1. **Field Descriptions**:
   - **title**: Appropriate title inferred from content analysis
   - **summary_one_line**: Character-limited for display consistency
   - **summary_detailed**: Includes topics, educational value, technical fields
   - **tags**: Examples provided (linguistics, mathematics, physics, programming)
   - **is_valid_content**: Filters out error pages and empty content

2. **Language Integration**:
   - Language suffix applied to user-facing content fields
   - Technical validation fields remain language-neutral
   - Backwards compatible with existing implementations

3. **Character Limits**:
   - One-line summary: 50 characters maximum
   - Detailed summary: 200-400 characters range
   - Provides guidance for consistent output length

4. **Content Categories**:
   - Suggests common tag categories for AI guidance
   - Emphasizes academic and educational value assessment
   - Technical field identification support

## Usage Examples

```python
# Basic schema without language
schema = build_summarize_schema()

# Schema with Japanese localization
schema_jp = build_summarize_schema(language='Japanese')

# Integration with llm7shi
from llm7shi import build_schema_from_json, config_from_schema
schema_dict = build_summarize_schema(language='English')
schema = build_schema_from_json(schema_dict)
config = config_from_schema(schema)
```

## Migration Notes

This module replaces the previous `schemas/summarize.json` file and eliminates:
- File I/O operations for schema loading
- String placeholder replacement (`{ in language}`)
- Resource path management
- JSON parsing errors

The new approach provides:
- Better type safety and IDE support
- Improved performance (no file operations)
- Easier maintenance and version control
- Full compatibility with existing summarize functionality

## Integration Points

- **summarize.py**: Main consumer of this schema
- **llm7shi**: Schema validation and LLM configuration
- **Testing**: Direct import for test validation
- **Multi-language**: Works with translation system