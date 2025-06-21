# Test Translation Cache Documentation

## Overview
The `test_translation_cache.py` module provides comprehensive unit tests for the translation caching functionality in url2md. It tests the `TranslationCache` class which manages persistent storage of UI term translations, ensuring efficient multilingual support without repeated AI translation calls.

## Dependencies and Imports
- **tempfile**: For creating temporary test directories
- **pathlib.Path**: For file system path operations
- **url2md.translation_cache**: TranslationCache class being tested

## Basic Operations Tests

### `test_translation_cache_basic_operations()`
Tests fundamental translation cache operations.
- **Purpose**: Verify core CRUD operations work correctly
- **Initial State**: Empty cache with no translations
- **Operations Tested**:
  - `get_all_translations()` - Retrieve all cached translations
  - `get_translation(term, language)` - Retrieve specific translation
  - `has_translation(term, language)` - Check translation existence
  - `add_translation(term, language, translation)` - Add new translation
- **Test Data**: Japanese translations for "Summary" (概要) and "Themes" (テーマ), plus Chinese translation for "Summary" (摘要)
- **Key Assertions**:
  - Empty cache initially has no translations
  - Added translations retrievable by term and language
  - `has_translation()` correctly identifies presence/absence
  - Multiple languages supported for same term

## Persistence Tests

### `test_translation_cache_persistence()`
Tests translation data persistence across cache instances.
- **Purpose**: Verify translations survive cache object recreation
- **Workflow**:
  1. Create cache → add translations → save to disk
  2. Create new cache instance from same directory
  3. Verify translations loaded automatically
- **Translation Data**: Japanese UI terms (Summary, Themes, Total URLs)
- **File Verification**: TSV file exists with correct content structure
- **Cross-Instance Testing**: New instance contains identical data
- **Key Assertions**:
  - TSV file created with proper header
  - All translations present in file content
  - New instance loads all translations correctly

## TSV Format Tests

### `test_translation_cache_tsv_format()`
Tests TSV file format compliance and structure.
- **Purpose**: Verify TSV file meets expected format specifications
- **TSV Structure**:
  - **Header**: `English	Language	Translation`
  - **Data Lines**: Tab-separated values for each translation
  - **Format**: UTF-8 encoding with proper field separation
- **Test Data**: Mixed language translations (Japanese and Chinese)
- **Format Verification**:
  - Correct number of lines (header + data)
  - Proper tab separation
  - All entries present regardless of insertion order
- **Key Assertions**: TSV format compliance, data integrity preservation

### `test_translation_cache_sanitization()`
Tests sanitization of problematic characters in translations.
- **Purpose**: Ensure TSV format integrity with special characters
- **Problematic Characters**: Tabs, newlines, carriage returns in term/translation text
- **Test Input**: `"Text with\ttabs and\nnewlines\r\nand more"`
- **Sanitization Process**:
  - Tabs in content → spaces
  - Newlines in content → spaces  
  - Carriage returns → spaces
  - TSV field separators preserved
- **Verification Process**:
  1. Add translation with problematic characters
  2. Save to TSV file
  3. Verify field separation maintained
  4. Verify content sanitized appropriately
  5. Reload and verify data integrity
- **Key Assertions**: Special characters sanitized, data retrievable after reload

## Advanced Operations Tests

### `test_translation_cache_clear()`
Tests cache clearing functionality.
- **Purpose**: Verify cache can be completely reset
- **Setup**: Cache with multiple translations
- **Clear Operation**: `tc.clear()` removes all translations
- **Verification**: Empty cache after clear operation
- **Key Assertions**: All translations removed, cache returns to empty state

### `test_translation_cache_multiple_languages()`
Tests multi-language support for individual terms.
- **Purpose**: Verify same term can have translations in multiple languages
- **Test Scenario**: "Summary" translated to 4 languages:
  - Japanese: "概要"
  - Chinese: "摘要"  
  - French: "Résumé"
  - Spanish: "Resumen"
- **Operations**: Add all translations → save → reload → verify
- **Persistence Testing**: All languages preserved across cache instances
- **Key Assertions**: 
  - All 4 translations stored correctly
  - Language-specific retrieval accurate
  - Cross-instance persistence maintained

### `test_translation_cache_empty_file()`
Tests behavior with non-existent or empty cache files.
- **Purpose**: Verify graceful handling of missing cache data
- **Initial State**: No TSV file exists
- **Expected Behavior**: Empty cache, no errors
- **File Creation**: TSV file created only when translations saved
- **Reload Testing**: Data accessible after file creation
- **Key Assertions**: 
  - No errors with missing file
  - File created on demand
  - Data persists after creation

## Testing Patterns and Approaches

### CRUD Operation Testing
Comprehensive testing of Create, Read, Update, Delete operations:
- Adding translations (Create)
- Retrieving translations (Read)  
- Implicit updates through re-adding
- Clearing cache (Delete)

### File Format Compliance Testing
Rigorous TSV format validation:
- Header row structure
- Field separation consistency
- Character encoding handling
- Special character sanitization

### Cross-Instance Persistence Testing
Verification of data survival across object lifecycles:
- Save in one instance
- Load in different instance
- Data integrity maintenance
- Automatic loading behavior

### Multi-Language Robustness Testing
Comprehensive multilingual support validation:
- Unicode character support
- Language isolation (same term, different languages)
- Character encoding preservation
- Cross-language data integrity

## Key Implementation Details

### TSV File Structure
Tests verify exact TSV format compliance:
- **Header**: Fixed 3-column header (`English`, `Language`, `Translation`)
- **Encoding**: UTF-8 throughout
- **Separators**: Tab characters between fields
- **Sanitization**: Special characters replaced with spaces

### Data Key Structure
Tests verify translation identification system:
- **Primary Key**: (English term, target language) tuple
- **Uniqueness**: One translation per term-language combination
- **Case Sensitivity**: Maintained throughout system

### Lazy Loading Strategy
Tests verify efficient resource usage:
- Files created only when data exists
- No unnecessary file operations
- Automatic loading when cache instances created

### Character Handling
Tests verify robust character processing:
- Unicode support for all languages
- Special character sanitization for TSV compliance
- Encoding preservation throughout pipeline

## Edge Cases Covered

### File System Edge Cases
- Non-existent cache directories
- Permission and access issues
- Corrupted or malformed TSV files

### Data Content Edge Cases
- Empty translations
- Special characters in terms and translations
- Very long translation strings
- Unicode and multi-byte characters

### Multi-Language Edge Cases
- Same term in many languages
- Language code variations
- Character encoding differences

### Concurrency Edge Cases
- Multiple cache instances accessing same file
- File locking and access coordination
- Data consistency across instances

## Testing Strategy

The translation cache test suite employs a **comprehensive data lifecycle testing** approach:

### Data Operations Testing
- Individual operation correctness
- Operation combination effects
- Edge case handling

### Persistence Testing
- File format compliance
- Cross-instance data flow
- Long-term storage reliability

### Multi-Language Testing
- Unicode character support
- Language isolation verification
- Scalability with many languages

### Integration Testing
- File system integration
- Character encoding pipeline
- Error handling throughout

This thorough testing ensures the translation cache system provides reliable, efficient multilingual support while maintaining data integrity and handling edge cases gracefully, enabling seamless multilingual report generation without repeated AI translation costs.