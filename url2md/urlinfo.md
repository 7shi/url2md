# URLInfo Module

## Why This Implementation Exists

### Centralized URL Metadata Management
**Problem**: URL metadata scattered across different data structures makes caching unreliable and error-prone.
**Solution**: Single URLInfo dataclass consolidates all URL-related information (content, status, hashes) for consistent cache operations.

### Automatic Derived Attributes
**Problem**: Manual hash generation and domain extraction creates inconsistency and errors across the application.
**Solution**: Post-init automation ensures URL hash and domain are always calculated correctly and consistently.

### Smart Content Fetching Strategy
**Problem**: Different content types require different fetching methods (dynamic vs static) but determining the right approach manually is error-prone.
**Solution**: Built-in logic detects binary content and chooses appropriate fetching method (Playwright vs requests) with automatic fallback.

### TSV Serialization for Human Readability
**Problem**: Binary cache formats are opaque and difficult to debug or manually inspect.
**Solution**: TSV format provides human-readable cache storage with robust escaping for special characters.

### Fail-Fast File Loading
**Problem**: Silent failures in URL file loading lead to incomplete processing and hard-to-debug issues.
**Solution**: Explicit error handling with stack traces and sys.exit(1) for file read errors ensures problems are immediately visible.