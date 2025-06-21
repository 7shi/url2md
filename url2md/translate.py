#!/usr/bin/env python3
"""
Generic translation functionality using LLM

Provides utilities for translating terms using AI models with caching support.
"""

import json
from typing import List, Dict, Optional

from llm7shi import generate_content_retry, config_from_schema, build_schema_from_json
from .schema import create_translate_schema_class


def create_translation_schema(terms: List[str], language: str) -> Dict:
    """Generate translation schema dynamically using Pydantic approach
    
    Args:
        terms: List of terms to translate
        language: Target language for translation
    
    Returns:
        Dict: JSON schema dictionary
    """
    schema_class = create_translate_schema_class(terms, language)
    return schema_class.model_json_schema()


def create_translation_prompt(terms: List[str], language: str) -> str:
    """Generate prompt for translating terms
    
    Args:
        terms: List of terms to translate
        language: Target language for translation
    
    Returns:
        str: Translation prompt
    """
    term_list = '\n'.join(f'- {term}' for term in terms)
    
    return f"""Please translate the following terms to {language}:
{term_list}

Return the translations in the exact same order as provided.
Keep the translations concise and appropriate for their context."""


def translate_terms(terms: List[str], language: str, model: str) -> Dict[str, str]:
    """Translate a list of terms to the specified language
    
    Args:
        terms: List of terms to translate
        language: Target language
        model: Model to use for translation
    
    Returns:
        Dict[str, str]: Mapping of original terms to translations
    """
    
    # Generate Pydantic schema class and prompt
    schema_class = create_translate_schema_class(terms, language)
    prompt = create_translation_prompt(terms, language)
    
    # Configure model with Pydantic schema
    config = config_from_schema(schema_class)
    
    # Generate translations
    response = generate_content_retry([prompt], model=model, config=config)
    
    # Parse JSON response
    translation_data = json.loads(response.text.strip())
    return translation_data.get('translations', {})
