#!/usr/bin/env python3
"""
url2md - URL analysis and classification tool

Generate Markdown reports from URLs through AI-powered content analysis,
summarization, and classification.
"""

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create main parser and subcommands"""
    from .gemini import default_model
    parser = argparse.ArgumentParser(
        description="url2md - URL analysis and classification tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s fetch -f urls.txt --playwright
  %(prog)s summarize -f urls.txt
  %(prog)s classify --classify -f urls.txt -o class.json
  %(prog)s report -f urls.txt -o report.md class.json
  %(prog)s pipeline urls.txt --cache-dir cache --output report.md

For more information on each command, use:
  %(prog)s <command> --help
        """
    )
    
    from . import __version__
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (show full traceback on errors)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # fetch subcommand
    fetch_parser = subparsers.add_parser('fetch', help='Fetch URLs and store in cache')
    fetch_parser.add_argument('urls', nargs='*', help='URLs to fetch (multiple allowed)')
    fetch_parser.add_argument('-f', '--file', help='URL list file (use - for stdin)')
    fetch_parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    fetch_parser.add_argument('--playwright', action='store_true', help='Use Playwright for dynamic rendering')
    fetch_parser.add_argument('--force', action='store_true', help='Force re-fetch even if cached')
    fetch_parser.add_argument('--throttle', type=int, default=5, help='Seconds between requests to same domain')
    fetch_parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    
    # summarize subcommand
    summarize_parser = subparsers.add_parser('summarize', help='Generate AI summaries of cached content')
    summarize_parser.add_argument('urls', nargs='*', help='URLs to summarize (all cached if not specified)')
    summarize_parser.add_argument('-f', '--file', help='URL list file')
    summarize_parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    summarize_parser.add_argument('--hash', help='Summarize specific hash only')
    summarize_parser.add_argument('--limit', type=int, help='Maximum number to process')
    summarize_parser.add_argument('--force', action='store_true', help='Force re-summarize existing summaries')
    summarize_parser.add_argument('--model', default=default_model, help=f'Gemini model to use (default: {default_model})')
    
    # classify subcommand
    classify_parser = subparsers.add_parser('classify', help='Analyze tags and classify with LLM')
    classify_parser.add_argument('-f', '--file', help='URL list file')
    classify_parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    classify_parser.add_argument('--extract-tags', action='store_true', help='Extract and count tags only')
    classify_parser.add_argument('--test', action='store_true', help='Show prompt only (test mode)')
    classify_parser.add_argument('--classify', action='store_true', help='Classify with LLM')
    classify_parser.add_argument('-o', '--output', help='Classification result output file')
    classify_parser.add_argument('--model', default=default_model, help=f'Gemini model to use (default: {default_model})')
    
    # report subcommand
    report_parser = subparsers.add_parser('report', help='Generate Markdown report from classification')
    report_parser.add_argument('classification_file', help='Classification result JSON file')
    report_parser.add_argument('-f', '--file', help='URL list file')
    report_parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    report_parser.add_argument('--format', choices=['markdown', 'html'], default='markdown', help='Output format')
    report_parser.add_argument('-o', '--output', help='Output file (stdout if not specified)')
    report_parser.add_argument('--theme-weight', '-t', action='append', metavar='THEME:WEIGHT',
                              help='Theme weight adjustment (e.g., -t "Theme Name:0.7")')
    
    # pipeline subcommand
    pipeline_parser = subparsers.add_parser('pipeline', help='Run complete pipeline (fetch → summarize → classify → report)')
    pipeline_parser.add_argument('urls', nargs='*', help='URLs to process (multiple allowed)')
    pipeline_parser.add_argument('-f', '--file', help='URL list file')
    pipeline_parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    pipeline_parser.add_argument('--classification-output', help='Classification result file')
    pipeline_parser.add_argument('-o', '--output', help='Final report output file')
    pipeline_parser.add_argument('--force-fetch', action='store_true', help='Force re-fetch URLs')
    pipeline_parser.add_argument('--force-summary', action='store_true', help='Force re-summarize')
    pipeline_parser.add_argument('--playwright', action='store_true', help='Use Playwright for fetch')
    pipeline_parser.add_argument('--model', default=default_model, help=f'Gemini model to use (default: {default_model})')
    
    return parser


