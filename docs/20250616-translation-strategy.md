# Translation Strategy

This document outlines the translation approach used in url2md for multi-language support.

## Overview

url2md implements a comprehensive translation strategy that leverages LLM capabilities to provide dynamic, contextual translations without requiring pre-translated resource files.

## Current Implementation (v0.3.0)

### Two-Phase Translation Approach with Caching

When users specify a language with `classify -l LANGUAGE`, the system performs two complementary translation processes:

1. **Content Generation in Target Language**
   - Theme names and descriptions are generated directly in the specified language
   - Uses `{ in language}` placeholder in JSON schemas
   - Processed during the main classification LLM call

2. **UI Term Translation with Cache**
   - Report interface elements are translated separately
   - Uses dedicated `translate_report_terms()` function with caching
   - Translations cached in `cache/terms.tsv` to avoid repeated LLM calls
   - Cache-first approach: check cache before calling LLM

### Schema-Based Language Support

**Classification Schema** (`schemas/classify.json`):
```json
{
  "theme_name": {
    "description": "Name of the theme{ in language}"
  },
  "theme_description": {
    "description": "Brief description of the theme{ in language}"
  },
  "classification_approach": {
    "description": "Explanation of methodology{ in language}"
  }
}
```

**Translation Schema** (`schemas/translate.json`):
```json
{
  "translations": {
    "properties": {
      ```translation_properties```
    },
    "required": [```translation_required```]
  }
}
```

Where placeholders are dynamically replaced with:
- ````translation_properties````: Individual property definitions for each term
- ````translation_required````: Required field list

**Translation Cache** (`cache/terms.tsv`):
```
English	Language	Translation
Summary	Japanese	概要
Themes	Japanese	テーマ
Total URLs	Japanese	総URL数
Classified	Japanese	分類済
Unclassified	Japanese	未分類
URLs	Japanese	URL
Other	Japanese	その他
```

### Implementation Details

**Translation Module Architecture**:
- **Generic Translation Module** (`translate.py`): Provides reusable translation functionality
  - `translate_terms()`: Main translation function for any list of terms
  - `create_translation_schema()`: Dynamic schema generation
  - `create_translation_prompt()`: Flexible prompt creation
- **TSVManager Base Class**: Common TSV file operations (load, save, sanitization)
- **TranslationCache Class**: Inherits from TSVManager, manages translation storage
- **Cache Integration**: Cache class includes translation_cache field

**Automatic Translation Integration** (`classify.py`):
```python
# Handle translation if language is specified and translation is needed
if language and needs_translation(language, cache):
    translate_report_terms(language, model, cache)
```

**Generic Translation Function** (`translate.py`):
```python
def translate_terms(terms: List[str], language: str, model: str = None) -> Dict[str, str]:
    """Translate a list of terms to the specified language"""
    # Generate schema dynamically based on terms
    schema_content = create_translation_schema(terms, language)
    prompt = create_translation_prompt(terms, language)
    
    # Configure and call LLM
    config = config_from_schema_string(schema_content)
    response = generate_content_retry(model, config, [prompt])
    
    # Return translations
    translation_data = json.loads(response.strip())
    return translation_data.get('translations', {})
```

**Translation Process**:
1. **Check Cache**: `needs_translation()` verifies if all terms are cached
2. **LLM Call**: Only call LLM for missing translations
3. **Cache Update**: Store new translations in `terms.tsv`
4. **Report Usage**: Report generation reads from cache

**User Experience**:
- Single command: `uv run url2md classify -l Japanese`
- Complete localization: content + UI elements
- Efficient caching: Avoid repeated LLM calls for same language
- Cache persistence: Translations saved across sessions

## Design Principles

### 1. User-Centric Efficiency
- **Single Command Execution**: Users specify language once, get complete localization
- **Transparent Processing**: Internal complexity hidden from user interface
- **Natural Workflow**: Language specification integrates naturally with existing commands
- **Performance Optimization**: Cache-first approach minimizes LLM API usage

### 2. LLM-Powered Flexibility
- **Dynamic Translation**: No static translation files to maintain
- **Contextual Accuracy**: LLM understands domain-specific terminology
- **Quality Consistency**: Same model handles all translation aspects

### 3. Separation of Concerns
- **Content Generation**: Domain-specific content in target language
- **UI Translation**: Interface elements translated separately
- **Independent Processing**: Each aspect can be optimized individually

### 4. Technical Architecture
- **Schema-Driven**: JSON schemas define translation requirements
- **Placeholder System**: `{ in language}` enables dynamic schema modification
- **Fallback Mechanism**: English terms used when translations unavailable
- **Cache-First Design**: Check cache before LLM calls for efficiency
- **Inheritance-Based**: TSVManager provides common file operations

