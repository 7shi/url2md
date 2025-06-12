#!/usr/bin/env python3
"""
Generate Markdown reports from URL analysis and classification results

Generate comprehensive reports from classification data in Markdown format.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .cache import Cache
from .models import URLInfo, load_urls_from_file


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


def classify_all_urls(url_summaries: Dict[str, Dict], classification_data: Dict) -> Dict[str, str]:
    """Classify all URLs to themes
    
    Args:
        url_summaries: URL summary data
        classification_data: Classification data
    
    Returns:
        Dict[str, str]: URL -> theme_name mapping
    """
    # Extract themes and weights from classification data
    themes_data = classification_data.get('themes', {})
    themes = []
    theme_weights = {}
    
    for theme_name, theme_info in themes_data.items():
        themes.append({
            'name': theme_name,
            'tags': theme_info.get('tags', [])
        })
        theme_weights[theme_name] = theme_info.get('weight', 1.0)
    
    # Classify each URL
    url_classifications = {}
    
    for url, summary in url_summaries.items():
        theme, score = classify_url_to_theme(summary, themes, theme_weights)
        if theme:
            url_classifications[url] = theme
    
    return url_classifications


def generate_markdown_report(url_classifications: Dict[str, str], classification_data: Dict, 
                           url_summaries: Dict[str, Dict]) -> str:
    """Generate Markdown format report
    
    Args:
        url_classifications: URL -> theme mapping
        classification_data: Theme classification data
        url_summaries: URL summary data
    
    Returns:
        str: Markdown report content
    """
    # Count classifications by theme
    theme_counts = Counter(url_classifications.values())
    total_classified = len(url_classifications)
    total_urls = len(url_summaries)
    unclassified_count = total_urls - total_classified
    
    # Generate report
    lines = []
    lines.append("# URL Analysis Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total URLs**: {total_urls}")
    lines.append(f"- **Classified**: {total_classified} ({total_classified/total_urls*100:.1f}%)")
    lines.append(f"- **Unclassified**: {unclassified_count} ({unclassified_count/total_urls*100:.1f}%)")
    lines.append("")
    
    # Theme distribution
    lines.append("## Theme Distribution")
    lines.append("")
    
    themes_data = classification_data.get('themes', {})
    for theme_name in sorted(themes_data.keys()):
        count = theme_counts.get(theme_name, 0)
        if count > 0:
            percentage = count / total_urls * 100
            lines.append(f"- **{theme_name}**: {count} URLs ({percentage:.1f}%)")
    
    lines.append("")
    
    # URLs by theme
    lines.append("## URLs by Theme")
    lines.append("")
    
    # Group URLs by theme
    urls_by_theme = {}
    for url, theme in url_classifications.items():
        if theme not in urls_by_theme:
            urls_by_theme[theme] = []
        urls_by_theme[theme].append(url)
    
    # Output each theme
    for theme_name in sorted(urls_by_theme.keys()):
        urls = urls_by_theme[theme_name]
        lines.append(f"### {theme_name} ({len(urls)} URLs)")
        lines.append("")
        
        for url in sorted(urls):
            summary = url_summaries.get(url, {})
            title = summary.get('title', [''])[0] if summary.get('title') else url
            one_line = summary.get('summary_one_line', '')
            
            lines.append(f"- [{title}]({url})")
            if one_line:
                lines.append(f"  - {one_line}")
        
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
                
                lines.append(f"- [{title}]({url})")
                if one_line:
                    lines.append(f"  - {one_line}")
        
        lines.append("")
    
    # Theme definitions
    lines.append("## Theme Definitions")
    lines.append("")
    
    for theme_name, theme_info in themes_data.items():
        tags = theme_info.get('tags', [])
        weight = theme_info.get('weight', 1.0)
        
        lines.append(f"### {theme_name}")
        lines.append("")
        lines.append(f"- **Weight**: {weight}")
        lines.append(f"- **Tags**: {', '.join(tags)}")
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


def main(args: List[str] = None) -> int:
    """Main function for report command"""
    parser = argparse.ArgumentParser(
        description="Generate Markdown report from classification results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s classification.json -f urls.txt    # Generate report for specific URLs
  %(prog)s classification.json               # Generate report for all cached URLs
  %(prog)s classification.json -o report.md  # Save report to file
        """
    )
    
    parser.add_argument('classification_file', help='Classification result JSON file')
    parser.add_argument('-f', '--file', help='URL list file')
    parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    parser.add_argument('--format', choices=['markdown', 'html'], default='markdown', help='Output format')
    parser.add_argument('-o', '--output', help='Output file (stdout if not specified)')
    
    parsed_args = parser.parse_args(args)
    
    # Load classification data
    try:
        with open(parsed_args.classification_file, 'r', encoding='utf-8') as f:
            classification_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Classification file not found: {parsed_args.classification_file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error loading classification file: {e}", file=sys.stderr)
        return 1
    
    cache = Cache(parsed_args.cache_dir)
    
    # Determine target URLs
    target_urls = []
    if parsed_args.file:
        try:
            target_urls = load_urls_from_file(parsed_args.file)
        except Exception as e:
            print(f"Error loading URLs from file: {e}", file=sys.stderr)
            return 1
    
    # Filter URLInfo objects
    url_infos = filter_url_infos_by_urls(cache, target_urls)
    
    if not url_infos:
        print("No valid URL info found")
        return 1
    
    # Load URL summaries
    url_summaries = load_url_summaries(cache, url_infos)
    
    if not url_summaries:
        print("No valid URL summaries found")
        return 1
    
    print(f"Processing {len(url_summaries)} URLs...")
    
    try:
        # Classify URLs
        url_classifications = classify_all_urls(url_summaries, classification_data)
        
        # Generate report
        if parsed_args.format == 'markdown':
            report_content = generate_markdown_report(url_classifications, classification_data, url_summaries)
        else:
            print(f"Error: Format '{parsed_args.format}' not yet implemented", file=sys.stderr)
            return 1
        
        # Output report
        if parsed_args.output:
            with open(parsed_args.output, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Report saved to: {parsed_args.output}")
        else:
            print(report_content)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())