# translate.py

## Overview

The `translate.py` module provides generic translation functionality using LLM APIs. It offers utilities for dynamically generating translation schemas and prompts, making it reusable for translating any list of terms to any target language with structured JSON output.

## Functions

### `create_translation_schema(terms: List[str], language: str) -> str`

Dynamically generates a JSON schema for translation based on the provided terms and target language.

**Parameters:**
- `terms`: List of terms to translate
- `language`: Target language for translation

**Returns:**
- JSON schema string with placeholders replaced

**Implementation Details:**
- Loads base schema from `schemas/translate.json`
- Generates property definitions for each term
- Replaces placeholders in the schema template
- Each term becomes a required string property

### `create_translation_prompt(terms: List[str], language: str) -> str`

Generates a natural language prompt for the LLM to translate terms.

**Parameters:**
- `terms`: List of terms to translate
- `language`: Target language for translation

**Returns:**
- Formatted prompt string

**Prompt Structure:**
- Lists all terms to translate
- Specifies target language
- Requests concise, context-appropriate translations
- Emphasizes maintaining order

### `translate_terms(terms: List[str], language: str, model: str) -> Dict[str, str]`

Main function that translates a list of terms using the specified LLM model.

**Parameters:**
- `terms`: List of terms to translate
- `language`: Target language
- `model`: LLM model identifier to use

**Returns:**
- Dictionary mapping original terms to their translations

**Process:**
1. Generates dynamic schema for the terms
2. Creates translation prompt
3. Configures LLM with schema for structured output
4. Calls LLM API and parses JSON response
5. Returns translation mappings

## Key Design Patterns Used

1. **Template Pattern**: Uses base schema as template with placeholders
2. **Builder Pattern**: Dynamically builds schema and prompt
3. **Schema-Driven Design**: Ensures structured LLM output
4. **Separation of Concerns**: Separates schema generation, prompt creation, and API calls

## Dependencies

### Internal Dependencies
- `.utils`: Uses `get_resource_path()` for schema file access

### External Dependencies
- `json`: For JSON parsing and manipulation
- `llm7shi`: LLM integration package
  - `generate_content_retry`: For LLM API calls with retry
  - `config_from_schema`: For schema configuration
  - `build_schema_from_json`: For schema object creation
- `typing`: For type hints

## Important Implementation Details

1. **Schema Generation**:
   - Base schema loaded from `schemas/translate.json`
   - Properties dynamically generated for each term
   - All terms marked as required fields
   - Placeholders (```translation_properties```, ```translation_required```) replaced

2. **Prompt Engineering**:
   - Clear instruction format
   - Terms presented as bulleted list
   - Emphasizes conciseness and context-appropriateness
   - Requests exact order preservation

3. **LLM Integration**:
   - Uses structured output via JSON schema
   - Three-step schema processing: string → dict → Schema → config
   - Expects response with 'translations' key
   - Handles JSON parsing of LLM response

4. **Error Handling**:
   - No explicit error handling - exceptions propagate
   - Relies on llm7shi's retry mechanism
   - JSON parsing errors will raise exceptions

5. **Flexibility**:
   - Generic design works with any term list
   - Language-agnostic implementation
   - Model-agnostic (any llm7shi-supported model)
   - No hardcoded term lists

6. **Usage Context**:
   - Used by classify.py for report term translations
   - Can be used independently for any translation needs
   - Designed for UI terms but works for any short text