## Current Translation Coverage

### Fully Supported
- **Theme Content**: Names, descriptions, classification approaches
- **Report Headers**: Summary, Themes, Total URLs, Classified, Unclassified, URLs, Other
- **Report Structure**: Complete markdown report localization

### Expansion Opportunities
- **Progress Messages**: "Classifying tags using model", "Total unique tags"
- **Error Messages**: Classification failures, file access errors
- **Statistics Display**: Frequency distributions, tag analysis
- **Help Text**: Command descriptions and usage information

## Implementation Strategy for Extensions

### 1. Using the Generic Translation Module

The `translate.py` module provides a flexible foundation for adding translation support to any part of the application:

```python
from url2md.translate import translate_terms

# Example: Translate custom terms
terms_to_translate = ["Progress", "Error", "Complete", "Failed"]
translations = translate_terms(terms_to_translate, "Japanese")

# Use translations with fallback
def get_translated(term, translations):
    return translations.get(term, term)  # Fallback to original

print(get_translated("Progress", translations))  # Shows translated term or "Progress"
```

### 2. Extending Report Terms

To add new report terms:

```python
# In classify.py, extend TRANSLATION_TERMS
TRANSLATION_TERMS = [
    'Summary', 'Themes', 'Total URLs', 'Classified', 
    'Unclassified', 'URLs', 'Other',
    # New terms
    'Statistics', 'Tags', 'Frequency'
]
```

### 3. Creating Domain-Specific Translation Functions

For specialized translation needs:

```python
def translate_error_messages(language: str, cache: Optional[Cache] = None) -> Dict[str, str]:
    """Translate common error messages"""
    ERROR_TERMS = [
        "File not found",
        "Invalid URL",
        "Network error",
        "API key missing"
    ]
    
    # Check cache first
    missing_terms = []
    translations = {}
    
    if cache and cache.translation_cache:
        for term in ERROR_TERMS:
            cached = cache.translation_cache.get_translation(term, language)
            if cached:
                translations[term] = cached
            else:
                missing_terms.append(term)
    else:
        missing_terms = ERROR_TERMS
    
    # Translate missing terms
    if missing_terms:
        new_translations = translate_terms(missing_terms, language)
        translations.update(new_translations)
        
        # Update cache
        if cache and cache.translation_cache:
            for term, translation in new_translations.items():
                cache.translation_cache.add_translation(term, language, translation)
            cache.translation_cache.save()
    
    return translations
```

### 4. Apply Translations
Modify output functions to use translated terms when available, with English fallback.

## Benefits of This Approach

### Technical Benefits
- **No Maintenance Overhead**: No static translation files to update
- **Consistent Quality**: Single LLM model ensures translation consistency
- **Flexible Coverage**: Can handle specialized terminology dynamically
- **Efficient Caching**: Persistent cache reduces API usage and improves performance
- **Modular Architecture**: TSVManager base class enables code reuse
- **Generic Translation Module**: Reusable translation functionality for any terms

### User Benefits
- **Complete Localization**: Both content and interface in target language
- **Simple Usage**: Single language parameter for full translation
- **Professional Output**: Contextually appropriate translations
- **Fast Performance**: Cached translations provide instant response

### Development Benefits
- **Extensible Design**: Easy to add new translatable elements using generic module
- **Clean Architecture**: Clear separation between content and UI translation
- **Testable Components**: Each translation aspect can be tested independently
- **Reusable Functions**: Generic translation module can be used throughout the codebase

## Future Considerations

### Performance Optimization
- ✅ **Translation Caching**: Implemented in v0.3.0 with TSV-based cache
- ✅ **Cache-First Approach**: Check cache before LLM calls
- Consider batch translation requests for multiple languages
- Monitor API usage patterns and cache hit rates

### Quality Assurance
- Implement translation validation mechanisms
- Consider user feedback collection for translation quality
- Maintain fallback strategies for translation failures

### Coverage Expansion
- Systematically review all user-facing text
- Prioritize high-impact translation opportunities
- Consider context-sensitive translation approaches

## Conclusion

The current translation strategy successfully balances efficiency, quality, and maintainability. By leveraging LLM capabilities for dynamic translation while implementing intelligent caching, url2md provides comprehensive multi-language support without the overhead of traditional localization approaches.

The cache-first design significantly improves performance and reduces API usage while maintaining the flexibility of LLM-powered translation. The TSVManager-based architecture ensures clean code organization and enables easy extension for future translation needs.

The design is well-positioned for future expansion, allowing systematic extension of translation coverage while preserving the core benefits of the cached LLM-powered approach.