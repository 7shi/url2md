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

from .cache import Cache
from .urlinfo import URLInfo, load_urls_from_file
from .utils import DEFAULT_CACHE_DIR, find_cache_dir, print_error_with_line


def create_parser() -> argparse.ArgumentParser:
    """Create main parser and subcommands"""
    from .gemini import default_model
    
    parser = argparse.ArgumentParser(
        description="url2md - URL analysis and classification tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Initialize cache directory (required first step, creates {DEFAULT_CACHE_DIR}/)
  %(prog)s init

  # Step-by-step workflow
  %(prog)s fetch -u urls.txt --playwright
  %(prog)s summarize -u urls.txt
  %(prog)s classify -u urls.txt -o class.json
  %(prog)s report -u urls.txt -c class.json -o report.md

  # Complete workflow in one command (fetch → summarize → classify → report)
  %(prog)s workflow -u urls.txt --playwright -c class.json -o report.md

For more information on each command, use:
  %(prog)s <command> --help
        """
    )
    
    from . import __version__
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--cache-dir', type=Path, help='Cache directory (auto-detected from parent dirs if not specified)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # init subcommand
    init_parser = subparsers.add_parser('init', help='Initialize cache directory')
    init_parser.add_argument('directory', nargs='?', default=None, help=f'Cache directory name (default: {DEFAULT_CACHE_DIR})')
    
    # fetch subcommand
    fetch_parser = subparsers.add_parser('fetch', help='Fetch URLs and store in cache')
    fetch_parser.add_argument('urls', nargs='*', help='URLs to fetch (multiple allowed)')
    fetch_parser.add_argument('-u', '--urls-file', dest='file', help='URL list file (use - for stdin)')
    fetch_parser.add_argument('--playwright', action='store_true', help='Use Playwright for dynamic rendering')
    fetch_parser.add_argument('--force', action='store_true', help='Force re-fetch even if cached')
    fetch_parser.add_argument('-r', '--retry', action='store_true', help='Retry failed URLs (default: skip errors)')
    fetch_parser.add_argument('--throttle', type=int, default=5, help='Seconds between requests to same domain')
    fetch_parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    
    # summarize subcommand
    summarize_parser = subparsers.add_parser('summarize', help='Generate AI summaries of cached content')
    summarize_parser.add_argument('urls', nargs='*', help='URLs to summarize (all cached if not specified)')
    summarize_parser.add_argument('-u', '--urls-file', dest='file', help='URL list file')
    summarize_parser.add_argument('--hash', help='Summarize specific hash only')
    summarize_parser.add_argument('--limit', type=int, help='Maximum number to process')
    summarize_parser.add_argument('--force', action='store_true', help='Force re-summarize existing summaries')
    summarize_parser.add_argument('--model', default=default_model, help=f'Gemini model to use (default: {default_model})')
    summarize_parser.add_argument('-l', '--language', help='Output language (e.g., Japanese, Chinese, French)')
    
    # classify subcommand
    classify_parser = subparsers.add_parser('classify', help='Analyze tags and classify with LLM')
    classify_parser.add_argument('urls', nargs='*', help='URLs to classify (all cached if not specified)')
    classify_parser.add_argument('-u', '--urls-file', dest='file', help='URL list file')
    classify_parser.add_argument('--extract-tags', action='store_true', help='Extract and count tags only (no classification)')
    classify_parser.add_argument('--show-prompt', action='store_true', help='Show classification prompt only (no LLM call)')
    classify_parser.add_argument('-o', '--output', help='Classification result output file (required for classification)')
    classify_parser.add_argument('--model', default=default_model, help=f'Gemini model to use (default: {default_model})')
    classify_parser.add_argument('-l', '--language', help='Output language (e.g., Japanese, Chinese, French)')
    
    # report subcommand
    report_parser = subparsers.add_parser('report', help='Generate Markdown report from classification')
    report_parser.add_argument('urls', nargs='*', help='URLs to include in report (all classified if not specified)')
    report_parser.add_argument('-u', '--urls-file', dest='file', help='URL list file')
    report_parser.add_argument('-c', '--class', dest='classification', required=True, help='Classification result JSON file')
    report_parser.add_argument('--format', choices=['markdown', 'html'], default='markdown', help='Output format')
    report_parser.add_argument('-o', '--output', help='Output file (stdout if not specified)')
    report_parser.add_argument('-t', '--theme-weight', action='append', metavar='THEME:WEIGHT',
                              help='Theme weight adjustment (e.g., -t "Theme Name:0.7"). Add $ suffix to create subsections (e.g., -t "Theme Name:1.5$")')
    report_parser.add_argument('-T', '--theme-weight-file', help='File containing theme weights (one per line)')
    
    # workflow subcommand
    workflow_parser = subparsers.add_parser('workflow', help='Run complete workflow (fetch → summarize → classify → report)')
    workflow_parser.add_argument('urls', nargs='*', help='URLs to process (multiple allowed)')
    workflow_parser.add_argument('-u', '--urls-file', dest='file', help='URL list file')
    workflow_parser.add_argument('-c', '--class', dest='classification', required=True, help='Classification result file (input/output)')
    workflow_parser.add_argument('-o', '--output', help='Final report output file')
    workflow_parser.add_argument('--force-fetch', action='store_true', help='Force re-fetch URLs')
    workflow_parser.add_argument('--force-summary', action='store_true', help='Force re-summarize')
    workflow_parser.add_argument('--playwright', action='store_true', help='Use Playwright for fetch')
    workflow_parser.add_argument('--model', default=default_model, help=f'Gemini model to use (default: {default_model})')
    workflow_parser.add_argument('-t', '--theme-weight', action='append', metavar='THEME:WEIGHT',
                              help='Theme weight adjustment (e.g., -t "Theme Name:0.7"). Add $ suffix to create subsections (e.g., -t "Theme Name:1.5$")')
    workflow_parser.add_argument('-T', '--theme-weight-file', help='File containing theme weights (one per line)')
    workflow_parser.add_argument('-l', '--language', help='Output language (e.g., Japanese, Chinese, French)')
    
    return parser


def run_subcommand(args) -> None:
    """Execute the specified subcommand"""
    if args.command == 'init':
        run_init(args)
    elif args.command == 'fetch':
        run_fetch(args)
    elif args.command == 'summarize':
        run_summarize(args)
    elif args.command == 'classify':
        run_classify(args)
    elif args.command == 'report':
        run_report(args)
    elif args.command == 'workflow':
        run_workflow(args)
    else:
        raise ValueError(f"Unknown command: {args.command}")


def run_init(args) -> None:
    """Run init subcommand"""
    
    # Check for conflicting directory specifications
    if args.cache_dir and args.directory:
        raise ValueError("Cannot specify both --cache-dir and directory argument for init command")
    
    # Determine cache directory
    if args.cache_dir:
        cache_dir = args.cache_dir
    elif args.directory:
        cache_dir = Path(args.directory)
    else:
        cache_dir = Path(DEFAULT_CACHE_DIR)
    
    # Check if cache already exists
    cache_tsv = cache_dir / "cache.tsv"
    if cache_tsv.exists():
        raise ValueError(f"Cache already exists: {cache_dir}")
    
    # Create cache directory
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (cache_dir / "content").mkdir(exist_ok=True)
    (cache_dir / "summary").mkdir(exist_ok=True)
    
    # Initialize cache and create cache.tsv
    cache = Cache(cache_dir)
    cache.save()  # Create empty cache.tsv file
    
    print(f"Initialized cache directory: {cache_dir}")


def run_fetch(args) -> None:
    """Run fetch subcommand"""
    from .fetch import fetch_urls
    
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
        retry=args.retry,
        throttle_seconds=args.throttle
    )


def run_summarize(args) -> None:
    """Run summarize subcommand"""
    from .summarize import summarize_urls, filter_url_infos_by_urls, filter_url_infos_by_hash
    
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
        model=args.model,
        language=args.language
    )


def run_classify(args) -> None:
    """Run classify subcommand"""
    from .classify import extract_tags, display_tag_statistics, create_tag_classification_prompt, classify_tags_with_llm, filter_url_infos_by_urls
    
    # Default action is classification unless --extract-tags or --show-prompt is specified
    perform_classification = not (args.extract_tags or args.show_prompt)
    
    # Check output file requirement for classification
    if perform_classification and not args.output:
        raise ValueError("Output file (-o/--output) is required when performing classification")
    
    # Check environment variable for LLM operations
    if perform_classification and not os.environ.get("GEMINI_API_KEY"):
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
    
    if args.show_prompt:
        prompt = create_tag_classification_prompt(tag_counter, language=args.language)
        if prompt:
            print("\n=== CLASSIFICATION PROMPT ===")
            print(prompt)
        else:
            print("No frequent tags found for prompt generation")
    
    if perform_classification:
        classification_result = classify_tags_with_llm(tag_counter, model=args.model, language=args.language)
        
        # Save to file
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(classification_result, f, ensure_ascii=False, indent=2)
            print(f"Classification results saved to: {args.output}")
        except Exception as e:
            print_error_with_line("Error", e)
            print(f"Cannot write to file '{args.output}'", file=sys.stderr)


def run_report(args) -> None:
    """Run report subcommand"""
    from .report import classify_all_urls, generate_markdown_report, filter_url_infos_by_urls, load_url_summaries
    
    # Load classification data
    try:
        with open(args.classification, 'r', encoding='utf-8') as f:
            classification_data = json.load(f)
    except Exception as e:
        print_error_with_line("Error", e)
        print(f"Cannot open file '{args.classification}'", file=sys.stderr)
        sys.exit(1)
    
    cache = Cache(args.cache_dir)
    
    # Parse theme weights and subsections
    theme_weights = {}
    theme_subsections = []
    
    # First, load from file if specified
    if hasattr(args, 'theme_weight_file') and args.theme_weight_file:
        try:
            with open(args.theme_weight_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    try:
                        theme_name, weight_str = line.rsplit(':', 1)
                        # Check for subsection marker
                        if weight_str.endswith('$'):
                            weight = float(weight_str[:-1])
                            theme_subsections.append(theme_name)
                        else:
                            weight = float(weight_str)
                        theme_weights[theme_name] = weight
                        print(f"Theme weight set from file: {theme_name} = {weight}" + (" (with subsections)" if theme_name in theme_subsections else ""))
                    except ValueError as e:
                        print(f"Error: Invalid weight specification in {args.theme_weight_file}:{line_num}: {line}", file=sys.stderr)
                        sys.exit(1)
        except FileNotFoundError:
            print(f"Error: Theme weight file not found: {args.theme_weight_file}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print_error_with_line("Error reading theme weight file", e)
            sys.exit(1)
    
    # Then, process command-line theme weights (these can override file settings)
    if hasattr(args, 'theme_weight') and args.theme_weight:
        for weight_spec in args.theme_weight:
            try:
                theme_name, weight_str = weight_spec.rsplit(':', 1)
                # Check for subsection marker
                if weight_str.endswith('$'):
                    weight = float(weight_str[:-1])
                    if theme_name not in theme_subsections:
                        theme_subsections.append(theme_name)
                else:
                    weight = float(weight_str)
                    # Remove from subsections if it was set in file
                    if theme_name in theme_subsections and not weight_str.endswith('$'):
                        theme_subsections.remove(theme_name)
                theme_weights[theme_name] = weight
                print(f"Theme weight set: {theme_name} = {weight}" + (" (with subsections)" if theme_name in theme_subsections else ""))
            except ValueError as e:
                print(f"Error: Invalid weight specification: {weight_spec}", file=sys.stderr)
                sys.exit(1)
    
    # Determine target URLs
    target_urls = []
    if args.urls:
        target_urls.extend(args.urls)
    
    if args.file:
        file_urls = load_urls_from_file(args.file)
        target_urls.extend(file_urls)
    
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
        subsection_marker = " (subsection)" if theme in theme_subsections else ""
        print(f"  {theme}: {count} URLs{subsection_marker}")
    print(f"Classification completed: {len(url_classifications)} URLs")
    
    # Generate report
    if args.format == 'markdown':
        report_content = generate_markdown_report(url_classifications, classification_data, url_summaries,
                                                theme_subsections=theme_subsections)
    else:
        raise ValueError(f"Format '{args.format}' not yet implemented")
    
    # Output report
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Report saved to: {args.output}")
        except Exception as e:
            print_error_with_line("Error", e)
            print(f"Cannot write to file '{args.output}'", file=sys.stderr)
    else:
        print(report_content)


def run_workflow(args) -> None:
    """Run workflow subcommand (complete workflow)"""
    # Check environment variable upfront
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    print("🔄 URL analysis workflow started")
    
    # Step 1: fetch
    print("\n📥 Step 1: URL fetching and caching")
    fetch_args = argparse.Namespace(
        urls=args.urls,
        file=args.file,
        cache_dir=args.cache_dir,
        playwright=getattr(args, 'playwright', False),
        force=getattr(args, 'force_fetch', False),
        retry=False,
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
        model=args.model,
        language=args.language
    )
    run_summarize(summarize_args)
    
    # Step 3: classify
    classification_file = args.classification
    
    if Path(classification_file).exists():
        print(f"\n🏷️ Step 3: LLM tag classification (skipped - {classification_file} exists)")
    else:
        print("\n🏷️ Step 3: LLM tag classification")
        classify_args = argparse.Namespace(
            urls=args.urls if args.urls else [],
            file=args.file,
            cache_dir=args.cache_dir,
            extract_tags=False,
            show_prompt=False,
            output=classification_file,
            model=args.model,
            language=args.language
        )
        run_classify(classify_args)
    
    # Step 4: report
    print("\n📊 Step 4: Report generation")
    report_args = argparse.Namespace(
        urls=args.urls if args.urls else [],
        classification=classification_file,
        file=args.file,
        cache_dir=args.cache_dir,
        format='markdown',
        output=args.output,
        theme_weight=getattr(args, 'theme_weight', None),
        theme_weight_file=getattr(args, 'theme_weight_file', None)
    )
    run_report(report_args)
    
    print("\n✅ Workflow completed successfully")
    if args.output:
        print(f"📄 Final report: {args.output}")


def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Set cache_dir if not provided (except for init command)
    if not args.cache_dir and args.command != 'init':
        try:
            args.cache_dir = find_cache_dir()
        except ValueError as e:
            print_error_with_line("Error", e)
            return 1
    
    # Run subcommand - let errors propagate for debugging
    run_subcommand(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
