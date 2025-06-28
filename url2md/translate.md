# Translation Module

## Why This Implementation Exists

### Dynamic Schema-Driven Translation
**Problem**: Multi-language report generation requires translating UI terms consistently across different languages, but hardcoded translation tables don't scale and LLM APIs need structured schemas to ensure reliable JSON output format.
**Solution**: Provides dynamic schema-driven translation using Pydantic models generated at runtime, creating language-aware field descriptions and structured prompts for any term list.

### Generic Reusable Design
**Problem**: Translation functionality was needed for report UI terms but hardcoding specific terms limits future extensibility.
**Solution**: Accepts any term list rather than hardcoded UI terms, enabling the classification system to generate translations while remaining reusable for any translation scenario requiring structured output validation.

### Structured Output Reliability
**Problem**: LLM translation responses can be inconsistent in format, breaking downstream processing.
**Solution**: Uses schema-enforced LLM responses through Pydantic models to ensure reliable JSON parsing and type safety.