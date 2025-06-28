# Translation Cache Module

## Why This Implementation Exists

### LLM Call Optimization
**Problem**: Repeated translation requests for the same UI terms waste API calls and slow down processing.
**Solution**: Persistent TSV cache stores translations locally, eliminating redundant LLM requests.

### Tuple-Based Key Design
**Problem**: Simple string keys cannot handle multiple languages for the same English term.
**Solution**: (english, language) tuple keys ensure unique translations per language combination.

### Memory-Plus-Persistence Pattern
**Problem**: File I/O for every translation lookup would be too slow for report generation.
**Solution**: Load all translations into memory for fast lookups while maintaining persistent TSV storage.

### Translation Lifecycle Management
**Problem**: Translations created during classification need to be available for subsequent report generation.
**Solution**: Centralized cache accessible from both classification and report commands ensures translation consistency.