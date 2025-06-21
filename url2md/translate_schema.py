"""
Schema definitions for translation operations.

This module provides functions to build JSON schemas for AI-powered
translation with dynamic term support.
"""

from typing import List, Dict, Any


def build_translate_schema(terms: List[str]) -> Dict[str, Any]:
    """
    Build JSON schema for term translation.
    
    Args:
        terms: List of terms to be translated.
               Each term becomes a required property in the schema.
                 
    Returns:
        Dict containing the JSON schema for translation output.
    """
    # Build properties dynamically from terms list
    properties = {}
    for term in terms:
        properties[term] = {
            "type": "string",
            "description": f"Translation of '{term}'"
        }
    
    return {
        "type": "object",
        "properties": {
            "translations": {
                "type": "object",
                "properties": properties,
                "required": terms,
                "additionalProperties": False
            }
        },
        "required": ["translations"],
        "additionalProperties": False
    }