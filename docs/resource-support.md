# Resource Support in url2md

This document describes how url2md handles package resources (schema files) that are bundled with the package.

## Overview

url2md includes JSON schema files that define the structure of AI operations. These files are packaged with the distribution and accessed at runtime using Python's `importlib.resources` module.

## Resource Structure

```
url2md/
├── __init__.py
├── main.py
├── models.py
├── schemas/              # Resource directory
│   ├── summarize.json   # Schema for summarize command
│   └── classify.json    # Schema for classify command
└── utils.py             # Contains resource access utilities
```

## Implementation Details

### Resource Access Function

The `utils.py` module provides a helper function to access package resources:

```python
from importlib import resources
from pathlib import Path

def get_resource_path(filename: str) -> Path:
    """Get path to a resource file in the package
    
    Args:
        filename: Resource filename relative to package root
        
    Returns:
        Path object pointing to the resource file
    """
    files = resources.files("url2md")
    return files / filename
```

### Usage in Modules

#### summarize.py

```python
from .utils import get_resource_path

def summarize_content(..., schema_file: str = None, ...):
    # Load JSON schema configuration
    if schema_file is None:
        schema_path = get_resource_path("schemas/summarize.json")
    else:
        schema_path = schema_file
    config = config_from_schema(str(schema_path))
```

#### classify.py

```python
from .utils import get_resource_path

def classify_tags_with_llm(..., schema_file: str = None, ...):
    # Load JSON schema configuration
    if schema_file is None:
        schema_path = get_resource_path("schemas/classify.json")
    else:
        schema_path = schema_file
    config = config_from_schema(str(schema_path))
```

## Package Configuration

The `pyproject.toml` configuration ensures that resource files are included in the package:

```toml
[tool.hatch.build.targets.wheel]
packages = ["url2md"]
```

Since the `schemas` directory is inside the `url2md` package directory, it is automatically included when the package is built.

## Python Version Compatibility

The current implementation uses `importlib.resources.files()` which is available in Python 3.9+. Since url2md requires Python 3.10+, this is compatible with our requirements.

## Testing Resource Access

To verify that resources are properly included and accessible:

1. **During Development** (with `uv run`):
   ```bash
   # Run actual classification (requires GEMINI_API_KEY)
   uv run url2md classify -u urls.txt -o class.json
   ```

2. **After Installation** (with `uv tool install`):
   ```bash
   # Clean install
   uv tool uninstall url2md
   uv cache clean url2md
   uv tool install .
   
   # Test resource access (requires GEMINI_API_KEY)
   url2md classify -u urls.txt -o class.json
   ```

### Testing Schema Loading

During development, a temporary `--test-schema` option was added to verify schema loading without requiring API access. This option has been removed from the final implementation, but the approach can be useful for debugging:

```python
# Example test code that was temporarily added to main.py
if args.test_schema:
    try:
        from .gemini import config_from_schema
        from .utils import get_resource_path
        schema_path = get_resource_path("schemas/classify.json")
        config = config_from_schema(str(schema_path))
        print("✅ Schema loaded successfully")
        print(f"   Schema type: {type(config)}")
    except Exception as e:
        print(f"❌ Schema loading failed: {e}")
```

Note: The `--show-prompt` option does not load schema files as it only displays the prompt without making API calls.

## Troubleshooting

### Resources Not Found After Installation

If you encounter "File not found" errors after installation:

1. **Clean the cache**: `uv cache clean url2md`
2. **Verify directory structure**: Ensure `schemas/` is inside `url2md/`
3. **Check package build**: Resources should be listed in the wheel file

### Development vs Production

- **Development**: Resources are read directly from the source tree
- **Production**: Resources are extracted from the installed package

Both scenarios are handled transparently by `importlib.resources`.

## Benefits

1. **No hardcoded paths**: Resources work regardless of installation location
2. **Package integrity**: Schema files are bundled with the code
3. **Cross-platform**: Works on all operating systems
4. **Future-proof**: Uses standard Python resource handling

## Migration Notes

The schemas directory was moved from the project root to inside the package:
- **Before**: `project_root/schemas/`
- **After**: `project_root/url2md/schemas/`

This change was made using `git mv schemas url2md/` to preserve history.