# Utils Module

## Why This Implementation Exists

### Graceful HTML Processing
**Problem**: Malformed HTML breaks content extraction and stops processing pipeline.
**Solution**: Fallback-first approach returns original content when HTML parsing fails, ensuring pipeline continues.

### Hierarchical Cache Discovery
**Problem**: Users run commands from different directories but need to find existing cache.
**Solution**: Parent directory traversal finds cache.tsv anywhere in project hierarchy, supporting flexible workflow.

### Package Resource Abstraction
**Problem**: Hard-coded file paths break when package is installed in different environments.
**Solution**: importlib.resources provides package-relative resource access that works across all installation methods.

### Defensive Directory Operations
**Problem**: Permission errors and missing directories can crash the application.
**Solution**: Silent error handling during directory traversal continues search despite individual access failures.