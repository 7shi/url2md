# url2md

URL analysis and classification tool - Generate Markdown reports from URLs through AI-powered content analysis, summarization, and classification.

## Features

- **URL Fetching**: Download and cache web content with support for dynamic rendering via Playwright
- **AI Summarization**: Generate structured summaries using Gemini API
- **Content Classification**: Automatically classify and tag content by topic
- **Markdown Reports**: Generate comprehensive reports in Markdown format
- **Pipeline Processing**: Complete workflow from URLs to final report

## Installation

```bash
# Install the package
pip install url2md

# For dynamic rendering support (optional)
playwright install

# Development setup with uv
git clone <repository>
cd url2md
uv sync
uv run playwright install  # Optional for dynamic rendering
```

## Quick Start

```bash
# Fetch URLs and cache content
url2md fetch "https://example.com" "https://another-site.com"

# Fetch from file
url2md fetch -u urls.txt

# Use dynamic rendering for JavaScript-heavy sites
url2md fetch --playwright -u urls.txt

# Run complete pipeline
url2md pipeline -u urls.txt --output report.md
```

## Commands

### `fetch` - Download and cache URLs

```bash
# Basic usage
url2md fetch "https://example.com"

# Multiple URLs
url2md fetch "https://example.com" "https://another-site.com"

# From file
url2md fetch -u urls.txt

# With dynamic rendering
url2md fetch --playwright -u urls.txt

# Custom cache directory
url2md fetch --cache-dir /path/to/cache -u urls.txt

# Force re-fetch
url2md fetch --force "https://example.com"
```

### `summarize` - Generate AI summaries

```bash
# Summarize all cached content
url2md summarize

# Summarize specific URLs
url2md summarize "https://example.com"

# Summarize URLs from file
url2md summarize -u urls.txt

# Limit number of summaries
url2md summarize --limit 10

# Force re-summarize
url2md summarize --force
```

### `classify` - Classify content by topic

```bash
# Extract and show tag statistics for all cached content
url2md classify --extract-tags

# Classify specific URLs with LLM
url2md classify "https://example.com" --classify -o classification.json

# Classify URLs from file
url2md classify -u urls.txt --classify -o classification.json

# Test mode (show prompt only)
url2md classify --test
```

### `report` - Generate Markdown reports

```bash
# Generate report from classification
url2md report -c classification.json

# Save to file
url2md report -c classification.json -o report.md

# Specify URL subset
url2md report -c classification.json -u urls.txt

# Include specific URLs in report
url2md report "https://example.com" -c classification.json -o report.md

# Adjust theme weights for classification
url2md report -c classification.json -t "Programming:1.5" -t "Education:0.8"
```

### `pipeline` - Complete workflow

```bash
# Run complete pipeline
url2md pipeline -u urls.txt -o final-report.md

# With custom settings
url2md pipeline \
    -u urls.txt \
    --cache-dir cache \
    --playwright \
    --classification-output classification.json \
    -o report.md

# With theme weight adjustments
url2md pipeline \
    -u urls.txt \
    -t "Programming:1.5" \
    -t "Education:0.8" \
    -o report.md
```

## Environment Variables

- `GEMINI_API_KEY`: Required for AI summarization and classification operations

## Requirements

- Python 3.10 or higher
- Internet connection for AI operations
- Optional: Playwright for dynamic rendering support

## File Formats

### URL List File
```
# Comments start with #
https://example.com
https://another-site.com
# Empty lines are ignored

https://third-site.com
```

### Cache Structure
```
cache/
├── cache.tsv              # Metadata index
├── content/               # Downloaded content
│   ├── abc123.html
│   ├── def456.pdf
│   └── ...
└── summary/               # AI-generated summaries
    ├── abc123.json
    ├── def456.json
    └── ...
```

### Summary JSON Format
```json
{
  "title": ["HTML Title", "AI-generated Title"],
  "summary_one_line": "Brief one-line summary",
  "summary_detailed": "Detailed summary with key points...",
  "tags": ["programming", "python", "tutorial"],
  "is_valid_content": true
}
```

### Classification JSON Format
```json
{
  "themes": [
    {
      "theme_name": "Programming",
      "theme_description": "Programming and software development content",
      "tags": ["programming", "coding", "development"]
    },
    {
      "theme_name": "Education", 
      "theme_description": "Educational and learning content",
      "tags": ["tutorial", "learning", "course"]
    }
  ],
  "classification_summary": {
    "total_tags_processed": 35,
    "total_themes_created": 2,
    "classification_approach": "Grouped related tags into thematic categories"
  }
}
```

## License

CC0-1.0 - Public Domain

## Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=url2md --cov-report=html

# Run specific test file
uv run pytest tests/test_cache.py -v
```

## Contributing

This project welcomes contributions. The codebase is designed to be modular and extensible.

For development guidelines, see [CLAUDE.md](CLAUDE.md).

### Architecture

- `url2md/main.py`: CLI entry point and command orchestration
- `url2md/models.py`: Data models (URLInfo, etc.)
- `url2md/cache.py`: Cache management
- `url2md/fetch.py`: URL fetching functions
- `url2md/summarize.py`: AI summarization functions
- `url2md/classify.py`: Tag classification functions
- `url2md/report.py`: Report generation functions
- `url2md/gemini.py`: Gemini API integration
- `url2md/utils.py`: HTML processing utilities
- `url2md/download.py`: Playwright dynamic rendering

### Debug Mode

For troubleshooting, use the `--debug` flag to see full stack traces:

```bash
url2md --debug fetch "https://example.com"
```