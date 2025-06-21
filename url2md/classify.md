# classify.py

## Overview

The `classify.py` module extracts and analyzes tags from summary files, then uses LLM to classify them into themes. It provides tag statistics, theme-based classification with weights, and handles multi-language report term translations. This module is central to organizing URLs by content themes.

## Global Constants

### `TRANSLATION_TERMS`
List of UI terms that need translation for multi-language reports:
- 'Summary', 'Themes', 'Total URLs', 'Classified', 'Unclassified', 'URLs', 'Other'

## Functions

### `extract_tags(cache: Cache, url_infos: List[URLInfo]) -> List[str]`

Extracts all tags from URLInfo summary files.

**Parameters:**
- `cache`: Cache instance for file access
- `url_infos`: List of URLInfo objects to process

**Returns:**
- List of all tags (may contain duplicates)

**Tag Extraction:**
- Reads JSON summary files
- Handles both list and comma-separated string formats
- Continues on individual file errors

### `display_tag_statistics(tag_counter: Counter)`

Displays comprehensive tag statistics to console.

**Parameters:**
- `tag_counter`: Counter object with tag frequencies

**Statistics Shown:**
- Total unique tags
- Total tag instances
- Frequency distribution
- Tags with frequency ≥ 2

### `get_frequent_tags_with_counts(tag_counter: Counter, min_frequency: int = 2) -> List[tuple]`

Filters tags by minimum frequency threshold.

**Parameters:**
- `tag_counter`: Counter with tag frequencies
- `min_frequency`: Minimum occurrences (default: 2)

**Returns:**
- List of (tag, count) tuples

### `create_tag_classification_prompt(tag_counter: Counter, language: str = None) -> str`

Generates the prompt for LLM tag classification.

**Parameters:**
- `tag_counter`: Counter with tag frequencies
- `language`: Optional output language

**Returns:**
- Formatted prompt string or None if no frequent tags

**Prompt Requirements:**
- Theme classification with clear names
- Theme weights (≥ 1.0)
- Each tag in only one theme
- Complete tag frequency information

### `classify_tags_with_llm(cache: Cache, tag_counter: Counter, model: str, language: str = None) -> Dict[str, Any]`

Main function that classifies tags using LLM and returns structured results.

**Parameters:**
- `cache`: Cache instance for translation management
- `tag_counter`: Counter with tag frequencies
- `model`: LLM model identifier
- `language`: Optional output language

**Returns:**
- Classification data dictionary with themes and metadata

**Process:**
1. Generates classification prompt
2. Builds schema using code-based function
3. Calls LLM with structured output
4. Adds language info if specified
5. Triggers translation if needed

### `needs_translation(language: str, cache: Optional[Cache] = None) -> bool`

Checks if translation is needed for the given language.

**Parameters:**
- `language`: Target language
- `cache`: Optional cache instance

**Returns:**
- True if any terms need translation

### `translate_report_terms(language: str, model: str = None, cache: Optional[Cache] = None) -> None`

Translates report UI terms and updates the cache.

**Parameters:**
- `language`: Target language
- `model`: LLM model to use
- `cache`: Cache instance for storage

**Process:**
1. Identifies missing translations
2. Calls translation API for missing terms
3. Updates translation cache
4. Saves to persistent storage

### `filter_url_infos_by_urls(cache: Cache, target_urls: List[str]) -> List[URLInfo]`

Filters URLInfo objects by target URL list (duplicate of summarize.py version).

## Key Design Patterns Used

1. **Statistics Pattern**: Separates data collection from display
2. **Prompt Engineering**: Structured prompts for consistent output
3. **Schema-Driven Design**: JSON schema for LLM responses
4. **Cache-First Translation**: Checks cache before API calls
5. **Language Placeholder Pattern**: Dynamic schema modification

## Dependencies

### Internal Dependencies
- `.cache`: Cache and translation management
- `.translate`: Generic translation functionality
- `.urlinfo`: URLInfo class
- `.schema`: Pydantic-based schema generation

### External Dependencies
- `json`: JSON parsing
- `collections.Counter`: Tag frequency counting
- `llm7shi`: LLM integration
- `pathlib`: Path operations
- `typing`: Type hints

## Important Implementation Details

1. **Tag Frequency Analysis**:
   - Groups tags by occurrence count
   - Shows distribution (1, 2-4, 5-9, 10+)
   - Only classifies frequent tags (≥2 uses)

2. **Theme Classification**:
   - Each tag assigned to one theme only
   - Themes have weights (1.0 = normal, >1.0 = priority)
   - Includes usage statistics in output

3. **Translation Integration**:
   - Automatic detection of translation needs
   - Only translates missing terms
   - Persistent caching across sessions

4. **Pydantic-Based Schema**:
   - Dynamic schema class generation via `create_classify_schema_class()`
   - Language parameter passed directly to schema class creation function
   - Type-safe Pydantic model manipulation with full IDE support

5. **Error Handling**:
   - Exits on schema file errors
   - Continues on summary read errors
   - No frequent tags triggers error exit

6. **LLM Configuration**:
   - Code-based schema generation
   - Structured JSON output enforced
   - Retry mechanism via llm7shi

7. **Output Structure**:
   - Themes with names and descriptions
   - Tag assignments with frequencies
   - Optional language metadata