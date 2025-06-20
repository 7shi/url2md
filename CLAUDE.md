# CLAUDE.md

This file provides guidelines for Claude Code (claude.ai/code) when working with the url2md package.

## Communication Guidelines

**Conversation Language**: While the assistant may converse with users in their preferred language, all code and documentation should be written in English unless specifically instructed otherwise.

### Git Commit Messages
- Use clear, concise commit messages in English
- Do not include promotional text or AI-generated signatures

### CHANGELOG Guidelines
- Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
- Keep entries concise and user-focused
- Use **bold** for feature names, avoid technical implementation details
- Focus on user-visible changes and benefits
- Group changes under Added/Changed/Fixed sections as appropriate

## Project Overview

url2md is a command-line tool for URL analysis and classification that generates Markdown reports through AI-powered content analysis, summarization, and classification.

**Key Features:**
- URL fetching with dynamic rendering support (Playwright)
- AI-powered content summarization using Gemini API with multi-language support
- LLM-based tag classification and theme analysis with thinking process visualization
- AI reasoning insights through Gemini 2.5's thinking capabilities
- Multi-language report generation with automatic translation of UI terms
- Complete pipeline processing with subsection ordering by URL tag priority

## Package Structure

```
url2md/
├── pyproject.toml          # Package configuration (CC0 license, Python 3.10+)
├── README.md               # User documentation and command reference
├── CLAUDE.md              # This file - development guidelines
├── CHANGELOG.md            # Version history following Keep a Changelog format
├── NOTES.md                # Development philosophy and lessons learned
├── docs/                  # Additional documentation
│   ├── resource-support.md # Resource handling documentation
│   └── translation-strategy.md # Translation implementation details
├── tests/                 # Test directory with comprehensive test suite
│   ├── test_report.py          # Core report functionality tests
│   ├── test_report_translations.py # Report translation functionality tests
│   └── ...
└── url2md/               # Main package
    ├── __init__.py       # Package entry point
    ├── main.py           # CLI entry point and subcommand dispatcher
    ├── urlinfo.py        # Data models (URLInfo, load_urls_from_file)
    ├── cache.py          # Cache management (Cache, CacheResult)
    ├── tsv_manager.py    # Base class for TSV file operations
    ├── translation_cache.py # Translation caching system
    ├── translate.py      # Generic translation functions
    ├── fetch.py          # URL fetching functions
    ├── summarize.py      # AI summarization functions
    ├── classify.py       # Tag classification functions
    ├── report.py         # Report generation functions
    ├── utils.py          # HTML processing and resource utilities
    ├── download.py       # Playwright dynamic rendering
    └── schemas/          # JSON schemas for AI operations
        ├── summarize.json# Schema for summarize command
        ├── classify.json # Schema for classify command
        └── translate.json# Schema for report term translation
```

## Development Environment

### Python Execution
**IMPORTANT**: Always use `uv run` for executing Python scripts and commands. See [README.md](README.md) for complete command examples.

