#!/usr/bin/env python3
"""
HTML processing utilities

Provides HTML content preprocessing and text extraction functionality.
"""

import re
import html
import sys
import traceback
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
    except Exception:
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
                    except Exception:
                        # Skip directories we can't access
                        continue
        except Exception:
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


def print_error_with_line(error_message: str, error: Exception) -> None:
    """Print error message with line number information
    
    Args:
        error_message: Custom error message to display
        error: Exception to display with traceback information
    """
    # Get the current exception info
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    if exc_traceback is None:
        # If no current exception, just print the message
        print(f"{error_message}: {error}", file=sys.stderr)
        return
    
    # Get traceback details
    tb_list = traceback.extract_tb(exc_traceback)
    
    if tb_list:
        # Get the last frame (where the error occurred)
        last_frame = tb_list[-1]
        filename = last_frame.filename
        line_number = last_frame.lineno
        function_name = last_frame.name
        line_text = last_frame.line
        
        print(f"Error in {filename}:{line_number} in {function_name}()", file=sys.stderr)
        if line_text:
            print(line_text.rstrip(), file=sys.stderr)
        print(f"{error_message}: {exc_value}", file=sys.stderr)
    else:
        print(f"{error_message}: {error}", file=sys.stderr)
