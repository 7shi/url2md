"""
Schema definitions for tag classification operations.

This module provides functions to build JSON schemas for AI-powered
tag classification with multi-language support.
"""

from typing import Optional, Dict, Any


def build_classify_schema(language: Optional[str] = None) -> Dict[str, Any]:
    """
    Build JSON schema for tag classification.
    
    Args:
        language: Optional language code for localized output.
                 If provided, schema descriptions will include language specification.
                 
    Returns:
        Dict containing the JSON schema for classification output.
    """
    lang_suffix = f" in {language}" if language else ""
    
    return {
        "type": "object",
        "properties": {
            "themes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "theme_name": {
                            "type": "string",
                            "description": f"Name of the theme{lang_suffix}"
                        },
                        "theme_description": {
                            "type": "string", 
                            "description": f"Brief description of the theme{lang_suffix}"
                        },
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of tags belonging to this theme"
                        }
                    },
                    "required": ["theme_name", "theme_description", "tags"]
                },
                "description": "List of classified themes"
            },
            "classification_summary": {
                "type": "object",
                "properties": {
                    "total_tags_processed": {
                        "type": "integer",
                        "description": "Total number of tags processed"
                    },
                    "total_themes_created": {
                        "type": "integer", 
                        "description": "Number of themes created"
                    },
                    "classification_approach": {
                        "type": "string",
                        "description": f"Explanation of classification approach and methodology{lang_suffix}"
                    }
                },
                "required": ["total_tags_processed", "total_themes_created", "classification_approach"]
            }
        },
        "required": ["themes", "classification_summary"]
    }