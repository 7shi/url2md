# Documentation Overview

This directory contains specialized documentation for different aspects of the url2md project. Each document serves a specific purpose in the development and maintenance workflow.

## User-Oriented Documentation

### [20250615-troubleshooting.md](20250615-troubleshooting.md)
**Common issues and debugging guidance**

Practical solutions for typical problems encountered when using url2md, including:
- Cache initialization issues
- Dependency and installation problems
- API configuration errors
- Browser support for dynamic rendering
- Development workflow debugging tips

**When to use**: First stop for resolving errors or unexpected behavior.

## Development Documentation

### [architecture.md](architecture.md)
**Architectural decisions and development methodology**

Comprehensive guide to the technical architecture and development approaches:
- Two-phase subcommand development methodology
- Centralized vs distributed architecture decisions
- Command architecture patterns and design principles
- Testing philosophy and safety net approach
- Future extensibility considerations

**When to use**: Before adding new features, understanding system design, or making architectural changes.

### [development-history.md](development-history.md)
**Historical examples and detailed lessons learned**

Concrete examples and detailed analysis of the evolution process:
- Specific UI/UX problems and solutions from real development
- Historical technical debt examples with before/after code
- Error handling philosophy evolution with practical examples
- The "Cache Class Refactoring Crisis" and other major lessons
- Detailed analysis of anti-patterns and their solutions

**When to use**: Understanding why certain decisions were made, learning from past mistakes, or seeing detailed examples of development challenges.

### [20250615-testing.md](20250615-testing.md)
**Testing guidelines and best practices**

Comprehensive testing approach and practical guidelines:
- Test execution workflow for development
- Test development guidelines and naming conventions
- File system testing patterns and external dependency mocking
- Error handling test strategies
- Performance considerations and test categories

**When to use**: Writing new tests, setting up testing environment, or understanding testing philosophy.

### [20250614-error-handling.md](20250614-error-handling.md)
**Error handling policies and implementation patterns**

Detailed error handling strategies and implementation guidance:
- Fail-fast vs graceful degradation decision criteria
- Exception handling patterns and anti-patterns
- File operation error handling strategies
- User vs developer error message priorities
- Specific implementation examples and code patterns

**When to use**: Implementing error handling, debugging complex error scenarios, or understanding error handling philosophy.

### [20250613-resource-support.md](20250613-resource-support.md) ⚠️ DEPRECATED
**Legacy resource handling and packaging details**

Historical documentation of the previous resource management system:
- Package resource access patterns (no longer used)
- JSON schema file handling (migrated to code-based)
- Resource distribution in different installation scenarios
- Resource loading under various deployment methods

**When to use**: Understanding legacy architecture or migration context. See [20250621-schema-migration-1.md](20250621-schema-migration-1.md) for current implementation.

### [20250621-schema-migration-1.md](20250621-schema-migration-1.md) ⚠️ DEPRECATED
**Phase 1: JSON to Code-based Schema Migration**

Historical documentation of the first phase migration from JSON-based to code-based dictionary schemas:
- Migration methodology and implementation phases (Phase 1)
- Before/after architecture comparison (JSON → Dictionaries)
- Technical improvements and benefits analysis from JSON elimination
- Legacy code examples and API changes
- Testing strategy and validation results

**When to use**: Understanding deprecated evolution or legacy architecture context. See [20250621-schema-migration-2.md](20250621-schema-migration-2.md) for current Pydantic-based implementation.

### [20250621-schema-migration-2.md](20250621-schema-migration-2.md) ✨ CURRENT
**Phase 2: Dictionary to Pydantic Schema Migration**

Current schema architecture documentation covering the migration to Pydantic class-based schemas:
- Complete migration from dictionary-based to Pydantic class generation
- `create_model` implementation for dynamic schemas
- Type safety and IDE support enhancements
- Performance improvements and developer experience gains
- Comprehensive test updates and documentation changes
- Gemini API compatibility considerations and fixes

**When to use**: Understanding current schema architecture, implementing new AI operations with type safety, or working with Pydantic-based schemas.

### [20250616-translation-strategy.md](20250616-translation-strategy.md)
**Multi-language support and translation architecture**

