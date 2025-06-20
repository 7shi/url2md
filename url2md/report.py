#!/usr/bin/env python3
"""
Generate Markdown reports from URL analysis and classification results

Generate comprehensive reports from classification data in Markdown format.
"""

import json
import sys
import traceback
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .cache import Cache
from .urlinfo import URLInfo


def calculate_tag_match_weight(url_tag: str, theme_tag: str) -> float:
    """Calculate tag match weight
    
    Args:
        url_tag: Tag from URL summary
        theme_tag: Tag belonging to theme
    
    Returns:
        float: Match weight (exact match=1.0, partial match=ratio, no match=0.0)
    """
    # Exact match
    if url_tag == theme_tag:
        return 1.0
    
    # Partial match: check if one contains the other
    if url_tag in theme_tag:
        # url_tag is contained in theme_tag
        return len(url_tag) / len(theme_tag)
    elif theme_tag in url_tag:
        # theme_tag is contained in url_tag
        return len(theme_tag) / len(url_tag)
    
    # No match
    return 0.0


def load_url_summaries(cache: Cache, url_infos: List[URLInfo]) -> Dict[str, Dict]:
    """Load URL summary data
    
    Args:
        cache: Cache object
        url_infos: List of URLInfo objects
    
    Returns:
        Dict[str, Dict]: URL -> summary data mapping
    """
    url_summaries = {}
    skip_count = 0
    
    for url_info in url_infos:
        summary_file = cache.get_summary_path(url_info)
        if summary_file and summary_file.exists():
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
                # Skip if is_valid_content is False
                if not summary_data.get('is_valid_content', False):
                    skip_count += 1
                    continue
                url_summaries[url_info.url] = summary_data
            except Exception as e:
                print(f"Warning: Summary file read error ({url_info.url})", file=sys.stderr)
                traceback.print_exc()
    
    if skip_count > 0:
        print(f"Skipped invalid content: {skip_count} items")
    
    return url_summaries


def classify_url_to_theme(url_summary: Dict, themes: List[Dict], theme_weights: Dict[str, float] = None) -> Tuple[str, float]:
    """Classify single URL to optimal theme
    
    Args:
        url_summary: URL summary data
        themes: List of theme data
        theme_weights: Theme weight mapping
    
    Returns:
        Tuple[str, float]: (theme_name, score)
    """
    url_tags = url_summary.get('tags', [])
    if not url_tags:
        return None, 0.0
    
    best_theme = None
    best_score = 0.0
    
    for theme_data in themes:
        theme_name = theme_data['name']
        theme_tags = theme_data['tags']
        
        # Calculate theme score
        theme_score = 0.0
        for url_tag in url_tags:
            for theme_tag in theme_tags:
                match_weight = calculate_tag_match_weight(url_tag, theme_tag)
                if match_weight > 0:
                    theme_score += match_weight
        
        # Apply theme weight
        if theme_weights and theme_name in theme_weights:
            theme_score *= theme_weights[theme_name]
        
        # Update best theme
        if theme_score > best_score:
            best_score = theme_score
            best_theme = theme_name
    
    return best_theme, best_score


def classify_all_urls(url_summaries: Dict[str, Dict], classification_data: Dict, theme_weights: Dict[str, float] = None) -> Dict[str, Dict]:
    """Classify all URLs to themes
    
    Args:
        url_summaries: URL summary data
        classification_data: Classification data
        theme_weights: Optional theme weight mapping
    
    Returns:
        Dict[str, Dict]: URL -> {theme, score} mapping
    """
    # Extract themes from classification data (new schema format)
    themes_data = classification_data.get('themes', [])
    themes = []
    
    if theme_weights is None:
        theme_weights = {}
    
    for theme_info in themes_data:
        theme_name = theme_info.get('theme_name', '')
        themes.append({
            'name': theme_name,
            'tags': theme_info.get('tags', [])
        })
        # Use provided weight or default to 1.0
        if theme_name not in theme_weights:
            theme_weights[theme_name] = 1.0
    
    # Classify each URL
    url_classifications = {}
    
    for url, summary in url_summaries.items():
        theme, score = classify_url_to_theme(summary, themes, theme_weights)
        if theme:
            url_classifications[url] = {
                'theme': theme,
                'score': score
            }
    
    return url_classifications


def group_urls_by_tag_in_theme(urls_with_scores: List[Tuple[str, float]], theme_tags: List[str], 
                               url_summaries: Dict[str, Dict]) -> Dict[str, List[Tuple[str, float]]]:
    """Group URLs by their first matching tag within a theme
    
    Args:
        urls_with_scores: List of (url, score) tuples for the theme
        theme_tags: List of tags belonging to the theme
        url_summaries: URL summary data containing tags
    
    Returns:
        Dict[str, List[Tuple[str, float]]]: tag -> [(url, score), ...] mapping
    """
    tag_groups = {}
    untagged = []
    
    for url, score in urls_with_scores:
        summary = url_summaries.get(url, {})
        url_tags = summary.get('tags', [])
        
        # Find first matching tag (prioritize URL tag order)
        matched = False
        for url_tag in url_tags:
            for theme_tag in theme_tags:
                if calculate_tag_match_weight(url_tag, theme_tag) > 0:
                    if theme_tag not in tag_groups:
                        tag_groups[theme_tag] = []
                    tag_groups[theme_tag].append((url, score))
                    matched = True
                    break
            if matched:
                break
        
        if not matched:
            untagged.append((url, score))
    
    # Add untagged if any
    if untagged:
        tag_groups['_untagged'] = untagged
    
    return tag_groups


