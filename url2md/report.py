#!/usr/bin/env python3
"""
Generate Markdown reports from URL analysis and classification results

Generate comprehensive reports from classification data in Markdown format.
"""

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .cache import Cache
from .models import URLInfo


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
                print(f"Warning: Summary file read error ({url_info.url}): {e}")
    
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


def generate_markdown_report(url_classifications: Dict[str, Dict], classification_data: Dict, 
                           url_summaries: Dict[str, Dict]) -> str:
    """Generate Markdown format report
    
    Args:
        url_classifications: URL -> {theme, score} mapping
        classification_data: Theme classification data
        url_summaries: URL summary data
    
    Returns:
        str: Markdown report content
    """
    # Count classifications by theme
    theme_counts = Counter(classification['theme'] for classification in url_classifications.values())
    total_classified = len(url_classifications)
    total_urls = len(url_summaries)
    unclassified_count = total_urls - total_classified
    
    # Generate report
    lines = []
    lines.append("# URL Analysis Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total URLs**: {total_urls:,}")
    if total_urls > 0:
        lines.append(f"- **Classified**: {total_classified:,} ({total_classified/total_urls*100:.1f}%)")
        lines.append(f"- **Unclassified**: {unclassified_count:,} ({unclassified_count/total_urls*100:.1f}%)")
    else:
        lines.append("- **Classified**: 0 (0.0%)")
        lines.append("- **Unclassified**: 0 (0.0%)")
    lines.append("")
    
    # Theme distribution
    lines.append("## Theme Distribution")
    lines.append("")
    
    themes_data = classification_data.get('themes', [])
    # Sort by count descending
    for theme_name, count in theme_counts.most_common():
        percentage = count / total_urls * 100
        lines.append(f"- **{theme_name}**: {count} URLs ({percentage:.1f}%)")
    
    lines.append("")
    
    # URLs by theme
    lines.append("## URLs by Theme")
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
        lines.append(f"### {theme_name} ({len(urls_with_scores)} URLs)")
        lines.append("")
        
        # Add theme description if available
        if theme_name in theme_descriptions and theme_descriptions[theme_name]:
            lines.append(theme_descriptions[theme_name])
            lines.append("")
        
        # Sort by score descending
        urls_with_scores.sort(key=lambda x: x[1], reverse=True)
        
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
        lines.append(f"### Unclassified ({unclassified_count} URLs)")
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


