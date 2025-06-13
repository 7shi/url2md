# CLAUDE.md

This file provides guidelines for Claude Code (claude.ai/code) when working with the url2md package.

## Communication Guidelines

**Conversation Language**: While the assistant may converse with users in their preferred language, all code and documentation should be written in English unless specifically instructed otherwise.

### Git Commit Messages
- Use clear, concise commit messages in English
- Do not include promotional text or AI-generated signatures

## Project Overview

url2md is a command-line tool for URL analysis and classification that generates Markdown reports through AI-powered content analysis, summarization, and classification.

**Key Features:**
- URL fetching with dynamic rendering support (Playwright)
- AI-powered content summarization using Gemini API
- LLM-based tag classification and theme analysis
- Markdown report generation
- Complete pipeline processing

## Package Structure

```
url2md/
├── pyproject.toml          # Package configuration (CC0 license, Python 3.10+)
├── README.md               # User documentation
├── CLAUDE.md              # This file - development guidelines
├── NOTES.md                # Development philosophy and lessons learned
├── schemas/               # JSON schemas for AI operations
│   ├── summarize.json     # Schema for summarize command
│   └── classify.json      # Schema for classify command
├── tests/                 # Test directory with comprehensive test suite
└── url2md/               # Main package
    ├── __init__.py       # Package entry point
    ├── main.py           # CLI entry point and subcommand dispatcher
    ├── models.py         # Data models (URLInfo, load_urls_from_file)
    ├── cache.py          # Cache management (Cache, CacheResult)
    ├── fetch.py          # URL fetching functions
    ├── summarize.py      # AI summarization functions
    ├── classify.py       # Tag classification functions
    ├── report.py         # Report generation functions
    ├── gemini.py         # Gemini API integration
    ├── utils.py          # HTML processing utilities
    └── download.py       # Playwright dynamic rendering
```

## Development Environment

### Python Execution
**IMPORTANT**: Always use `uv run` for executing Python scripts and commands:

```bash
# Correct way to run url2md
uv run url2md --help
uv run url2md fetch "https://example.com"
uv run url2md fetch -u urls.txt
uv run url2md summarize -u urls.txt -l Japanese
uv run url2md classify -u urls.txt -o classification.json -l Japanese
uv run url2md --cache-dir /custom/cache fetch -u urls.txt

# Avoid direct Python execution
python -m url2md        # ❌ Don't use this
python url2md/main.py   # ❌ Don't use this
```

### Dependencies
Dependencies are managed in `pyproject.toml`. Key dependencies include:
- **google-genai>=1.19.0**: Gemini API integration
- **requests>=2.31.0**: HTTP client
- **playwright>=1.52.0**: Dynamic rendering (optional)
- **tqdm>=4.67.1**: Progress bars
- **minify-html>=0.16.4**: HTML minification
- **pillow>=10.0.0**: Image processing (GIF→PNG conversion)

### Development Dependencies
Test and development dependencies:
- **pytest>=8.3.0**: Testing framework
- **pytest-cov**: Coverage reporting
- **tempfile**: For filesystem testing (built-in)
- **unittest.mock**: Mocking framework (built-in)