def generate_markdown_report(cache: Cache, url_classifications: Dict[str, Dict], classification_data: Dict, 
                           url_summaries: Dict[str, Dict], theme_subsections: Optional[List[str]] = None) -> str:
    """Generate Markdown format report
    
    Args:
        cache: Cache instance for translation lookup
        url_classifications: URL -> {theme, score} mapping
        classification_data: Theme classification data
        url_summaries: URL summary data
        theme_subsections: List of theme names to create subsections for
    
    Returns:
        str: Markdown report content
    """
    # Get language from classification data
    language = classification_data.get('language')
    
    # Translation helper function
    def t(term: str) -> str:
        # Use cache for translation lookup
        if cache.translation_cache and language:
            cached = cache.translation_cache.get_translation(term, language)
            if cached:
                return cached
        # Default to original term
        return term
    # Count classifications by theme
    theme_counts = Counter(classification['theme'] for classification in url_classifications.values())
    total_classified = len(url_classifications)
    total_urls = len(url_summaries)
    unclassified_count = total_urls - total_classified
    
    # Generate report
    lines = []
    lines.append(f"# {t('Summary')}")
    lines.append("")
    lines.append(f"- **{t('Total URLs')}**: {total_urls:,}")
    if total_urls > 0:
        lines.append(f"- **{t('Classified')}**: {total_classified:,} ({total_classified/total_urls*100:.1f}%)")
        lines.append(f"- **{t('Unclassified')}**: {unclassified_count:,} ({unclassified_count/total_urls*100:.1f}%)")
    else:
        lines.append(f"- **{t('Classified')}**: 0 (0.0%)")
        lines.append(f"- **{t('Unclassified')}**: 0 (0.0%)")
    lines.append("")
    
    # Theme distribution
    lines.append(f"# {t('Themes')}")
    lines.append("")
    
    themes_data = classification_data.get('themes', [])
    # Sort by count descending
    for theme_name, count in theme_counts.most_common():
        percentage = count / total_urls * 100
        lines.append(f"- **{theme_name}**: {count} {t('URLs')} ({percentage:.1f}%)")
    
    lines.append("")
    
    # Group URLs by theme
    urls_by_theme = {}
    for url, classification in url_classifications.items():
        theme = classification['theme']
        if theme not in urls_by_theme:
            urls_by_theme[theme] = []
        urls_by_theme[theme].append((url, classification['score']))
    
    # Get theme descriptions
    theme_descriptions = {}
    for theme_info in themes_data:
        theme_name = theme_info.get('theme_name', '')
        theme_descriptions[theme_name] = theme_info.get('theme_description', '')
    
    # Output each theme (sorted by count descending)
    for theme_name, count in theme_counts.most_common():
        if theme_name not in urls_by_theme:
            continue
        urls_with_scores = urls_by_theme[theme_name]
        lines.append(f"## {theme_name} ({len(urls_with_scores)} {t('URLs')})")
        lines.append("")
        
        # Add theme description if available
        if theme_name in theme_descriptions and theme_descriptions[theme_name]:
            lines.append(theme_descriptions[theme_name])
            lines.append("")
        
        # Sort by score descending
        urls_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        if theme_subsections and theme_name in theme_subsections:
            # Get theme tags
            theme_tags = []
            for theme_info in themes_data:
                if theme_info.get('theme_name', '') == theme_name:
                    theme_tags = theme_info.get('tags', [])
                    break
            
            # Group URLs by tags
            tag_groups = group_urls_by_tag_in_theme(urls_with_scores, theme_tags, url_summaries)
            
            # Output by tag subsections (preserve theme_tags order)
            for theme_tag in theme_tags:
                if theme_tag in tag_groups:
                    tag_urls = tag_groups[theme_tag]
                    lines.append(f"### {theme_tag}")
                    lines.append("")
                    
                    for url, score in tag_urls:
                        summary = url_summaries.get(url, {})
                        title = summary.get('title', [''])[0] if summary.get('title') else url
                        one_line = summary.get('summary_one_line', '')
                        
                        lines.append(f"- [{title}]({url})" + ("  " if one_line else ""))
                        if one_line:
                            lines.append(f"  {one_line}")
                        lines.append("")
            
            # Output untagged URLs if any
            if '_untagged' in tag_groups:
                lines.append(f"### {t('Other')}")
                lines.append("")
                
                for url, score in tag_groups['_untagged']:
                    summary = url_summaries.get(url, {})
                    title = summary.get('title', [''])[0] if summary.get('title') else url
                    one_line = summary.get('summary_one_line', '')
                    
                    lines.append(f"- [{title}]({url})" + ("  " if one_line else ""))
                    if one_line:
                        lines.append(f"  {one_line}")
                    lines.append("")
        else:
            # Original flat list output
            for url, score in urls_with_scores:
                summary = url_summaries.get(url, {})
                title = summary.get('title', [''])[0] if summary.get('title') else url
                one_line = summary.get('summary_one_line', '')
                
                lines.append(f"- [{title}]({url})" + ("  " if one_line else ""))
                if one_line:
                    lines.append(f"  {one_line}")
                lines.append("")
    
    # Unclassified URLs
    if unclassified_count > 0:
        lines.append(f"## {t('Unclassified')} ({unclassified_count} {t('URLs')})")
        lines.append("")
        
        classified_urls = set(url_classifications.keys())
        for url in sorted(url_summaries.keys()):
            if url not in classified_urls:
                summary = url_summaries[url]
                title = summary.get('title', [''])[0] if summary.get('title') else url
                one_line = summary.get('summary_one_line', '')
                
                lines.append(f"- [{title}]({url})" + ("  " if one_line else ""))
                if one_line:
                    lines.append(f"  {one_line}")
                lines.append("")
    
    return "\n".join(lines)


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


