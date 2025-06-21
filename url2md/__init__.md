# __init__.py

## Overview

This is the package initialization file for url2md, which serves as the main entry point for the package. It defines the package metadata, imports key components, and explicitly declares the public API through `__all__`.

## Package Metadata

- **__version__**: Dynamically retrieved from package metadata using `importlib.metadata.version()`
- **__author__**: "url2md contributors"
- **__license__**: "CC0-1.0" (Creative Commons Zero - Public Domain)

## Imports and Exports

The file imports and re-exports commonly used components from various modules:

### HTML Utilities (from utils.py)
- `extract_body_content`: Extracts body content from HTML
- `extract_html_title`: Extracts title from HTML documents

### Download Utilities (from download.py)
- `PLAYWRIGHT_AVAILABLE`: Boolean flag indicating if Playwright is installed
- `download`: Function to download content from URLs
- `is_text`: Checks if content type is text-based
- `user_agent`: User agent string for HTTP requests

### Data Models and Cache (from urlinfo.py and cache.py)
- `URLInfo`: Data model for URL information
- `load_urls_from_file`: Loads URLs from a file
- `Cache`: Cache management class
- `CacheResult`: Cache result data structure

## Public API

The `__all__` list explicitly defines what is exported when using `from url2md import *`. This includes all the imported components above, organized into categories:
- Version information
- HTML processing utilities
- Download functionality
- Data models and caching

## Function Modules

The file includes comments noting that function modules are available as submodules but not automatically imported:
- `fetch.fetch_urls`: URL fetching functionality
- `summarize.summarize_urls`: AI-powered summarization
- `classify.extract_tags, classify_tags_with_llm`: Tag classification
- `report.generate_markdown_report`: Report generation

This design keeps the main import lightweight while making submodules available for specific use cases.