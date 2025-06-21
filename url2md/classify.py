#!/usr/bin/env python3
"""
Extract and analyze tags from cache/summary/, classify with LLM

Extract all tags from summary files, aggregate them, and classify by theme using LLM.
"""

import sys
import json
import traceback
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any, Optional

from .cache import Cache
from llm7shi import generate_content_retry, config_from_schema, build_schema_from_json
from .translate import translate_terms
from .urlinfo import URLInfo
from .classify_schema import build_classify_schema


# Global list of terms that need translation
TRANSLATION_TERMS = ['Summary', 'Themes', 'Total URLs', 'Classified', 'Unclassified', 'URLs', 'Other']


def extract_tags(cache: Cache, url_infos: List[URLInfo]) -> List[str]:
    """Extract tags from URLInfo list
    
    Args:
        cache: Cache object
        url_infos: List of URLInfo objects
    
    Returns:
        List[str]: All tags
    """
    all_tags = []
    
    for url_info in url_infos:
        # Read JSON using Cache method
        summary_file = cache.get_summary_path(url_info)
        if summary_file and summary_file.exists():
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
                
                tags = summary_data.get('tags', [])
                if isinstance(tags, list):
                    all_tags.extend(tags)
                elif isinstance(tags, str):
                    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                    all_tags.extend(tag_list)
            except Exception as e:
                print(f"Warning: Summary file read error ({url_info.url})", file=sys.stderr)
                traceback.print_exc()
    
    return all_tags


def display_tag_statistics(tag_counter: Counter):
    """Display tag statistics"""
    print(f"\n=== TAG STATISTICS ===")
    print(f"Total unique tags: {len(tag_counter)}")
    print(f"Total tag instances: {sum(tag_counter.values())}")
    
    # Frequency statistics
    freq_stats = Counter()
    for tag, count in tag_counter.items():
        if count >= 10:
            freq_stats["10+ occurrences"] += 1
        elif count >= 5:
            freq_stats["5-9 occurrences"] += 1
        elif count >= 2:
            freq_stats["2-4 occurrences"] += 1
        else:
            freq_stats["1 occurrence"] += 1
    
    print(f"\nFrequency distribution:")
    for category, count in freq_stats.most_common():
        print(f"  {category}: {count} tags")
    
    print(f"\n=== TOP TAGS (frequency >= 2) ===")
    
    # Get tags with frequency >= 2
    frequent_tags = [(tag, count) for tag, count in tag_counter.most_common() if count >= 2]
    
    if frequent_tags:
        # Calculate width for max occurrence count
        max_count = frequent_tags[0][1]  # First is max since sorted by most_common()
        count_width = len(str(max_count))
        
        for tag, count in frequent_tags:
            print(f"{count:>{count_width}d} : {tag}")
    else:
        print("(No tags with frequency >= 2)")


def get_frequent_tags_with_counts(tag_counter: Counter, min_frequency: int = 2) -> List[tuple]:
    """Get frequent tags with usage counts (min_frequency or more occurrences)"""
    return [(tag, count) for tag, count in tag_counter.items() if count >= min_frequency]


def create_tag_classification_prompt(tag_counter: Counter, language: str = None) -> str:
    """Generate prompt for tag classification"""
    # Get frequent tags with usage counts
    frequent_tags = get_frequent_tags_with_counts(tag_counter, min_frequency=2)
    
    if not frequent_tags:
        return None
    
    # Sort by usage count
    frequent_tags.sort(key=lambda x: x[1], reverse=True)
    
    # Create tag list string
    tag_list_parts = []
    for tag, count in frequent_tags:
        tag_list_parts.append(f"- {tag} ({count} uses)")
    
    tag_list_str = "\n".join(tag_list_parts)
    
    prompt = f"""Please analyze the following list of tags and classify them into appropriate themes.

TAGS (with usage frequency):
{tag_list_str}

Please output the classification results as structured JSON according to the following requirements:

1. **Theme Classification**: Group similar tags under appropriate theme names
   - Theme names should be concise and clear (e.g., "Programming", "Mathematics", "Linguistics")
   - Each theme should contain a list of tags that belong to that category
   
2. **Theme Weights**: Assign a weight to each theme (floating point number >= 1.0)
   - Weight 1.0 = standard weight
   - Weight > 1.0 = higher priority theme that should be emphasized in classification
   - Consider the importance and specificity of the theme when determining weights

3. **Tag Statistics**: Include the original usage statistics for reference

Requirements:
- Minimize theme duplication and aim for clear categorization
- Each tag should belong to only one theme
- Use appropriate weight values to reflect theme importance
- Include all provided tags in the classification

The output should include complete tag frequency information for use in URL classification algorithms."""
    
    if language:
        prompt += f"\n\nIMPORTANT: Output all text content (theme names, descriptions) in {language}."
    
    return prompt


