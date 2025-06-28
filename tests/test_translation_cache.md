# Test Translation Cache

## Why This Implementation Exists

### Challenge of Repeated AI Translation Costs
**Problem**: Multilingual report generation requires translating the same UI terms repeatedly, consuming API quota and introducing latency with each report generation.
**Solution**: Implemented persistent translation cache with TSV storage to eliminate redundant AI translation calls, reducing costs and improving response times for multilingual workflows.

### TSV Format Special Character Conflicts
**Problem**: Translation text can contain tabs, newlines, and other characters that break TSV field separation, corrupting the cache file and preventing data recovery.
**Solution**: Built character sanitization system that replaces problematic characters with spaces while preserving semantic meaning, ensuring TSV format integrity without data loss.

### Multi-Language Term Isolation
**Problem**: Same English terms need different translations per language, but simple key-value storage would cause language conflicts and data overwrites.
**Solution**: Adopted composite key structure (term, language) to enable multiple translations per term while maintaining language isolation and preventing cross-language data conflicts.

### Lazy Cache File Creation
**Problem**: Creating empty cache files on startup wastes file system resources and clutters directories when no translations are needed.
**Solution**: Implemented on-demand file creation that only writes TSV files when actual translation data exists, minimizing file system impact while maintaining automatic loading functionality.