"""
Schema definitions for tag classification operations.

This module provides functions to create Pydantic schema classes for AI-powered
tag classification with multi-language support.
"""

from typing import Optional, Dict, Any, List, Type
from pydantic import BaseModel, Field


def create_classify_schema_class(language: Optional[str] = None) -> Type[BaseModel]:
    """
    Create Pydantic schema class for tag classification.
    
    Args:
        language: Optional language code for localized output.
                 If provided, schema descriptions will include language specification.
                 
    Returns:
        Pydantic BaseModel class for classification output.
    """
    lang_suffix = f" in {language}" if language else ""
    
    class Theme(BaseModel):
        theme_name: str = Field(description=f"Name of the theme{lang_suffix}")
        theme_description: str = Field(description=f"Brief description of the theme{lang_suffix}")
        tags: List[str] = Field(description="List of tags belonging to this theme")
    
    class ClassificationSummary(BaseModel):
        total_tags_processed: int = Field(description="Total number of tags processed")
        total_themes_created: int = Field(description="Number of themes created")
        classification_approach: str = Field(
            description=f"Explanation of classification approach and methodology{lang_suffix}"
        )
    
    class ClassifyResult(BaseModel):
        themes: List[Theme] = Field(description="List of classified themes")
        classification_summary: ClassificationSummary
    
    return ClassifyResult


