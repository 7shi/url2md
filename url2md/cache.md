# Cache Module

## Why This Implementation Exists

### Domain-Based Throttling
**Problem**: Rapid requests to the same domain can trigger rate limiting or blocking.
**Solution**: Per-domain timing controls prevent server overload while maintaining efficient batch processing.

### Collision-Safe Filename Generation
**Problem**: Multiple URLs with similar names would overwrite cached content.
**Solution**: Automatic counter-based naming prevents file collisions while maintaining readable filenames.

### Atomic File Operations
**Problem**: System crashes during cache saves corrupt the cache index.
**Solution**: Temporary file pattern with atomic rename ensures cache integrity is never compromised.

### Centralized Content Organization
**Problem**: Mixed file types and metadata scattered across directories creates management complexity.
**Solution**: Structured directory layout (content/, summary/, terms.tsv) with clear separation of concerns.

### Retry Logic for Failed URLs
**Problem**: Temporary network failures permanently mark URLs as failed.
**Solution**: Automatic retry of URLs with error status or missing content files enables recovery from transient issues.