### Dependencies
Dependencies are managed in `pyproject.toml`. The project uses the **llm7shi** package for Gemini API integration and terminal formatting utilities. See [README.md](README.md#installation) for dependency details and [README.md](README.md#environment-variables) for required environment variables.

## Command Architecture

url2md follows a **centralized command architecture** with function modules:

```bash
uv run url2md [global-options] <subcommand> [options]
```

**Core Design Pattern:**
- **Single Entry Point**: `url2md/main.py` serves as the central command orchestrator
- **Function Modules**: Each subcommand is implemented as a pure function module (no standalone execution)
- **Clean Separation**: CLI logic centralized, business logic distributed

**Command Flow:**
1. **Argument Parsing**: All done in `main.py` using subparsers
2. **Command Routing**: `run_subcommand()` dispatches to appropriate `run_*()` function
3. **Function Import**: Each `run_*()` function imports only what it needs locally
4. **Error Handling**: Exception-based with natural propagation for debugging

**Centralized Benefits:** Eliminates code duplication, improves maintainability, and enables consistent error handling. See [NOTES.md](NOTES.md#architecture-decision-centralized-vs-distributed) for detailed rationale.

## Development Workflows

### Adding New Features
1. Identify which module needs modification
2. Update relevant data models if needed
3. Add/modify command logic
4. Update JSON schemas if AI operations are involved
5. Add tests for new functionality
6. Update README.md if user-facing changes

### Development Best Practices
- **Start Simple, Evolve Gradually**: Begin with functional prototypes rather than perfect designs
- **Centralize What Should Be Central**: Identify system-wide concerns (like CLI parsing, global options) and centralize them
- **Test-Driven Stabilization**: Comprehensive tests enable confident refactoring
- **Consistency Over Optimization**: Favor consistency over minor optimizations
- **Document Reasoning**: Document the reasoning behind non-obvious choices
- **Fail Fast Philosophy**: Prefer natural exception propagation over complex fallback mechanisms
- **Resource Access**: Use `get_resource_path()` for consistent package resource access

### Common Development Tasks

#### Adding a New Subcommand

Use the **two-phase development approach**: start with standalone module for prototyping, then integrate into centralized architecture. See [NOTES.md](NOTES.md#development-methodology-two-phase-subcommand-development) for detailed methodology and benefits.

#### Modifying AI Operations
1. Update relevant JSON schema in `url2md/schemas/`
2. Modify prompt generation in the command module
3. Import Gemini functions from `llm7shi` package: `from llm7shi import generate_content_retry, config_from_schema`
4. Configure thinking parameters in `generate_content_retry()` calls if needed
5. Use `get_resource_path()` for schema file access in tests and code
6. For language-specific operations, use `{ in language}` placeholder in schema descriptions
7. Test with actual API calls
8. Verify structured output format and thinking process display

#### Language Support and Schema Placeholders
- Use `{ in language}` placeholder in JSON schema descriptions for language-specific fields
- Schemas automatically replace placeholders: if language specified → ` in {language}`, if not → empty string
- Use `config_from_schema_string()` for dynamic schema modification with placeholders
- Generic translation module (`translate.py`): `translate_terms()` for any term list, `create_translation_schema()` and `create_translation_prompt()` for dynamic generation

#### Report Translation Implementation
- **Translation Cache System**: Uses TSV-based caching (`cache/terms.tsv`) to store translations persistently
- **Cache-First Approach**: Check cache before calling LLM for efficiency
- **Automatic Integration**: Classification commands with language option automatically handle translation cache
- **Report Usage**: Report generation reads translations from cache via language field in classification data
- **Translation terms**: "Summary", "Themes", "Total URLs", "Classified", "Unclassified", "URLs", "Other"
- **Architecture**: TSVManager base class provides common file operations, TranslationCache inherits for specialized functionality
- **Generic Translation**: `translate.py` module provides reusable translation functions for any terms
- **Fallback mechanism**: Uses English terms when translations are missing from cache
- **Testing**: Test translation functionality in `test_report_translations.py` with complete and partial translation scenarios

#### Cache Management Changes
1. Modify `cache.py` for data model changes
2. Update `urlinfo.py` for URLInfo changes
3. Ensure backward compatibility with existing cache files

#### Configuration Changes
When modifying configurable values: define constants in appropriate modules, update all references, documentation, tests, and verify consistency across examples and help text.

## Testing

### Test Execution Workflow
Before making changes: run `uv run pytest`, fix any failures, then run tests again after changes.

### Key Guidelines
- Use descriptive test names and test both positive/negative cases
- Use `pytest.raises(SystemExit)` for `sys.exit(1)` cases
- Use `get_resource_path()` for accessing schema files in tests
- Follow existing test patterns in the test suite
- For report generation tests, include tests for subsection URL tag ordering priority
- Translation functionality tests should be in separate test files (e.g., `test_report_translations.py`)
- Test both complete translations and partial translations (fallback scenarios)

See [docs/testing.md](docs/testing.md) for comprehensive testing guidelines and [README.md](README.md#testing) for basic commands.

## Debugging and Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for comprehensive troubleshooting guide including common issues and debugging tips.

## Code Style and Conventions

### Constants and Configuration
Define configurable values as constants in appropriate modules, avoid hardcoding strings, and reference constants from a single source.

### Import Organization
- Standard library imports first, third-party second, project imports last
- Use local imports for specialized modules within functions
- Avoid redundant imports

### Language and Style
- All code, comments, and docstrings in English
- Use snake_case for functions/variables, PascalCase for classes
- All functions should have docstrings and type hints

## Error Handling

**Core Policy**: Prioritize error visibility in development phase (0.1.0)

- **Exception-based**: All `run_*()` functions use exceptions, let errors propagate for full stack traces
- **Localized try-catch**: Handle exceptions close to their source, avoid broad safety nets
- **Fail fast**: User input files → `sys.exit(1)`, critical system data → `sys.exit(1)`
- **Graceful degradation**: Only for optional operations (cache detection, HTML parsing)

See [docs/error-handling.md](docs/error-handling.md) for detailed guidelines and [NOTES.md](NOTES.md#error-handling-philosophy) for philosophical background.

## Future Development

The centralized architecture supports extension through new subcommands (function module + CLI integration), AI operations (new schemas), output formats, and content types. Maintain centralized CLI patterns while keeping business logic in separate function modules.

## Development Philosophy

This project evolved through iterative refinement, resembling a "diffusion model" - starting from noisy prototypes and systematically removing complexity while enhancing clarity. See [NOTES.md](NOTES.md) for detailed lessons learned and development philosophy.