### Environment Variables
See [README.md](README.md#environment-variables) for required environment variables.

## Command Architecture

url2md follows a **centralized command architecture** with function modules:

```bash
uv run url2md [global-options] <subcommand> [options]
```

**Global Options:**
- `--cache-dir PATH`: Cache directory (default: cache/)
- `--debug`: Enable debug mode with full stack traces
- `--version`: Show version information
- `--help`: Show help message

### Implementation Strategy

**Core Design Pattern:**
- **Single Entry Point**: `url2md/main.py` serves as the central command orchestrator
- **Function Modules**: Each subcommand is implemented as a pure function module (no standalone execution)
- **Clean Separation**: CLI logic centralized, business logic distributed

**Centralized Benefits:** Eliminates code duplication, improves maintainability, and enables consistent error handling. See [NOTES.md](NOTES.md#architecture-decision-centralized-vs-distributed) for detailed rationale.

**Command Flow:**
1. **Argument Parsing**: All done in `main.py` using subparsers
2. **Command Routing**: `run_subcommand()` dispatches to appropriate `run_*()` function
3. **Function Import**: Each `run_*()` function imports only what it needs locally
4. **Error Handling**: Exception-based, with try-catch only in `main()`
5. **Debug Support**: `--debug` flag bypasses exception handling for full tracebacks

### Available Subcommands

**Unified Command Interface:**
- **Positional arguments**: URL enumeration (`urls` nargs='*')
- **URL file input**: `-u/--urls-file` for URL list files
- **Output files**: `-o/--output` for result files
- **Classification input**: `-c/--class` for classification JSON files

1. **fetch**: Download and cache URLs
   - Implementation: `url2md/fetch.py` (functions), `url2md/main.py` (CLI integration)
   - Purpose: Download web content, handle caching, support Playwright
   - **Default Behavior**: Skip failed URLs (use `-r/--retry` to retry errors)
   
2. **summarize**: Generate AI summaries
   - Implementation: `url2md/summarize.py` (functions), `url2md/main.py` (CLI integration)
   - Purpose: Create structured summaries using Gemini API
   - Schema: `schemas/summarize.json`
   - **Language Support**: Use `-l/--language` to specify output language (e.g., Japanese, Chinese, French)
   
3. **classify**: Classify content by topic
   - Implementation: `url2md/classify.py` (functions), `url2md/main.py` (CLI integration)
   - Purpose: Extract tags and classify by theme using LLM (default action)
   - Schema: `schemas/classify.json`
   - **Default Behavior**: Classification runs automatically unless `--extract-tags` or `--show-prompt` specified
   - **Language Support**: Use `-l/--language` to specify output language for theme names and descriptions
   
4. **report**: Generate Markdown reports
   - Implementation: `url2md/report.py` (functions), `url2md/main.py` (CLI integration)
   - Purpose: Create comprehensive Markdown reports from classification data
   
5. **workflow**: Complete workflow
   - Implementation: `url2md/main.py` (run_workflow function)
   - Purpose: Execute entire workflow (fetch → summarize → classify → report)
   - **Language Support**: Use `-l/--language` to specify output language for summarize and classify steps

## Data Flow

The standard workflow follows this pattern:

```
URLs → fetch → summarize → classify → report → Markdown Report
```

### Data Storage

- **Cache Directory**: `cache/` (configurable with `--cache-dir`)
  - `cache.tsv`: Metadata index with URL info
  - `content/`: Downloaded files (HTML, PDF, images, etc.)
  - `summary/`: AI-generated summaries as JSON files
  
- **Intermediate Files**:
  - `classification.json`: LLM classification results
  - `report.md`: Final Markdown report

### Data Models

- **URLInfo**: Core data model for cached URLs (in `models.py`)
- **Cache**: Cache management class (in `cache.py`)
- **CacheResult**: Result object for cache operations

## Testing Guidelines

### Running Tests
See [README.md](README.md#testing) for basic testing commands. For comprehensive testing guidelines, see [NOTES.md](NOTES.md#testing-philosophy-and-practices).

### Test Structure
Tests should be placed in the `tests/` directory and follow the naming convention `test_*.py`.

**Test Categories:**
- Unit tests for individual modules
- Integration tests for command workflows
- End-to-end tests for complete pipeline

### Test Files Overview

The test suite includes the following files:

1. **test_cache.py** - Cache management functionality tests
   - Cache initialization and data operations
   - TSV format validation and persistence
   - Filename collision handling and domain throttling
   - CacheResult object testing

2. **test_integration.py** - Integration and end-to-end tests
   - Command-line interface integration
   - Module import and dependency testing
   - Complete workflow integration
   - Schema file accessibility verification

3. **test_models.py** - Data model tests
   - URLInfo creation, serialization, and validation
   - TSV format handling and error escaping
   - URL loading from files and stdin
   - Content fetching with error handling

4. **test_report.py** - Report generation tests
   - Tag matching weight calculations
   - URL classification algorithms
   - Markdown report formatting
   - Theme analysis and statistics

5. **test_schema_structure.py** - Schema and code structure validation
   - JSON schema validation for AI operations
   - Package structure verification
   - Import path consistency checks
   - Schema-code alignment validation

6. **test_summarize.py** - AI summarization tests
   - Schema validation and structure testing
   - Prompt generation functionality
   - File operations and JSON handling
   - Mock-based content summarization testing

7. **test_utils.py** - HTML processing utility tests
   - HTML content extraction and cleaning
   - Title extraction and text processing
   - Minification and content validation
   - Edge case handling for malformed HTML

### Mock Considerations
When testing:
- Mock external API calls (Gemini API) using `unittest.mock`
- Mock file system operations when appropriate with `tempfile`
- Mock Playwright for browser automation tests
- Use `patch` decorators for dependency injection
- Test both success and error scenarios

## Development Workflows

### Adding New Features
1. Identify which module needs modification
2. Update relevant data models if needed
3. Add/modify command logic
4. Update JSON schemas if AI operations are involved
5. Add tests for new functionality
6. Update README.md if user-facing changes

### Common Development Tasks

#### Adding a New Subcommand

Use the **two-phase development approach**: start with a standalone module for prototyping, then integrate into the centralized architecture once stable. This methodology reduces risk and enables rapid iteration.

For detailed methodology and rationale, see [NOTES.md](NOTES.md#development-methodology-two-phase-subcommand-development).

#### Modifying AI Operations
1. Update relevant JSON schema in `schemas/`
2. Modify prompt generation in the command module
3. Test with actual API calls
4. Verify structured output format

#### Cache Management Changes
1. Modify `cache.py` for data model changes
2. Update `models.py` for URLInfo changes
3. Ensure backward compatibility with existing cache files

## Debugging and Troubleshooting

### Common Issues

1. **Import Errors**: Ensure using `uv run` instead of direct Python execution
2. **Missing Dependencies**: Check `pyproject.toml` and run `uv sync`
3. **API Errors**: Verify `GEMINI_API_KEY` environment variable
4. **Playwright Issues**: Run `uv run playwright install` for browser support
5. **Test Failures**: Run `uv run pytest -v` to see detailed test output and error messages

### Test Development

Follow the comprehensive testing guidelines and workflow detailed in [NOTES.md](NOTES.md#testing-philosophy-and-practices).

### Logging and Debugging
- Use `print()` statements for user-facing progress information
- Commands include progress bars using `tqdm`
- Error messages should be clear and actionable
- Use `--debug` flag for full stack traces during development: `uv run url2md --debug <command>`

### Performance Considerations
- Cache management prevents redundant downloads
- Domain-based throttling prevents rate limiting
- Progress bars provide user feedback for long operations

## Code Style and Conventions

### Language
- All code, comments, and docstrings are in English
- Function and variable names use snake_case
- Class names use PascalCase
- JSON schema files must use English descriptions only
- Avoid language-specific instructions in schema descriptions

### Documentation
- All functions should have docstrings
- Type hints are used throughout
- README.md provides user documentation
- This CLAUDE.md provides development documentation

### Error Handling
- **Exception-based**: All `run_*()` functions use exceptions instead of return values
- **Single Catch Point**: Only `main()` has try-except blocks
- **Meaningful Messages**: ValueError for user errors, generic Exception for system errors
- **Debug Mode**: `--debug` flag shows full stack traces for development
- Graceful degradation when possible (e.g., fallback from Playwright to requests)

## License and Distribution

See [README.md](README.md#license) for license information.

- **Package Name**: url2md
- **Entry Point**: `url2md = "url2md.main:main"` in pyproject.toml

This package is designed to be independent and redistributable without dependencies on the original Skype analysis project.

## Future Development

The centralized architecture is designed to be extensible:
- **New subcommands**: Add function module + CLI integration in main.py
- **AI operations**: Extend with new schemas and prompt generation
- **Output formats**: Expand beyond Markdown with new format modules
- **Content types**: Support additional types through fetch/utils modules
- **Import optimization**: Standard modules global, project modules local
- **Error handling**: Maintain exception-based pattern for consistency

When making changes, maintain the centralized CLI pattern while keeping business logic in separate function modules for maintainability.

## Development Philosophy

This project evolved through an iterative refinement process, gradually moving from unclear requirements to a clean, coherent design. The development approach resembles a "diffusion model" - starting from noisy prototypes and systematically removing complexity while enhancing clarity.

For detailed lessons learned and development philosophy, see [NOTES.md](NOTES.md).
