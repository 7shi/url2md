#!/usr/bin/env python3
"""
Extract and analyze tags from cache/summary/, classify with LLM

Extract all tags from summary files, aggregate them, and classify by theme using LLM.
"""

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any

from .cache import Cache
from .gemini import generate_content_retry, config_from_schema, models
from .models import URLInfo, load_urls_from_file


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
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            tags = summary_data.get('tags', [])
            if isinstance(tags, list):
                all_tags.extend(tags)
            elif isinstance(tags, str):
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                all_tags.extend(tag_list)
    
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


def create_tag_classification_prompt(tag_counter: Counter) -> str:
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
    
    return prompt


def classify_tags_with_llm(tag_counter: Counter, model: str = None, 
                          schema_file: str = "schemas/classify.json") -> Dict[str, Any]:
    """Classify tags using LLM and return structured result"""
    if model is None:
        model = models[0]  # Use default model
    
    # Generate prompt
    prompt = create_tag_classification_prompt(tag_counter)
    if not prompt:
        raise ValueError("No frequent tags found for classification")
    
    print(f"Classifying tags using model: {model}")
    print(f"Total unique tags: {len(tag_counter)}")
    print(f"Frequent tags (>=2 occurrences): {len(get_frequent_tags_with_counts(tag_counter))}")
    
    # Load JSON schema configuration
    config = config_from_schema(schema_file)
    
    # Generate classification
    response = generate_content_retry(model, config, [prompt])
    
    # Parse JSON response
    try:
        classification_data = json.loads(response.strip())
        
        # Add original tag statistics
        classification_data["tag_stats"] = dict(tag_counter.most_common())
        
        return classification_data
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parsing error: {e}. Response: {response[:200]}...")


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
    """Main function for classify command"""
    parser = argparse.ArgumentParser(
        description="Analyze tags and classify with LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --extract-tags    # Extract and count tags only
  %(prog)s --test            # Show prompt only (test mode)
  %(prog)s --classify        # Classify with LLM
  %(prog)s --classify -o result.json  # Save classification results to file
  %(prog)s --classify -f urls.txt -o result.json  # Specify targets from URL file
        """
    )
    
    parser.add_argument('-f', '--file', help='URL list file')
    parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    parser.add_argument('--extract-tags', action='store_true', help='Extract and count tags only')
    parser.add_argument('--test', action='store_true', help='Show prompt only (test mode)')
    parser.add_argument('--classify', action='store_true', help='Classify with LLM')
    parser.add_argument('-o', '--output', help='Classification result output file')
    parser.add_argument('--model', choices=models, help=f'Gemini model to use (default: {models[0]})')
    
    parsed_args = parser.parse_args(args)
    
    # Check that at least one action is specified
    if not any([parsed_args.extract_tags, parsed_args.test, parsed_args.classify]):
        print("Error: Please specify at least one action (--extract-tags, --test, or --classify)", file=sys.stderr)
        return 1
    
    # Check environment variable for LLM operations
    if (parsed_args.test or parsed_args.classify) and not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
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
    
    # Extract tags
    all_tags = extract_tags(cache, url_infos)
    if not all_tags:
        print("No tags found in summary files")
        return 1
    
    # Count tags
    tag_counter = Counter(all_tags)
    
    # Execute requested actions
    try:
        if parsed_args.extract_tags:
            display_tag_statistics(tag_counter)
        
        if parsed_args.test:
            prompt = create_tag_classification_prompt(tag_counter)
            if prompt:
                print("\n=== CLASSIFICATION PROMPT ===")
                print(prompt)
            else:
                print("No frequent tags found for prompt generation")
        
        if parsed_args.classify:
            classification_result = classify_tags_with_llm(tag_counter, model=parsed_args.model)
            
            if parsed_args.output:
                # Save to file
                with open(parsed_args.output, 'w', encoding='utf-8') as f:
                    json.dump(classification_result, f, ensure_ascii=False, indent=2)
                print(f"Classification results saved to: {parsed_args.output}")
            else:
                # Output to stdout
                print("\n=== CLASSIFICATION RESULTS ===")
                print(json.dumps(classification_result, ensure_ascii=False, indent=2))
        
        return 0
        
    except KeyboardInterrupt:
        print("\nClassification interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())