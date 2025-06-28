# TSV Manager Module

## Why This Implementation Exists

### Atomic File Writing Safety
**Problem**: System crashes during file writes can corrupt TSV data files.
**Solution**: Temporary file with atomic rename prevents partial writes and ensures data integrity.

### Consistent Data Sanitization
**Problem**: Tabs and newlines in data fields break TSV format parsing.
**Solution**: Centralized sanitization function ensures all TSV files maintain format consistency.

### Inheritance-Ready Base Class
**Problem**: Multiple TSV file types (cache, translations) would duplicate file handling code.
**Solution**: Base class provides common operations while allowing specialized behavior in subclasses.

### Format Flexibility
**Problem**: Different TSV files need different header structures and data handling.
**Solution**: Generic List[List[str]] data structure accommodates any TSV schema without code changes.