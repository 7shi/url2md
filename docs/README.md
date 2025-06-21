# Documentation Overview

This directory contains specialized documentation for different aspects of the url2md project. Each document serves a specific purpose in the development and maintenance workflow.

## User-Oriented Documentation

### [troubleshooting.md](troubleshooting.md)
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

### [testing.md](testing.md)
**Testing guidelines and best practices**

Comprehensive testing approach and practical guidelines:
- Test execution workflow for development
- Test development guidelines and naming conventions
- File system testing patterns and external dependency mocking
- Error handling test strategies
- Performance considerations and test categories

**When to use**: Writing new tests, setting up testing environment, or understanding testing philosophy.

### [error-handling.md](error-handling.md)
**Error handling policies and implementation patterns**

Detailed error handling strategies and implementation guidance:
- Fail-fast vs graceful degradation decision criteria
- Exception handling patterns and anti-patterns
- File operation error handling strategies
- User vs developer error message priorities
- Specific implementation examples and code patterns

**When to use**: Implementing error handling, debugging complex error scenarios, or understanding error handling philosophy.

### [resource-support.md](resource-support.md) ⚠️ DEPRECATED
**Legacy resource handling and packaging details**

Historical documentation of the previous resource management system:
- Package resource access patterns (no longer used)
- JSON schema file handling (migrated to code-based)
- Resource distribution in different installation scenarios
- Resource loading under various deployment methods

**When to use**: Understanding legacy architecture or migration context. See [schema-migration.md](schema-migration.md) for current implementation.

### [schema-migration.md](schema-migration.md) ✨ NEW
**Schema architecture migration documentation**

Comprehensive documentation of the migration from JSON-based to code-based schemas:
- Migration methodology and implementation phases
- Before/after architecture comparison
- Technical improvements and benefits analysis
- Code examples and API changes
- Testing strategy and validation results

**When to use**: Understanding current schema architecture, implementing new AI operations, or learning from architectural improvements.

### [translation-strategy.md](translation-strategy.md)
**Multi-language support and translation architecture**

Comprehensive documentation of the LLM-powered translation approach:
- Two-phase translation strategy (content generation + UI translation)
- Schema-based language support with placeholder system
- Dynamic translation without static resource files
- Future expansion opportunities and implementation strategies

**When to use**: Working with multi-language features, extending translation coverage, or understanding the translation architecture.

## Navigation Guide

### For New Developers
1. Start with [architecture.md](architecture.md) to understand the system design
2. Review [schema-migration.md](schema-migration.md) for current schema architecture
3. Check [development-history.md](development-history.md) for context on key decisions
4. Review [testing.md](testing.md) for testing setup and patterns
5. Reference [error-handling.md](error-handling.md) when implementing error handling

### For Troubleshooting
1. Check [troubleshooting.md](troubleshooting.md) for common issues
2. Review [error-handling.md](error-handling.md) for error handling patterns
3. Consult [development-history.md](development-history.md) for historical context on complex issues

### For Adding Features
1. Follow the methodology in [architecture.md](architecture.md)
2. Review schema patterns in [schema-migration.md](schema-migration.md) for AI operations
3. Implement tests according to [testing.md](testing.md)
4. Handle errors per [error-handling.md](error-handling.md)
5. Consider lessons from [development-history.md](development-history.md)

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
schema-migration.md (Current Schema Architecture) ✨
    ↓
development-history.md (Detailed Examples & Evolution)
    ↓
testing.md, error-handling.md, translation-strategy.md (Implementation Specifics)
resource-support.md (Legacy - DEPRECATED) ⚠️
    ↓
troubleshooting.md (Practical Problem Solving)
```

Each document builds upon the previous level, providing increasing detail and specificity while maintaining clear separation of concerns.

## Maintenance Notes

- **Cross-references**: All documents include appropriate links to related information
- **Consistency**: Terminology and examples are consistent across documents
- **Completeness**: Each document covers its scope comprehensively without overlap
- **Currency**: Documents are updated as the system evolves

This documentation structure emerged from the iterative refinement process described in [NOTES.md](../NOTES.md), following the principle of organizing information by audience and use case rather than arbitrary categories.