def run_subcommand(args) -> None:
    """Execute the specified subcommand"""
    if args.command == 'fetch':
        run_fetch(args)
    elif args.command == 'summarize':
        run_summarize(args)
    elif args.command == 'classify':
        run_classify(args)
    elif args.command == 'report':
        run_report(args)
    elif args.command == 'pipeline':
        run_pipeline(args)
    else:
        raise ValueError(f"Unknown command: {args.command}")


def run_fetch(args) -> None:
    """Run fetch subcommand"""
    from .fetch import fetch_urls
    from .models import load_urls_from_file
    
    # Collect URLs
    urls = []
    
    if args.urls:
        urls.extend(args.urls)
    
    if args.file:
        file_urls = load_urls_from_file(args.file)
        urls.extend(file_urls)
    
    if not urls:
        raise ValueError("No URLs provided. Use --help for usage information.")
    
    # Remove duplicates while preserving order
    unique_urls = []
    seen = set()
    for url in urls:
        if url not in seen:
            unique_urls.append(url)
            seen.add(url)
    
    fetch_urls(
        unique_urls,
        args.cache_dir,
        use_playwright=args.playwright,
        force=args.force,
        throttle_seconds=args.throttle
    )


def run_summarize(args) -> None:
    """Run summarize subcommand"""
    from .summarize import summarize_urls, filter_url_infos_by_urls, filter_url_infos_by_hash
    from .cache import Cache
    from .models import load_urls_from_file
    
    # Check environment variable
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    cache = Cache(args.cache_dir)
    
    # Determine target URLs
    target_urls = []
    if args.urls:
        target_urls.extend(args.urls)
    
    if args.file:
        file_urls = load_urls_from_file(args.file)
        target_urls.extend(file_urls)
    
    # Filter URLInfo objects
    if args.hash:
        url_infos = filter_url_infos_by_hash(cache, args.hash)
    elif target_urls:
        url_infos = filter_url_infos_by_urls(cache, target_urls)
    else:
        url_infos = cache.get_all()
    
    summarize_urls(
        url_infos,
        cache,
        force=args.force,
        limit=args.limit,
        model=args.model
    )


def run_classify(args) -> None:
    """Run classify subcommand"""
    from .classify import extract_tags, display_tag_statistics, create_tag_classification_prompt, classify_tags_with_llm, filter_url_infos_by_urls
    from .cache import Cache
    from .models import load_urls_from_file
    
    # Check that at least one action is specified
    if not any([args.extract_tags, args.test, args.classify]):
        raise ValueError("Please specify at least one action (--extract-tags, --test, or --classify)")
    
    # Check environment variable for LLM operations
    if (args.test or args.classify) and not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    cache = Cache(args.cache_dir)
    
    # Determine target URLs
    target_urls = []
    if args.file:
        target_urls = load_urls_from_file(args.file)
    
    # Filter URLInfo objects
    url_infos = filter_url_infos_by_urls(cache, target_urls)
    
    if not url_infos:
        raise ValueError("No valid URL info found")
    
    # Extract tags
    all_tags = extract_tags(cache, url_infos)
    if not all_tags:
        raise ValueError("No tags found in summary files")
    
    # Count tags
    tag_counter = Counter(all_tags)
    
    # Execute requested actions
    if args.extract_tags:
        display_tag_statistics(tag_counter)
    
    if args.test:
        prompt = create_tag_classification_prompt(tag_counter)
        if prompt:
            print("\n=== CLASSIFICATION PROMPT ===")
            print(prompt)
        else:
            print("No frequent tags found for prompt generation")
    
    if args.classify:
        classification_result = classify_tags_with_llm(tag_counter, model=args.model)
        
        if args.output:
            # Save to file
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(classification_result, f, ensure_ascii=False, indent=2)
            print(f"Classification results saved to: {args.output}")
        else:
            # Output to stdout
            print("\n=== CLASSIFICATION RESULTS ===")
            print(json.dumps(classification_result, ensure_ascii=False, indent=2))


