#!/usr/bin/env python3
"""
HTML processing utilities

Provides HTML content preprocessing and text extraction functionality.
"""

import re
import html
from pathlib import Path
from importlib import resources


# Default cache directory name
DEFAULT_CACHE_DIR = "url2md-cache"


def extract_body_content(html_content: str) -> str:
    """Extract innerHTML from body tag and remove script and style tags"""
    try:
        # Extract body tag content
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
        if body_match:
            body_content = body_match.group(1)
        else:
            # Use entire content if no body tag found
            body_content = html_content
        
        # Remove script and style tags
        body_content = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
        body_content = re.sub(r'<style[^>]*>.*?</style>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
        
        return body_content.strip()
    except Exception:
        # Return original content if error occurs
        return html_content


def extract_html_title(html_content: str) -> str:
    """Extract title tag content from HTML"""
    try:
        # Extract title tag content (case insensitive)
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.DOTALL | re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Decode HTML entities
            return html.unescape(title)
        else:
            return ""
    except Exception:
        # Return empty string if error occurs
        return ""


def find_cache_dir() -> Path:
    """Find cache directory by looking for cache.tsv in current or parent directories
    
    Returns:
        Path to directory containing cache.tsv
    
    Raises:
        ValueError: If no cache.tsv found (requires explicit initialization)
    """
    current_dir = Path.cwd()
    
    # First, check if default cache directory exists in current directory
    default_cache = current_dir / DEFAULT_CACHE_DIR
    default_tsv = default_cache / "cache.tsv"
    try:
        if default_tsv.exists():
            return Path(DEFAULT_CACHE_DIR)  # Return relative path for current directory
    except PermissionError:
        pass
    
    # Check current directory and parent directories for cache.tsv
    for directory in [current_dir] + list(current_dir.parents):
        try:
            # Look for cache.tsv in any subdirectory
            for path in directory.iterdir():
                if path.is_dir():
                    tsv_file = path / "cache.tsv"
                    try:
                        if tsv_file.exists():
                            return path
                    except PermissionError:
                        # Skip directories we can't access
                        continue
        except PermissionError:
            # Skip directories we can't iterate
            continue
    
    # If no cache.tsv found, require initialization
    raise ValueError("No cache directory found. Run 'url2md init' to initialize.")


def get_resource_path(filename: str) -> Path:
    """Get path to a resource file in the package
    
    Args:
        filename: Resource filename relative to package root
        
    Returns:
        Path object pointing to the resource file
    """
    # For Python 3.9+
    files = resources.files("url2md")
    return files / filename