# Test HTML Utils Documentation

## Overview
The `test_utils.py` module provides comprehensive unit tests for HTML processing utility functions in url2md. It focuses on testing the `extract_body_content()` and `extract_html_title()` functions, ensuring reliable HTML parsing, content extraction, and proper handling of edge cases in web content processing.

## Test Class Structure

### `TestExtractBodyContent`
Tests HTML body content extraction functionality with script/style removal.

### `TestExtractHtmlTitle`
Tests HTML title extraction functionality with proper text processing.

## Dependencies and Imports
- **pytest**: Testing framework for assertions and test organization
- **url2md.utils**: HTML processing utility functions being tested

## Body Content Extraction Tests

### `TestExtractBodyContent.test_basic_body_extraction()`
Tests fundamental body content extraction from well-formed HTML.
- **Purpose**: Verify basic HTML body extraction works correctly
- **Test HTML Structure**:
  ```html
  <html>
    <head><title>Test</title></head>
    <body>
      <h1>Title</h1>
      <p>Content</p>
    </body>
  </html>
  ```
- **Expected Behavior**: Body content extracted, head content excluded
- **Key Assertions**: 
  - Body elements (`<h1>`, `<p>`) present in result
  - Head elements (`<title>`) excluded from result

### `TestExtractBodyContent.test_script_and_style_removal()`
Tests removal of script and style tags from extracted content.
- **Purpose**: Verify JavaScript and CSS code filtered from content
- **Test Content**: Mixed HTML with `<script>` and `<style>` tags
- **Script Content**: `alert('test');` JavaScript code
- **Style Content**: `body { color: red; }` CSS rules
- **Expected Behavior**: Script and style content completely removed
- **Key Assertions**: 
  - HTML content elements preserved
  - JavaScript code removed
  - CSS code removed

### `TestExtractBodyContent.test_case_insensitive_tags()`
Tests case-insensitive HTML tag processing.
- **Purpose**: Verify uppercase HTML tags handled correctly
- **Test HTML**: Uppercase tags (`<BODY>`, `<SCRIPT>`, `<STYLE>`)
- **Expected Behavior**: Case-insensitive tag recognition and processing
- **Key Assertions**: 
  - Uppercase HTML content preserved
  - Uppercase script/style tags removed
  - Case insensitivity maintained throughout

### `TestExtractBodyContent.test_no_body_tag()`
Tests content processing when no `<body>` tag exists.
- **Purpose**: Verify processing works with HTML fragments
- **Test Content**: HTML without explicit body tags
- **Expected Behavior**: Process entire content, remove scripts regardless
- **Key Assertions**: 
  - Content elements preserved
  - Script content removed even without body tag

### `TestExtractBodyContent.test_nested_script_tags()`
Tests handling of script tags nested within other elements.
- **Purpose**: Verify script removal works in complex HTML structures
- **Test Structure**: Script tag nested inside div elements
- **Script Content**: Multi-line JavaScript function
- **Expected Behavior**: Nested scripts completely removed, surrounding content preserved
- **Key Assertions**: 
  - Surrounding div and paragraph content preserved
  - All JavaScript code removed regardless of nesting

### `TestExtractBodyContent.test_body_with_attributes()`
Tests body tag processing when attributes are present.
- **Purpose**: Verify body extraction works with attributed tags
- **Test HTML**: `<body class="main" id="content">`
- **Expected Behavior**: Attributes ignored, content extracted correctly
- **Key Assertions**: Body content extracted regardless of attributes

### `TestExtractBodyContent.test_body_extraction_error_handling()`
Tests error handling for invalid input.
- **Purpose**: Verify graceful handling of invalid input
- **Test Input**: `None` value (invalid input)
- **Expected Behavior**: Graceful failure, return original input
- **Key Assertion**: Original input returned on processing error

## Title Extraction Tests

### `TestExtractHtmlTitle.test_basic_title_extraction()`
Tests fundamental HTML title extraction.
- **Purpose**: Verify basic title extraction from well-formed HTML
- **Test HTML**: Standard HTML with `<title>Test Page Title</title>`
- **Expected Result**: Clean title text without HTML tags
- **Key Assertion**: Exact title text extracted correctly

### `TestExtractHtmlTitle.test_title_with_html_entities()`
Tests HTML entity decoding in titles.
- **Purpose**: Verify HTML entities properly decoded in title text
- **Test Entities**: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- **Input Title**: `Test &amp; Example &lt;Page&gt; &quot;Title&quot;`
- **Expected Output**: `Test & Example <Page> "Title"`
- **Key Assertion**: All HTML entities properly decoded

### `TestExtractHtmlTitle.test_case_insensitive_title()`
Tests case-insensitive title tag recognition.
- **Purpose**: Verify uppercase HTML tags handled correctly
- **Test HTML**: Uppercase tags (`<TITLE>`, `<HEAD>`)
- **Expected Behavior**: Case-insensitive title extraction
- **Key Assertion**: Title extracted regardless of tag case

