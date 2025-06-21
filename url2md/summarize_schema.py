"""
Schema definitions for URL summarization operations.

This module provides functions to create Pydantic schema classes for AI-powered
content summarization with multi-language support.
"""

from typing import Optional, Dict, Any, List, Type
from pydantic import BaseModel, Field


def create_summarize_schema_class(language: Optional[str] = None) -> Type[BaseModel]:
    """
    Create Pydantic schema class for URL content summarization.
    
    Args:
        language: Optional language code for localized output.
                 If provided, schema descriptions will include language specification.
                 
    Returns:
        Pydantic BaseModel class for summarization output.
    """
    lang_suffix = f" in {language}" if language else ""
    
    class SummarizeResult(BaseModel):
        title: str = Field(
            description=f"Page title{lang_suffix} (appropriate title inferred from content)"
        )
        summary_one_line: str = Field(
            description=f"Concise one-line summary{lang_suffix} within 50 characters"
        )
        summary_detailed: str = Field(
            description=f"Detailed summary{lang_suffix} of 200-400 characters including main topics, content, academic/educational value, and technical fields"
        )
        tags: List[str] = Field(
            description=f"List of tags{lang_suffix} representing the content (e.g., linguistics, mathematics, physics, programming)"
        )
        is_valid_content: bool = Field(
            description="Whether the content is meaningful (not error pages or empty pages)"
        )
    
    return SummarizeResult