def run_report(args) -> None:
    """Run report subcommand"""
    from .report import classify_all_urls, generate_markdown_report, filter_url_infos_by_urls, load_url_summaries
    from .cache import Cache
    from .models import load_urls_from_file
    
    # Load classification data
    try:
        with open(args.classification_file, 'r', encoding='utf-8') as f:
            classification_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Classification file not found: {args.classification_file}")
    
    cache = Cache(args.cache_dir)
    
    # Parse theme weights
    theme_weights = {}
    if hasattr(args, 'theme_weight') and args.theme_weight:
        for weight_spec in args.theme_weight:
            try:
                theme_name, weight_str = weight_spec.rsplit(':', 1)
                weight = float(weight_str)
                theme_weights[theme_name] = weight
                print(f"Theme weight set: {theme_name} = {weight}")
            except ValueError:
                print(f"Warning: Invalid weight specification ignored: {weight_spec}", file=sys.stderr)
    
    # Determine target URLs
    target_urls = []
    if args.file:
        target_urls = load_urls_from_file(args.file)
    
    # Filter URLInfo objects
    url_infos = filter_url_infos_by_urls(cache, target_urls)
    
    if not url_infos:
        raise ValueError("No valid URL info found")
    
    # Load URL summaries
    url_summaries = load_url_summaries(cache, url_infos)
    
    if not url_summaries:
        raise ValueError("No valid URL summaries found")
    
    print(f"Processing {len(url_summaries)} URLs...")
    
    # Classify URLs
    url_classifications = classify_all_urls(url_summaries, classification_data, theme_weights)
    
    # Display classification results
    theme_counts = Counter(classification['theme'] for classification in url_classifications.values())
    print("Classification results:")
    for theme, count in theme_counts.most_common():
        print(f"  {theme}: {count} URLs")
    print(f"Classification completed: {len(url_classifications)} URLs")
    
    # Generate report
    if args.format == 'markdown':
        report_content = generate_markdown_report(url_classifications, classification_data, url_summaries)
    else:
        raise ValueError(f"Format '{args.format}' not yet implemented")
    
    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Report saved to: {args.output}")
    else:
        print(report_content)


def run_pipeline(args) -> None:
    """Run pipeline subcommand (complete workflow)"""
    print("🔄 URL analysis pipeline started")
    
    # Step 1: fetch
    print("\n📥 Step 1: URL fetching and caching")
    fetch_args = argparse.Namespace(
        urls=args.urls,
        file=args.file,
        cache_dir=args.cache_dir,
        playwright=getattr(args, 'playwright', False),
        force=getattr(args, 'force_fetch', False),
        throttle=5,
        timeout=30
    )
    run_fetch(fetch_args)
    
    # Step 2: summarize
    print("\n📝 Step 2: AI summary generation")
    summarize_args = argparse.Namespace(
        urls=args.urls if args.urls else [],
        file=args.file,
        cache_dir=args.cache_dir,
        hash=None,
        limit=None,
        force=getattr(args, 'force_summary', False),
        model=args.model
    )
    run_summarize(summarize_args)
    
    # Step 3: classify
    print("\n🏷️ Step 3: LLM tag classification")
    classification_file = getattr(args, 'classification_output', None) or f"{args.cache_dir}/classification.json"
    classify_args = argparse.Namespace(
        file=args.file,
        cache_dir=args.cache_dir,
        extract_tags=False,
        test=False,
        classify=True,
        output=classification_file,
        model=args.model
    )
    run_classify(classify_args)
    
    # Step 4: report
    print("\n📊 Step 4: Report generation")
    report_args = argparse.Namespace(
        classification_file=classification_file,
        file=args.file,
        cache_dir=args.cache_dir,
        format='markdown',
        output=args.output
    )
    run_report(report_args)
    
    print("\n✅ Pipeline completed successfully")
    if args.output:
        print(f"📄 Final report: {args.output}")


def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.debug:
        # Run subcommand without exception handling (show full traceback)
        run_subcommand(args)
        return 0
    else:
        try:
            # Run subcommand with exception handling
            run_subcommand(args)
            return 0
            
        except KeyboardInterrupt:
            print(f"\n{args.command.title()} interrupted by user")
            return 1
        except ValueError as e:
            # Handle unknown command case
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1


if __name__ == '__main__':
    sys.exit(main())
