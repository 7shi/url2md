# Translation Strategy

This document outlines the translation approach used in url2md for multi-language support.

## Overview

url2md implements a comprehensive translation strategy that leverages LLM capabilities to provide dynamic, contextual translations without requiring pre-translated resource files.

## Current Implementation (v0.3.0)

### Two-Phase Translation Approach

When users specify a language with `classify -l LANGUAGE`, the system performs two complementary translation processes:

1. **Content Generation in Target Language**
   - Theme names and descriptions are generated directly in the specified language
   - Uses `{ in language}` placeholder in JSON schemas
   - Processed during the main classification LLM call

2. **UI Term Translation**
   - Report interface elements are translated separately
   - Uses dedicated `translate_report_terms()` function
   - Handled via a second, specialized LLM call

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
    "Summary": {"description": "Translation of 'Summary' to {language}"},
    "Themes": {"description": "Translation of 'Themes' to {language}"},
    "Total URLs": {"description": "Translation of 'Total URLs' to {language}"},
    // ... other UI terms
  }
}
```

### Implementation Details

**Automatic Translation Integration** (`classify.py:189-194`):
```python
# Add translations if language is specified
if language:
    translations = translate_report_terms(language, model)
    classification_data['translations'] = translations
```

**User Experience**:
- Single command: `uv run url2md classify -l ja`
- Complete localization: content + UI elements
- No pre-translation required

## Design Principles

### 1. User-Centric Efficiency
- **Single Command Execution**: Users specify language once, get complete localization
- **Transparent Processing**: Internal complexity hidden from user interface
- **Natural Workflow**: Language specification integrates naturally with existing commands

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

### 1. Identify Translation Candidates
Review user-facing text in:
- Terminal output messages
- Error handling strings
- Progress indicators
- Statistical summaries

### 2. Extend Translation Schema
Add new translation terms to `schemas/translate.json`:
```json
{
  "translations": {
    // Existing terms...
    "progress_classifying": {
      "description": "Translation of 'Classifying tags using model' to {language}"
    },
    "stats_unique_tags": {
      "description": "Translation of 'Total unique tags' to {language}"
    }
  }
}
```

### 3. Update Translation Function
Extend `translate_report_terms()` to include additional terms and return comprehensive translation mapping.

### 4. Apply Translations
Modify output functions to use translated terms when available, with English fallback.

## Benefits of This Approach

### Technical Benefits
- **No Maintenance Overhead**: No static translation files to update
- **Consistent Quality**: Single LLM model ensures translation consistency
- **Flexible Coverage**: Can handle specialized terminology dynamically

### User Benefits
- **Complete Localization**: Both content and interface in target language
- **Simple Usage**: Single language parameter for full translation
- **Professional Output**: Contextually appropriate translations

### Development Benefits
- **Extensible Design**: Easy to add new translatable elements
- **Clean Architecture**: Clear separation between content and UI translation
- **Testable Components**: Each translation aspect can be tested independently

## Future Considerations

### Performance Optimization
- Consider caching translations for repeated terms
- Batch translation requests when possible
- Monitor API usage patterns

### Quality Assurance
- Implement translation validation mechanisms
- Consider user feedback collection for translation quality
- Maintain fallback strategies for translation failures

### Coverage Expansion
- Systematically review all user-facing text
- Prioritize high-impact translation opportunities
- Consider context-sensitive translation approaches

## Conclusion

The current translation strategy successfully balances efficiency, quality, and maintainability. By leveraging LLM capabilities for dynamic translation while maintaining clean architectural separation, url2md provides comprehensive multi-language support without the overhead of traditional localization approaches.

The design is well-positioned for future expansion, allowing systematic extension of translation coverage while preserving the core benefits of the LLM-powered approach.