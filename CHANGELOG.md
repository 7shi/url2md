# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-06-15

### Added
- **Tag Subsections**: Added `$` suffix to `-t` option to enable tag-based subsections within themes for better content organization
- **Theme Weight Files**: Added `-T` option to load theme weights from a file, supporting mixing with command-line specifications
- **Enhanced Summarization**: Added `--show-summary` option to summarize command for displaying AI-generated summaries without full reports

### Changed
- **Report Structure**: Improved report layout by removing top-level "URL Analysis Report" heading and restructuring sections
- **Subsection Display**: Added "(subsection)" marker in classification results output when subsections are enabled

## [0.1.0] - 2025-06-14

### Added
- Core URL fetching with dynamic rendering support (Playwright)
- AI-powered content summarization using Gemini API
- LLM-based tag classification and theme analysis with thinking process visualization
- AI reasoning insights through Gemini 2.5's thinking capabilities
- Markdown report generation
- Complete pipeline processing
- Comprehensive test suite
- Command-line interface with multiple subcommands including init
- Caching system for improved performance
- HTML processing and resource utilities
- Terminal formatting utilities for Markdown display
- Package resource support with JSON schemas
- Centralized command architecture with function modules
- Exception-based error handling with fail-fast philosophy