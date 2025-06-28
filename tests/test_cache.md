# Test Cache Module

## Why This Implementation Exists

### Challenge of URL Fetch Result Management
**Problem**: URL fetching operations are expensive and unreliable - network requests fail, content changes over time, and repeated fetches waste resources and API quotas.
**Solution**: Implemented persistent cache system with TSV-based storage to eliminate redundant network operations while maintaining data integrity across application restarts.

### Filename Collision in Content Storage
**Problem**: URLs can generate identical hash values or filenames, causing data overwrites and content loss in file-based storage systems.
**Solution**: Adopted collision detection with automatic filename incrementing (-1, -2, etc.) to ensure unique storage paths for all cached content.

### Cross-Session Data Persistence
**Problem**: In-memory caches lose all data when applications restart, forcing expensive re-fetching of previously processed URLs.
**Solution**: Implemented TSV-based persistence that automatically loads cached data on startup, preserving fetch results across application lifecycle.

### Domain-Based Request Throttling
**Problem**: Rapid successive requests to the same domain can trigger rate limiting or server blocking, causing fetch failures.
**Solution**: Built domain-aware throttling mechanism to space requests appropriately, preventing server overload and improving fetch success rates.