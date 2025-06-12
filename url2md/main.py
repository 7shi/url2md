#!/usr/bin/env python3
"""
url2md - URL analysis and classification tool

Generate Markdown reports from URLs through AI-powered content analysis,
summarization, and classification.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create main parser and subcommands"""
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
    
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    
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
    
    # classify subcommand
    classify_parser = subparsers.add_parser('classify', help='Analyze tags and classify with LLM')
    classify_parser.add_argument('-f', '--file', help='URL list file')
    classify_parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    classify_parser.add_argument('--extract-tags', action='store_true', help='Extract and count tags only')
    classify_parser.add_argument('--test', action='store_true', help='Show prompt only (test mode)')
    classify_parser.add_argument('--classify', action='store_true', help='Classify with LLM')
    classify_parser.add_argument('-o', '--output', help='Classification result output file')
    
    # report subcommand
    report_parser = subparsers.add_parser('report', help='Generate Markdown report from classification')
    report_parser.add_argument('classification_file', help='Classification result JSON file')
    report_parser.add_argument('-f', '--file', help='URL list file')
    report_parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    report_parser.add_argument('--format', choices=['markdown', 'html'], default='markdown', help='Output format')
    report_parser.add_argument('-o', '--output', help='Output file (stdout if not specified)')
    
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
    
    return parser


def run_fetch(args) -> int:
    """Run fetch subcommand"""
    try:
        from .fetch import main as fetch_main
        
        # Convert args to list format
        fetch_args = []
        
        if args.urls:
            fetch_args.extend(args.urls)
        
        if args.file:
            fetch_args.extend(['--file', args.file])
        
        if args.cache_dir != Path('cache'):
            fetch_args.extend(['--cache-dir', str(args.cache_dir)])
        
        if args.playwright:
            fetch_args.append('--playwright')
        
        if args.force:
            fetch_args.append('--force')
        
        if args.throttle != 5:
            fetch_args.extend(['--throttle', str(args.throttle)])
        
        if args.timeout != 30:
            fetch_args.extend(['--timeout', str(args.timeout)])
        
        return fetch_main(fetch_args)
        
    except ImportError as e:
        print(f"Error: Cannot load fetch module: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Fetch execution error: {e}", file=sys.stderr)
        return 1


def run_summarize(args) -> int:
    """Run summarize subcommand"""
    try:
        from .summarize import main as summarize_main
        
        # Convert args to list format
        summarize_args = []
        
        if args.urls:
            summarize_args.extend(args.urls)
        
        if args.file:
            summarize_args.extend(['--file', args.file])
        
        if args.cache_dir != Path('cache'):
            summarize_args.extend(['--cache-dir', str(args.cache_dir)])
        
        if args.hash:
            summarize_args.extend(['--hash', args.hash])
        
        if args.limit:
            summarize_args.extend(['--limit', str(args.limit)])
        
        if args.force:
            summarize_args.append('--force')
        
        return summarize_main(summarize_args)
        
    except ImportError as e:
        print(f"Error: Cannot load summarize module: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Summarize execution error: {e}", file=sys.stderr)
        return 1


def run_classify(args) -> int:
    """Run classify subcommand"""
    try:
        from .classify import main as classify_main
        
        # Convert args to list format
        classify_args = []
        
        if args.file:
            classify_args.extend(['-f', args.file])
        
        if args.cache_dir != Path('cache'):
            classify_args.extend(['--cache-dir', str(args.cache_dir)])
        
        if args.extract_tags:
            classify_args.append('--extract-tags')
        
        if args.test:
            classify_args.append('--test')
        
        if args.classify:
            classify_args.append('--classify')
        
        if args.output:
            classify_args.extend(['-o', args.output])
        
        return classify_main(classify_args)
        
    except ImportError as e:
        print(f"Error: Cannot load classify module: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Classify execution error: {e}", file=sys.stderr)
        return 1


def run_report(args) -> int:
    """Run report subcommand"""
    try:
        from .report import main as report_main
        
        # Convert args to list format
        report_args = [args.classification_file]
        
        if args.file:
            report_args.extend(['-f', args.file])
        
        if args.cache_dir != Path('cache'):
            report_args.extend(['--cache-dir', str(args.cache_dir)])
        
        if args.output:
            report_args.extend(['-o', args.output])
        
        return report_main(report_args)
        
    except ImportError as e:
        print(f"Error: Cannot load report module: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Report execution error: {e}", file=sys.stderr)
        return 1


def run_pipeline(args) -> int:
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
    result = run_fetch(fetch_args)
    if result != 0:
        print("❌ URL fetch failed")
        return result
    
    # Step 2: summarize
    print("\n📝 Step 2: AI summary generation")
    summarize_args = argparse.Namespace(
        urls=args.urls if args.urls else [],
        file=args.file,
        cache_dir=args.cache_dir,
        hash=None,
        limit=None,
        force=getattr(args, 'force_summary', False)
    )
    result = run_summarize(summarize_args)
    if result != 0:
        print("❌ Summary generation failed")
        return result
    
    # Step 3: classify
    print("\n🏷️ Step 3: LLM tag classification")
    classification_file = getattr(args, 'classification_output', None) or f"{args.cache_dir}/classification.json"
    classify_args = argparse.Namespace(
        file=args.file,
        cache_dir=args.cache_dir,
        extract_tags=False,
        test=False,
        classify=True,
        output=classification_file
    )
    result = run_classify(classify_args)
    if result != 0:
        print("❌ Tag classification failed")
        return result
    
    # Step 4: report
    print("\n📊 Step 4: Report generation")
    report_args = argparse.Namespace(
        classification_file=classification_file,
        file=args.file,
        cache_dir=args.cache_dir,
        format='markdown',
        output=args.output
    )
    result = run_report(report_args)
    if result != 0:
        print("❌ Report generation failed")
        return result
    
    print("\n✅ Pipeline completed successfully")
    if args.output:
        print(f"📄 Final report: {args.output}")
    return 0


def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Run subcommand
    if args.command == 'fetch':
        return run_fetch(args)
    elif args.command == 'summarize':
        return run_summarize(args)
    elif args.command == 'classify':
        return run_classify(args)
    elif args.command == 'report':
        return run_report(args)
    elif args.command == 'pipeline':
        return run_pipeline(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
