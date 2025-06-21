# summarize.py

## Overview

The `summarize.py` module provides AI-powered content summarization using the Gemini API. It reads cached content files, generates structured JSON summaries including titles, descriptions, and tags, and saves them for later classification and report generation. The module supports multiple content types and languages.

## Functions

### `generate_summary_prompt(url: str, content_type: str, language: str = None) -> str`

Generates the prompt for content summarization.

**Parameters:**
- `url`: URL of the content
- `content_type`: MIME type of the content
- `language`: Optional target language for output

**Returns:**
- Formatted prompt string with requirements

**Prompt Structure:**
- Requests structured JSON output
- Specifies required fields (title, summaries, tags, validity)
- Includes language directive if specified

### `summarize_content(cache: Cache, url_info: URLInfo, model: str, language: str = None) -> Tuple[bool, Dict[str, Any], Optional[str]]`

Generates structured JSON summary for a single file using Gemini.

**Parameters:**
- `cache`: Cache instance for file access
- `url_info`: URLInfo object with metadata
- `model`: Gemini model to use
- `language`: Optional output language

**Returns:**
- Tuple of (success: bool, summary_data: dict, error: Optional[str])

**Content Processing:**
- Text files: Preprocessed and sent as text
- HTML: Title extracted, body content cleaned
- Images: Uploaded or converted (GIF→PNG)
- Other binaries: Uploaded to Gemini

### `filter_url_infos_by_urls(cache: Cache, target_urls: List[str]) -> List[URLInfo]`

Filters URLInfo objects by a target URL list.

**Parameters:**
- `cache`: Cache instance
- `target_urls`: List of URLs to filter by

**Returns:**
- Filtered list of URLInfo objects

### `filter_url_infos_by_hash(cache: Cache, target_hash: str) -> List[URLInfo]`

Filters URLInfo objects by specific hash value.

**Parameters:**
- `cache`: Cache instance
- `target_hash`: Hash to filter by

**Returns:**
- List of URLInfo objects with matching hash

### `summarize_urls(url_infos: List[URLInfo], cache: Cache, force: bool = False, limit: Optional[int] = None, model: str = None, language: str = None) -> None`

Batch summarization of multiple URLs with progress tracking.

**Parameters:**
- `url_infos`: List of URLInfo objects to summarize
- `cache`: Cache instance
- `force`: Force re-summarization of existing summaries
- `limit`: Maximum number to process
- `model`: Gemini model to use
- `language`: Output language for summaries

**Process:**
1. Filters for valid cached content
2. Checks existing summaries (skip if not forced)
3. Applies limit if specified
4. Shows progress bar during processing
5. Saves summaries as JSON files
6. Displays final statistics

### `show_summary_files(cache: Cache, url_infos: List[URLInfo]) -> None`

Displays summary file paths and contents for specified URLs.

**Parameters:**
- `cache`: Cache instance
- `url_infos`: List of URLInfo objects to display

**Output Format:**
- Shows URL and summary file path
- Displays formatted content fields
- Truncates long detailed summaries
- Lists tags with count

## Key Design Patterns Used

1. **Schema-Driven Design**: Uses JSON schema for structured output
2. **Content Type Handling**: Different processing for text/binary/images
3. **Progress Tracking**: Visual feedback with tqdm
4. **Graceful Degradation**: Continues on individual failures

## Dependencies

### Internal Dependencies
- `.cache`: Cache class for file management
- `.urlinfo`: URLInfo for metadata
- `.utils`: HTML processing utilities
- `.schema`: Pydantic-based schema generation

### External Dependencies
- `json`: JSON parsing and generation
- `minify_html`: HTML minification
- `tqdm`: Progress bar display
- `llm7shi`: Gemini API integration
- `PIL` (Pillow): For GIF to PNG conversion
- `google.genai.types`: For image data handling

## Important Implementation Details

1. **HTML Processing**:
   - Extracts title tag content
   - Minifies HTML before processing
   - Removes script and style tags
   - Preserves title in output as list

2. **Character Limits**:
   - Text content limited to 300,000 characters
   - Truncates if exceeds limit
   - Shows character count in output

3. **Image Handling**:
   - GIF files converted to PNG in memory
   - Uses Part.from_bytes for converted images
   - Other images uploaded via file upload API

4. **File Upload Management**:
   - Uploads binary files to Gemini
   - Cleans up uploaded files after use
   - Handles cleanup failures gracefully

5. **Pydantic-Based Schema**:
   - Uses `create_summarize_schema_class()` function
   - Dynamic language support via function parameters
   - Type-safe Pydantic class generation with full IDE support

6. **Summary Storage**:
   - Saves as JSON in cache/summary/
   - Filename based on content file stem
   - Creates directory if needed

7. **Error Categories**:
   - JSON parsing errors
   - Summary generation errors
   - File access errors
   - Each handled with appropriate messages

8. **Validation**:
   - Skips URLs without successful fetch status
   - Verifies content file existence
   - Checks for valid_content flag in output