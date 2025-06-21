"""
Schema definitions for URL summarization operations.

This module provides functions to build JSON schemas for AI-powered
content summarization with multi-language support.
"""

from typing import Optional, Dict, Any


def build_summarize_schema(language: Optional[str] = None) -> Dict[str, Any]:
    """
    Build JSON schema for URL content summarization.
    
    Args:
        language: Optional language code for localized output.
                 If provided, schema descriptions will include language specification.
                 
    Returns:
        Dict containing the JSON schema for summarization output.
    """
    lang_suffix = f" in {language}" if language else ""
    
    return {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": f"Page title{lang_suffix} (appropriate title inferred from content)"
            },
            "summary_one_line": {
                "type": "string",
                "description": f"Concise one-line summary{lang_suffix} within 50 characters"
            },
            "summary_detailed": {
                "type": "string", 
                "description": f"Detailed summary{lang_suffix} of 200-400 characters including main topics, content, academic/educational value, and technical fields"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"List of tags{lang_suffix} representing the content (e.g., linguistics, mathematics, physics, programming)"
            },
            "is_valid_content": {
                "type": "boolean",
                "description": "Whether the content is meaningful (not error pages or empty pages)"
            }
        },
        "required": ["title", "summary_one_line", "summary_detailed", "tags", "is_valid_content"]
    }