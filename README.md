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

# Source installation with uv
git clone https://github.com/7shi/url2md.git
cd url2md
uv sync

# Optional for dynamic rendering
uv run playwright install
```

## Workflow Overview

url2md follows a standard workflow to analyze URLs and generate reports:

1. **Initialize** → Create cache directory structure (one-time setup)
2. **Fetch** → Download and cache web content
3. **Summarize** → Generate AI-powered summaries  
4. **Classify** → Extract tags and categorize by themes
5. **Report** → Create comprehensive Markdown reports

### Quick Examples

Here are the standard workflow commands (same as shown by `uv run url2md`):

```bash
# Initialize cache directory (required first step, creates `url2md-cache/`)
uv run url2md init

# Step-by-step workflow
uv run url2md fetch -u urls.txt --playwright
uv run url2md summarize -u urls.txt
uv run url2md classify -u urls.txt -o class.json
uv run url2md report -u urls.txt -c class.json -o report.md

# Complete workflow in one command (fetch → summarize → classify → report)
uv run url2md workflow -u urls.txt --playwright -c class.json -o report.md

# With Japanese language output for AI operations
uv run url2md summarize -u urls.txt -l Japanese
uv run url2md classify -u urls.txt -o class.json -l Japanese
uv run url2md workflow -u urls.txt -c class.json -o report.md -l Japanese
```

For more command details, use `uv run url2md <command> --help`.

## Global Options

These options must be specified before the subcommand:

```bash
# Cache directory (applies to all commands)
url2md --cache-dir /custom/cache <command> [options]

# Debug mode (shows full stack traces)
url2md --debug <command> [options]

# Examples
url2md --cache-dir /tmp/cache fetch -u urls.txt
url2md --debug --cache-dir /custom/cache summarize -u urls.txt
```

### Cache Directory Detection

url2md automatically detects cache directories by looking for `cache.tsv` files in parent directories, similar to how git finds `.git` directories:

1. **Priority**: If `url2md-cache/cache.tsv` exists in the current directory, it uses `url2md-cache` (relative path)
2. **Parent Search**: Otherwise, searches for any directory containing `cache.tsv` in current and parent directories
3. **Initialization Required**: If no `cache.tsv` is found, you must run `url2md init` to create a cache

This allows you to run url2md commands from any subdirectory within your project, and it will automatically find and use the appropriate cache directory.

```bash
# Running from project root
project/
├── url2md-cache/
│   └── cache.tsv    # Uses this cache
└── subdir/
    └── (working here) # Automatically finds ../url2md-cache

# Custom cache directory names are supported
project/
├── my_url_cache/
│   └── cache.tsv    # Uses this cache (directory name is flexible)
└── src/
```

## Command Reference

### `init` - Initialize cache directory

**Required first step**: Creates cache directory structure with `cache.tsv` file.

```bash
# Initialize cache in current directory (creates ./url2md-cache/)
url2md init

# Initialize with custom directory name
url2md init my_cache

# Initialize with custom path (global option)
url2md --cache-dir /path/to/cache init

# Note: Cannot specify both --cache-dir and directory argument
# url2md --cache-dir foo init bar  # Error: conflicting arguments
```

### `fetch` - Download and cache URLs

**Default behavior**: Skip previously failed URLs and show count. Use `--retry` to retry errors.

```bash
# Basic usage (skips errors by default)
url2md fetch "https://example.com"

# Multiple URLs
url2md fetch "https://example.com" "https://another-site.com"

# From file
url2md fetch -u urls.txt

# Retry failed URLs explicitly
url2md fetch -r -u urls.txt

# With dynamic rendering
url2md fetch --playwright -u urls.txt

# Custom cache directory (global option)
url2md --cache-dir /path/to/cache fetch -u urls.txt

# Force re-fetch all URLs
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

# Generate summaries in Japanese
url2md summarize -u urls.txt -l Japanese

# Generate summaries in Chinese
url2md summarize -u urls.txt -l Chinese
```

### `classify` - Classify content by topic

```bash
# Extract and show tag statistics for all cached content
url2md classify --extract-tags

# Classify specific URLs with LLM (output file required)
url2md classify "https://example.com" -o classification.json

# Classify URLs from file (output file required)
url2md classify -u urls.txt -o classification.json

# Show classification prompt only (no LLM call)
url2md classify --show-prompt

# Classify with Japanese theme names and descriptions
url2md classify -u urls.txt -o classification.json -l Japanese

# Show classification prompt in specified language
url2md classify --show-prompt -l Japanese
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

### `workflow` - Complete workflow

```bash
# Run complete workflow (classification file required)
url2md workflow -u urls.txt -c classification.json -o final-report.md

# With custom settings
url2md --cache-dir url2md-cache workflow \
    -u urls.txt \
    --playwright \
    -c classification.json \
    -o report.md

# With theme weight adjustments
url2md workflow \
    -u urls.txt \
    -c classification.json \
    -t "Programming:1.5" \
    -t "Education:0.8" \
    -o report.md

# With Japanese language output for AI operations
url2md workflow \
    -u urls.txt \
    -c classification.json \
    -o report.md \
    -l Japanese
```

## Language Support

url2md supports multi-language output for AI operations (summarize and classify commands):

```bash
# Supported languages (examples)
url2md summarize -u urls.txt -l Japanese
url2md summarize -u urls.txt -l Chinese
url2md summarize -u urls.txt -l French
url2md summarize -u urls.txt -l Spanish

# Apply to classification as well
url2md classify -u urls.txt -o class.json -l Japanese

# Use in complete workflow
url2md workflow -u urls.txt -c class.json -o report.md -l Japanese
```

**Language Support Features:**
- **Summarize**: Generates titles, summaries, and tags in specified language
- **Classify**: Creates theme names and descriptions in specified language  
- **Workflow**: Applies language setting to both summarize and classify steps
- **Prompts**: Use `--show-prompt -l LANGUAGE` to see localized classification prompts

**Notes:**
- Language setting only affects AI-generated content (summaries, themes)
- Original URLs and technical metadata remain unchanged
- Any language name can be specified (e.g., "Japanese", "中文", "Français")

## Environment Variables

- `GEMINI_API_KEY`: Required for AI summarization and classification operations (not needed for `--extract-tags` or `--show-prompt`)

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
url2md-cache/
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
# Install development dependencies first (if not done already)
uv sync --dev

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=url2md --cov-report=html
```

**Development vs Usage**:
- **For development**: Use `uv sync --dev` to install development tools like pytest, black, and flake8
- **For usage only**: Use `uv sync` to install only runtime dependencies needed to run url2md

For detailed testing commands and development workflows, see [CLAUDE.md](CLAUDE.md#test-development).

## Contributing

This project welcomes contributions. The codebase is designed to be modular and extensible.

### Documentation

- **[README.md](README.md)** - User documentation and command reference
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines and technical specifications  
- **[NOTES.md](NOTES.md)** - Development philosophy and lessons learned

For development guidelines, see [CLAUDE.md](CLAUDE.md).

For detailed architecture information, development guidelines, and troubleshooting, see [CLAUDE.md](CLAUDE.md).
