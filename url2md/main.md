# main.py

## Overview

This is the main entry point and command-line interface (CLI) orchestrator for the url2md package. It implements a centralized command architecture where all subcommands are routed through a single entry point, following the design philosophy outlined in CLAUDE.md.

## Key Components

### Command-Line Parser (`create_parser()`)

Creates the main argument parser with:
- **Global options**: `--version`, `--cache-dir`
- **Subcommands**: init, fetch, summarize, classify, report, workflow
- Each subcommand has its own set of options and arguments
- Provides comprehensive help text with examples

### Subcommand Dispatcher (`run_subcommand()`)

Routes commands to their respective handler functions:
- `init` → `run_init()`
- `fetch` → `run_fetch()`
- `summarize` → `run_summarize()`
- `classify` → `run_classify()`
- `report` → `run_report()`
- `workflow` → `run_workflow()`

### Subcommand Handlers

#### `run_init(args)`
- Initializes a new cache directory structure
- Creates subdirectories: `content/`, `summary/`
- Initializes empty `cache.tsv` file
- Validates that cache doesn't already exist

#### `run_fetch(args)`
- Collects URLs from command line and/or file
- Removes duplicates while preserving order
- Delegates to `fetch.fetch_urls()` for actual fetching
- Supports Playwright for dynamic rendering

#### `run_summarize(args)`
- Filters URLs based on arguments (specific URLs, hash, or all)
- Handles `--show-summary` option to display existing summaries
- Requires `GEMINI_API_KEY` environment variable
- Delegates to `summarize.summarize_urls()` for AI summarization

#### `run_classify(args)`
- Extracts tags from summaries
- Three modes:
  - `--extract-tags`: Display tag statistics only
  - `--show-prompt`: Show LLM prompt without calling API
  - Default: Perform full classification with LLM
- Handles translation prompts when language is specified
- Saves classification results to JSON file

#### `run_report(args)`
- Loads classification data from JSON file
- Parses theme weights and subsection specifications
- Supports both command-line and file-based theme weight configuration
- Classifies URLs based on themes
- Generates Markdown report (HTML format planned)
- Outputs to file or stdout

#### `run_workflow(args)`
- Executes complete pipeline: fetch → summarize → classify → report
- Skips classification if output file already exists
- Provides progress indicators with emoji icons
- Aggregates all workflow steps with appropriate parameters

### Main Entry Point (`main()`)

- Parses command-line arguments
- Auto-detects cache directory if not specified (except for init)
- Executes requested subcommand
- Returns appropriate exit codes
- Follows fail-fast philosophy for error handling

## Design Patterns

### Centralized Architecture
- Single entry point for all commands
- Consistent argument parsing and validation
- Unified error handling approach
- Eliminates code duplication across commands

### Namespace Objects
- Uses `argparse.Namespace` to pass arguments between functions
- Enables workflow command to call other handlers programmatically

### Local Imports
- Each handler function imports only what it needs
- Reduces startup time and circular dependency risks

### Error Handling
- Exception-based with natural propagation
- Full stack traces for debugging
- User-friendly error messages for common issues

## Configuration

### Cache Directory
- Auto-detected from parent directories if not specified
- Can be explicitly set with `--cache-dir`
- Required for all commands except `init`

### Environment Variables
- `GEMINI_API_KEY`: Required for AI operations (summarize, classify)

### Theme Weights
- Command-line: `-t "Theme Name:1.5"` or `-t "Theme Name:1.5$"` (with subsections)
- File-based: `-T weights.txt` with one weight per line
- Command-line weights override file settings

## Workflow Integration

The workflow command demonstrates the power of centralized architecture by:
- Reusing existing handler functions
- Maintaining consistent behavior across individual and batch operations
- Providing a seamless end-to-end experience

This design makes the codebase maintainable, testable, and extensible while providing a clean user interface.