### `TestExtractHtmlTitle.test_title_with_attributes()`
Tests title extraction when title tag has attributes.
- **Purpose**: Verify attributes don't interfere with title extraction
- **Test HTML**: `<title lang="en">Attributed Title</title>`
- **Expected Behavior**: Attributes ignored, title content extracted
- **Key Assertion**: Title content extracted correctly despite attributes

### `TestExtractHtmlTitle.test_multiline_title()`
Tests title extraction with multiline title content.
- **Purpose**: Verify whitespace preservation in multiline titles
- **Test Title**: Title content spanning multiple lines with indentation
- **Expected Behavior**: Whitespace and line breaks preserved
- **Key Assertion**: Multiline content preserved exactly as written

### `TestExtractHtmlTitle.test_no_title_tag()`
Tests behavior when no title tag exists.
- **Purpose**: Verify graceful handling of missing title
- **Test HTML**: Complete HTML without `<title>` tag
- **Expected Result**: Empty string returned
- **Key Assertion**: Empty string for missing title

### `TestExtractHtmlTitle.test_empty_title()`
Tests handling of empty title tags.
- **Purpose**: Verify empty title tags handled correctly
- **Test HTML**: `<title></title>` (empty title tag)
- **Expected Result**: Empty string returned
- **Key Assertion**: Empty string for empty title tag

### `TestExtractHtmlTitle.test_title_with_whitespace()`
Tests whitespace trimming in title extraction.
- **Purpose**: Verify leading/trailing whitespace removed
- **Test Title**: `<title>   Spaced Title   </title>`
- **Expected Result**: `"Spaced Title"` (whitespace trimmed)
- **Key Assertion**: Whitespace properly trimmed from title

### `TestExtractHtmlTitle.test_title_extraction_error_handling()`
Tests error handling for invalid title extraction input.
- **Purpose**: Verify graceful handling of invalid input
- **Test Input**: `None` value (invalid input)
- **Expected Behavior**: Empty string returned on error
- **Key Assertion**: Empty string returned for invalid input

## Testing Patterns and Approaches

### HTML Structure Testing
Tests cover various HTML document structures:
- Well-formed complete documents
- HTML fragments without complete structure
- Nested element hierarchies
- Mixed case tag variations

### Content Filtering Testing
Tests verify selective content processing:
- Script tag content completely removed
- Style tag content completely removed
- Regular HTML content preserved
- Nested structure handling

### Error Resilience Testing
Tests verify robust error handling:
- Invalid input types (None, non-string)
- Malformed HTML structures
- Missing expected elements
- Graceful degradation strategies

### Edge Case Coverage
Tests handle various edge cases:
- Empty content
- Whitespace-only content
- Special characters and entities
- Unicode content support

## Key Implementation Details

### Content Extraction Algorithm
Tests verify sophisticated HTML processing:
- **Body Extraction**: Find and extract content within body tags
- **Script Removal**: Remove all script tags and content
- **Style Removal**: Remove all style tags and content
- **Case Insensitivity**: Handle mixed-case HTML tags

### Title Processing Algorithm
Tests verify robust title extraction:
- **Title Location**: Find title tags within HTML
- **Entity Decoding**: Convert HTML entities to text
- **Whitespace Handling**: Trim leading/trailing whitespace
- **Case Insensitivity**: Handle uppercase/lowercase tags

### Regular Expression Usage
Tests verify proper regex application:
- Case-insensitive pattern matching
- Non-greedy matching for nested content
- Proper escaping of special characters
- Multi-line content handling

### Error Handling Strategy
Tests verify graceful error management:
- **Fallback Behavior**: Return original input on parsing errors
- **Default Values**: Return appropriate defaults (empty string for titles)
- **Type Safety**: Handle unexpected input types gracefully

## HTML Processing Edge Cases

### Malformed HTML Handling
Tests verify processing works with real-world HTML:
- Missing closing tags
- Improperly nested elements
- Mixed quote styles in attributes
- Non-standard HTML structures

### Content Preservation
Tests ensure important content preserved:
- Text content within elements
- HTML structure for semantic meaning
- Special characters and Unicode
- Formatting elements (headers, paragraphs)

### Security Considerations
Tests verify potentially dangerous content removed:
- JavaScript code completely filtered
- CSS rules removed to prevent styling interference
- Only safe HTML content passed through

## Testing Strategy

The HTML utils test suite employs a **comprehensive HTML processing validation** approach:

### Algorithm Testing
- Individual processing step verification
- Edge case boundary testing
- Performance characteristic validation

### Content Safety Testing
- Malicious content filtering verification
- Script injection prevention
- Style interference prevention

### Compatibility Testing
- Real-world HTML structure handling
- Cross-browser HTML variation support
- Legacy HTML format processing

### Error Resilience Testing
- Invalid input handling verification
- Graceful degradation confirmation
- Robust fallback behavior validation

This thorough testing ensures the HTML utility functions provide reliable, secure content processing that works with real-world web content while maintaining safety and performance standards essential for url2md's content analysis capabilities.