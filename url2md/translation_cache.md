# translation_cache.py

## Overview

The `translation_cache.py` module implements a caching system for translated terms to avoid repeated LLM API calls. It extends TSVManager to provide persistent storage of translations in TSV format, supporting multi-language translation caching for UI terms used in reports.

## Classes and Their Methods

### TranslationCache

A specialized TSV manager for caching translations with the format: English\tLanguage\tTranslation

**Attributes:**
- `_translations` (Dict[tuple, str]): In-memory cache mapping (english, language) tuples to translations

**Methods:**

#### `__init__(self, cache_dir: Path)`
Initializes the translation cache with a cache directory. Creates the TSV file at `cache_dir/terms.tsv` and loads existing translations.

#### `load() -> None`
Loads translations from the TSV file into memory. Parses each row as English, Language, Translation and populates the internal dictionary.

#### `save() -> None`
Saves all translations to the TSV file. Converts the internal dictionary to TSV rows with proper headers.

#### `get_translation(english: str, language: str) -> Optional[str]`
Retrieves a cached translation for a given English term and target language.

**Parameters:**
- `english`: The English term to translate
- `language`: Target language for translation

**Returns:**
- Cached translation string or None if not found

#### `add_translation(english: str, language: str, translation: str) -> None`
Adds a new translation to the cache.

**Parameters:**
- `english`: The English term
- `language`: Target language
- `translation`: The translated term

#### `has_translation(english: str, language: str) -> bool`
Checks if a translation exists in the cache.

**Returns:**
- True if the translation is cached, False otherwise

#### `get_all_translations() -> Dict[tuple, str]`
Returns a copy of all cached translations.

**Returns:**
- Dictionary mapping (english, language) tuples to translations

#### `clear() -> None`
Clears all translations from memory (does not affect the file until save() is called).

## Key Design Patterns Used

1. **Inheritance Pattern**: Extends TSVManager for file operations
2. **Cache Pattern**: In-memory dictionary for fast lookups
3. **Tuple Key Pattern**: Uses (english, language) tuples as unique keys
4. **Defensive Copy Pattern**: Returns copy of internal data in get_all_translations()

## Dependencies

### Internal Dependencies
- `.tsv_manager`: TSVManager base class for TSV file operations

### External Dependencies
- `pathlib`: For path manipulation
- `typing`: For type hints

## Important Implementation Details

1. **File Format**:
   - Fixed TSV format: English\tLanguage\tTranslation
   - First row contains headers
   - Each subsequent row is one translation

2. **Cache Key Design**:
   - Uses (english, language) tuples as dictionary keys
   - Ensures unique translations per language
   - Case-sensitive matching

3. **Memory Management**:
   - All translations loaded into memory on initialization
   - Changes only persisted when save() is called
   - Clear() only affects memory, not the file

4. **Data Integrity**:
   - Inherits TSV sanitization from TSVManager
   - Tabs and newlines in translations are replaced with spaces
   - Empty or malformed rows are skipped during load

5. **Usage Pattern**:
   - Load existing translations on startup
   - Check cache before making LLM calls
   - Add new translations after LLM responses
   - Save periodically or at shutdown

6. **Integration Points**:
   - Used by Cache class for centralized translation management
   - Accessed by report generation for UI term translations
   - Updated by classification commands when language is specified