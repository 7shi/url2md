"""
Schema definitions for all AI operations.

This module provides functions to create Pydantic schema classes for AI-powered
operations including summarization, classification, and translation with 
multi-language support.
"""

from typing import Optional, List, Type
from pydantic import BaseModel, Field, create_model


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


def create_translate_schema_class(terms: List[str]) -> Type[BaseModel]:
    """
    Create Pydantic schema class for term translation.
    
    Args:
        terms: List of terms to be translated.
               Each term becomes a required field in the schema.
                 
    Returns:
        Pydantic BaseModel class for translation output.
    """
    # Build dynamic fields from terms list
    translation_fields = {
        term: (str, Field(description=f"Translation of '{term}'"))
        for term in terms
    }
    
    # Create dynamic TranslationDict class
    TranslationDict = create_model(
        'TranslationDict',
        **translation_fields
    )
    
    # Main result class
    class TranslateResult(BaseModel):
        translations: TranslationDict
    
    return TranslateResult