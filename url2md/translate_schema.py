"""
Schema definitions for translation operations.

This module provides functions to create Pydantic schema classes for AI-powered
translation with dynamic term support using create_model.
"""

from typing import List, Type, Dict, Any
from pydantic import BaseModel, Field, create_model, ConfigDict


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