def classify_tags_with_llm(cache: Cache, tag_counter: Counter, model: str, 
                          language: str = None) -> Dict[str, Any]:
    """Classify tags using LLM and return structured result"""
    
    # Generate prompt
    prompt = create_tag_classification_prompt(tag_counter, language)
    if not prompt:
        print("Error: No frequent tags found for classification", file=sys.stderr)
        sys.exit(1)
    
    print(f"Classifying tags using model: {model}")
    print(f"Total unique tags: {len(tag_counter)}")
    print(f"Frequent tags (>=2 occurrences): {len(get_frequent_tags_with_counts(tag_counter))}")
    
    # Build schema using code-based function
    try:
        schema_dict = build_classify_schema(language=language)
        schema = build_schema_from_json(schema_dict)
        config = config_from_schema(schema)
    except Exception as e:
        print(f"Error: Cannot build schema: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
    
    # Generate classification
    response = generate_content_retry([prompt], model=model, config=config)
    
    # Parse JSON response
    classification_data = json.loads(response.text.strip())
    
    # Add language information if specified
    if language:
        classification_data['language'] = language
    
    # Handle translation if language is specified and translation is needed
    if language and needs_translation(language, cache):
        translate_report_terms(language, model, cache)
    
    return classification_data




def needs_translation(language: str, cache: Optional[Cache] = None) -> bool:
    """Check if translation is needed for the given language
    
    Args:
        language: Target language to check
        cache: Cache instance for checking existing translations
    
    Returns:
        bool: True if translation is needed, False if all terms are cached
    """
    if not cache or not cache.translation_cache:
        return True
    
    for term in TRANSLATION_TERMS:
        if not cache.translation_cache.get_translation(term, language):
            return True
    
    return False


def translate_report_terms(language: str, model: str = None, cache: Optional[Cache] = None) -> None:
    """Translate report terms to specified language and update cache
    
    Args:
        language: Target language for translation
        model: Model to use (default: first available model)
        cache: Cache instance for storing translations
    
    Returns:
        None: Translations are stored in cache
    """
    # Get missing terms to translate
    terms_to_translate = []
    if cache and cache.translation_cache:
        for term in TRANSLATION_TERMS:
            if not cache.translation_cache.get_translation(term, language):
                terms_to_translate.append(term)
    else:
        terms_to_translate = TRANSLATION_TERMS
    
    if not terms_to_translate:
        return  # All terms already cached
    
    # Translate missing terms
    translations = translate_terms(terms_to_translate, language, model)
    
    # Add to cache if available
    if cache and cache.translation_cache:
        for term, translation in translations.items():
            if term in TRANSLATION_TERMS:  # Only cache the predefined terms
                cache.translation_cache.add_translation(term, language, translation)
        cache.translation_cache.save()


def filter_url_infos_by_urls(cache: Cache, target_urls: List[str]) -> List[URLInfo]:
    """Filter URLInfo objects by target URL list"""
    if not target_urls:
        return cache.get_all()
    
    # Create lookup set for efficiency
    target_set = set(target_urls)
    
    # Filter URLInfo objects
    filtered = []
    for url_info in cache.get_all():
        if url_info.url in target_set:
            filtered.append(url_info)
    
    return filtered


