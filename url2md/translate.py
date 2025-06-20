#!/usr/bin/env python3
"""
Generic translation functionality using LLM

Provides utilities for translating terms using AI models with caching support.
"""

import json
from typing import List, Dict, Optional

from llm7shi import generate_content_retry, config_from_schema_string
from .utils import get_resource_path


def create_translation_schema(terms: List[str], language: str) -> str:
    """Generate translation schema dynamically
    
    Args:
        terms: List of terms to translate
        language: Target language for translation
    
    Returns:
        str: JSON schema string with placeholders replaced
    """
    # Generate properties and required fields
    properties = []
    required = []
    
    for term in terms:
        properties.append(f'"{term}": {{"type": "string", "description": "Translation of \'{term}\' to {language}"}}')
        required.append(f'"{term}"')
    
    properties_str = ', '.join(properties)
    required_str = ', '.join(required)
    
    # Load base schema and replace placeholders
    schema_path = get_resource_path("schemas/translate.json")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_content = f.read()
    
    # Replace placeholders
    schema_content = schema_content.replace('```translation_properties```', properties_str)
    schema_content = schema_content.replace('```translation_required```', required_str)
    
    return schema_content


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
    
    # Generate schema and prompt
    schema_content = create_translation_schema(terms, language)
    prompt = create_translation_prompt(terms, language)
    
    # Configure model with schema
    config = config_from_schema_string(schema_content)
    
    # Generate translations
    response = generate_content_retry([prompt], model=model, config=config)
    
    # Parse JSON response
    translation_data = json.loads(response.strip())
    return translation_data.get('translations', {})