Comprehensive documentation of the LLM-powered translation approach:
- Two-phase translation strategy (content generation + UI translation)
- Schema-based language support with placeholder system
- Dynamic translation without static resource files
- Future expansion opportunities and implementation strategies

**When to use**: Working with multi-language features, extending translation coverage, or understanding the translation architecture.

### [20250621-schema-compatibility.md](20250621-schema-compatibility.md)
**Schema design and LLM API compatibility**

Technical guide to schema design constraints and compatibility considerations:
- LLM API limitations and restrictions (Gemini, OpenAI, etc.)
- Dynamic schema generation with `create_model` patterns
- `additionalProperties` compatibility issues and solutions
- Multi-API compatibility best practices and testing strategies

**When to use**: Designing new schemas, troubleshooting API compatibility issues, or understanding LLM API constraints.

## Navigation Guide

### For New Developers
1. Start with [architecture.md](architecture.md) to understand the system design
2. Review [20250621-schema-migration-2.md](20250621-schema-migration-2.md) for current Pydantic-based schema architecture
3. Check [development-history.md](development-history.md) for context on key decisions
4. Review [20250615-testing.md](20250615-testing.md) for testing setup and patterns
5. Reference [20250614-error-handling.md](20250614-error-handling.md) when implementing error handling

### For Troubleshooting
1. Check [20250615-troubleshooting.md](20250615-troubleshooting.md) for common issues
2. Review [20250614-error-handling.md](20250614-error-handling.md) for error handling patterns
3. Consult [development-history.md](development-history.md) for historical context on complex issues

### For Adding Features
1. Follow the methodology in [architecture.md](architecture.md)
2. Review Pydantic schema patterns in [20250621-schema-migration-2.md](20250621-schema-migration-2.md) for AI operations
3. Check API compatibility guidelines in [20250621-schema-compatibility.md](20250621-schema-compatibility.md) for LLM integrations
4. Implement tests according to [20250615-testing.md](20250615-testing.md)
5. Handle errors per [20250614-error-handling.md](20250614-error-handling.md)
6. Consider lessons from [development-history.md](development-history.md)

### For Understanding Decisions
1. Read [development-history.md](development-history.md) for detailed examples
2. Check [architecture.md](architecture.md) for architectural rationale
3. Review evolution context in the main [NOTES.md](../NOTES.md)

## Document Relationships

```
NOTES.md (Philosophy & Core Lessons)
    ↓
architecture.md (Technical Design & Methodology)
    ↓
20250621-schema-migration-2.md (Current Pydantic Schema Architecture) ✨
    ↓
20250621-schema-migration-1.md (Deprecated Schema Evolution) ⚠️
    ↓
development-history.md (Detailed Examples & Evolution)
    ↓
20250615-testing.md, 20250614-error-handling.md, 20250616-translation-strategy.md, 20250621-schema-compatibility.md (Implementation Specifics)
20250613-resource-support.md (Legacy - DEPRECATED) ⚠️
    ↓
20250615-troubleshooting.md (Practical Problem Solving)
```

Each document builds upon the previous level, providing increasing detail and specificity while maintaining clear separation of concerns.

## File Naming Convention

All documentation files in this directory follow a consistent naming pattern:

```
YYYYMMDD-filename.md
```

- **YYYYMMDD**: Date prefix for chronological ordering (e.g., 20250615)
- **filename**: Descriptive name using kebab-case (e.g., error-handling)
- **Exception**: README.md maintains its standard name without date prefix

This convention provides:
- **Intuitive chronological relationships**: Instantly see which documents came before/after others
- **Evolution tracking**: Understand the development timeline and how concepts evolved
- **Quick navigation**: Sort files naturally to follow the project's historical progression

## Maintenance Notes

- **Cross-references**: All documents include appropriate links to related information
- **Consistency**: Terminology and examples are consistent across documents
- **Completeness**: Each document covers its scope comprehensively without overlap
- **Currency**: Documents are updated as the system evolves

This documentation structure emerged from the iterative refinement process described in [NOTES.md](../NOTES.md), following the principle of organizing information by audience and use case rather than arbitrary categories.
