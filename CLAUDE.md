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


## Development Environment

**IMPORTANT**: Always use `uv run` for executing Python scripts and commands. Dependencies are managed in `pyproject.toml` using the **llm7shi** package for Gemini API integration. See [README.md](README.md) for installation and environment variable details.

## Command Architecture

url2md follows a **centralized command architecture**: all CLI logic in `main.py`, business logic in function modules. See [NOTES.md](NOTES.md#architecture-decision-centralized-vs-distributed) for rationale.

## Development Workflows

### Adding New Features
1. Identify which module needs modification
2. Update relevant data models if needed
3. Add/modify command logic
4. Update schema modules if AI operations are involved
5. Add tests for new functionality
6. Update module documentation if implementation changes
7. Update README.md if user-facing changes

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
Update schemas in `schema.py`, modify prompts in command modules, use `llm7shi` package functions, test with actual API calls.

#### Language Support and Translation
Pydantic schemas with dynamic language support, TSV-based translation caching with cache-first approach and English fallback.

#### Cache Management Changes
Ensure backward compatibility with existing cache files when modifying data models.

#### Configuration Changes
When modifying configurable values: define constants in appropriate modules, update all references, documentation, tests, and verify consistency across examples and help text.

## Testing

### Test Execution Workflow
Before making changes: run `uv run pytest`, fix any failures, then run tests again after changes.

### Key Guidelines
- Use descriptive test names, test positive/negative cases
- Use `pytest.raises(SystemExit)` for `sys.exit(1)` cases
- Follow existing test patterns, separate translation functionality tests

See [tests/README.md](tests/README.md) for comprehensive testing guidelines, test suite documentation, and coverage overview.

## Debugging and Troubleshooting

See [docs/20250615-troubleshooting.md](docs/20250615-troubleshooting.md) for comprehensive troubleshooting guide including common issues and debugging tips.

## Code Style and Conventions

- Define configurable values as constants, avoid hardcoding
- Standard library → third-party → project imports
- All code in English, snake_case/PascalCase naming
- Functions need docstrings and type hints

## Error Handling

**Core Policy**: Exception-based with natural propagation for debugging visibility. Fail fast for user input errors, graceful degradation only for optional operations. See [docs/20250614-error-handling.md](docs/20250614-error-handling.md) and [NOTES.md](NOTES.md#error-handling-philosophy).

## Future Development

The centralized architecture supports extension through new subcommands (function module + CLI integration), AI operations (new schemas), output formats, and content types. Maintain centralized CLI patterns while keeping business logic in separate function modules.

## Documentation Structure

The project maintains comprehensive documentation across multiple levels following **implementation rationale over implementation details** - see [DOCUMENTATION.md](DOCUMENTATION.md) for complete guidelines.

**Module Documentation**: Each Python module has a corresponding `.md` file (e.g., `module.py` → `module.md`, `test_feature.py` → `test_feature.md`) that explains implementation rationale and design decisions rather than code details.

- **README.md** - User documentation
- **url2md/README.md** - Package architecture
- **tests/README.md** - Test suite documentation
- **NOTES.md** - Development philosophy
- **docs/** - Specialized documentation (YYYYMMDD-filename.md format)

### Documentation Maintenance
Update corresponding `.md` files when making module, test, architecture, user-facing, or development process changes.

## Development Philosophy

This project evolved through iterative refinement, resembling a "diffusion model" - starting from noisy prototypes and systematically removing complexity while enhancing clarity. See [NOTES.md](NOTES.md) for detailed lessons learned and development philosophy.
