#!/usr/bin/env python3
"""
Summarize cached web content using Gemini API

Read files from cache directory, generate summaries using Gemini API, 
and save as structured JSON files in cache/summary directory.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import minify_html
from tqdm import tqdm

from .cache import Cache
from .gemini import generate_content_retry, config_from_schema, models, upload_file, delete_file
from .models import URLInfo, load_urls_from_file
from .utils import extract_body_content, extract_html_title


def generate_summary_prompt(url: str, content_type: str) -> str:
    """Generate prompt for summarization"""
    prompt_parts = [
        "Please summarize the content of this document as structured JSON.",
        "",
        f"URL: {url}",
        f"Content Type: {content_type}",
        "",
        "Summary requirements:",
        "- title: Page title (appropriate title inferred from content)",
        "- summary_one_line: Concise one-line summary within 50 characters",
        "- summary_detailed: Detailed summary of 200-400 characters (include main topics, academic/educational value, technical field)",
        "- tags: List of tags representing the content (e.g., linguistics, mathematics, physics, programming, etc.)",
        "- is_valid_content: Whether this is meaningful content (true if not error page or empty page)",
    ]
    return "\n".join(prompt_parts)


def summarize_content(cache: Cache, url_info: URLInfo, model: str = None, schema_file: str = "schemas/summarize.json") -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """Generate structured JSON summary for a single file using Gemini"""
    if model is None:
        model = models[0]  # Use default model
    
    url = url_info.url
    content_path = cache.get_content_path(url_info)
    content_type = url_info.content_type
    
    # Determine MIME type for Gemini
    mime_type = content_type or "text/plain"
    
    print(f"Generating summary: {url}")
    print(f"  File: {content_path}")
    print(f"  MIME type: {mime_type}")
    
    try:
        # Load JSON schema configuration
        config = config_from_schema(schema_file)
        
        # Generate prompt
        prompt = generate_summary_prompt(url, content_type)
        
        # For text/*, preprocess and read directly; otherwise upload
        uploaded_file = None
        html_title = None  # Store HTML title
        
        if content_type.startswith("text/"):
            # Read text file
            with open(content_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Preprocess based on whether it's HTML
            if content_type == "text/html":
                # Minify
                content = minify_html.minify(content, remove_processing_instructions=True)

                # Extract HTML title
                html_title = extract_html_title(content)
                if html_title:
                    print(f"  HTML title: {html_title}")
                
                # For HTML, extract body and remove script/style
                content = extract_body_content(content).strip()
            
            # Character limit (300,000 characters)
            original_char_count = len(content)
            print(f"  Character count: {original_char_count:,} characters")
            if original_char_count > 300_000:
                content = content[:300_000]
                print(f"  Truncated to 300,000 character limit")
            
            # Create content (as text)
            contents = [content, prompt] if content else [prompt]
            
        elif content_type == "image/gif":
            # Convert GIF files to PNG and send with from_bytes
            try:
                from PIL import Image
                import io
                from google.genai import types
                
                # Read GIF file
                with Image.open(content_path) as img:
                    # Get first frame (for animated GIFs)
                    if hasattr(img, 'is_animated') and img.is_animated:
                        img.seek(0)  # First frame
                    
                    # Convert to RGBA mode (transparency support)
                    if img.mode != 'RGBA':
                        rgba_img = img.convert('RGBA')
                        img.close()  # Explicitly close original Image object
                        img = rgba_img
                    
                    # Convert to PNG in memory
                    with io.BytesIO() as png_buffer:
                        img.save(png_buffer, format='PNG')
                        png_data = png_buffer.getvalue()
                
                print(f"  GIF→PNG conversion complete (in memory): {len(png_data)} bytes")
                
                # Use from_bytes with PNG format
                png_part = types.Part.from_bytes(
                    data=png_data,
                    mime_type="image/png"
                )
                
                contents = [png_part, prompt]
                    
            except Exception as e:
                print(f"  GIF conversion error: {e}")
                # Use original GIF file if conversion fails
                uploaded_file = upload_file(str(content_path), mime_type)
                contents = [uploaded_file, prompt]
                
        else:
            # Upload binary files (PDF, etc.)
            uploaded_file = upload_file(str(content_path), mime_type)
            
            # Create content
            contents = [uploaded_file, prompt]
        
        try:
            # Generate structured JSON summary
            response = generate_content_retry(model, config, contents)
            
            # Parse JSON
            try:
                summary_data = json.loads(response.strip())
                
                # Convert title to list format
                if 'title' in summary_data:
                    gemini_title = summary_data['title']
                    title_list = [gemini_title]
                    
                    # Insert HTML title at the beginning if available
                    if html_title:
                        title_list.insert(0, html_title)
                    
                    summary_data['title'] = title_list
                
                return True, summary_data, None
            except json.JSONDecodeError as e:
                error_msg = f"JSON parsing error: {e}"
                print(f"  {error_msg}")
                print(f"  Response: {response[:200]}...")
                return False, {}, error_msg
            
        finally:
            # Clean up uploaded file if exists
            if uploaded_file:
                try:
                    delete_file(uploaded_file)
                except Exception as e:
                    print(f"  Warning: Failed to delete uploaded file: {e}")
        
    except Exception as e:
        error_msg = f"Summary generation error: {e}"
        print(f"  {error_msg}")
        return False, {}, error_msg


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


def filter_url_infos_by_hash(cache: Cache, target_hash: str) -> List[URLInfo]:
    """Filter URLInfo objects by specific hash"""
    filtered = []
    for url_info in cache.get_all():
        if url_info.hash == target_hash:
            filtered.append(url_info)
    
    return filtered


def summarize_urls(url_infos: List[URLInfo], cache: Cache, force: bool = False, 
                  limit: Optional[int] = None, model: str = None) -> None:
    """
    Summarize multiple URLs
    
    Args:
        url_infos: List of URLInfo objects to summarize
        cache: Cache object
        force: Force re-summarization of existing summaries
        limit: Maximum number to process
        model: Gemini model to use
    """
    if not url_infos:
        print("No URLs to summarize")
        return
    
    # Filter successfully cached URLs only
    valid_url_infos = []
    for url_info in url_infos:
        if url_info.status == 'success' and url_info.filename:
            content_path = cache.get_content_path(url_info)
            if content_path.exists():
                valid_url_infos.append(url_info)
            else:
                print(f"⚠️  File not found: {content_path} (URL: {url_info.url})")
        else:
            print(f"⚠️  Skipping failed URL: {url_info.url} (status: {url_info.status})")
    
    if not valid_url_infos:
        print("No valid cached URLs found")
        return
    
    # Filter URLs that need summarization
    urls_to_summarize = []
    for url_info in valid_url_infos:
        summary_path = cache.get_summary_path(url_info)
        if force or not summary_path or not summary_path.exists():
            urls_to_summarize.append(url_info)
        else:
            print(f"⏭️  Skipping already summarized: {url_info.url}")
    
    if not urls_to_summarize:
        print("All URLs already summarized")
        return
    
    # Apply limit
    if limit and len(urls_to_summarize) > limit:
        urls_to_summarize = urls_to_summarize[:limit]
        print(f"Limited to {limit} URLs for processing")
    
    print(f"Summarizing {len(urls_to_summarize)} URLs...")
    
    # Process with progress bar
    success_count = 0
    error_count = 0
    
    with tqdm(total=len(urls_to_summarize), desc="Summarizing") as pbar:
        for url_info in urls_to_summarize:
            pbar.set_description(f"Summarizing: {url_info.url[:50]}...")
            
            success, summary_data, error = summarize_content(cache, url_info, model=model)
            
            if success:
                # Save summary to JSON file
                summary_path = cache.get_summary_path(url_info)
                if summary_path:
                    summary_path.parent.mkdir(exist_ok=True)
                    with open(summary_path, 'w', encoding='utf-8') as f:
                        json.dump(summary_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ Summary saved: {summary_path}")
                    success_count += 1
                    pbar.set_postfix(status="✅ Success")
                else:
                    print(f"❌ Could not determine summary path for: {url_info.url}")
                    error_count += 1
                    pbar.set_postfix(status="❌ Path Error")
            else:
                print(f"❌ Summary failed: {url_info.url}")
                if error:
                    print(f"   Error: {error}")
                error_count += 1
                pbar.set_postfix(status="❌ Error")
            
            pbar.update(1)
    
    print(f"\n=== Summary Statistics ===")
    print(f"Total processed: {len(urls_to_summarize)}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")


def main(args: List[str] = None) -> int:
    """Main function for summarize command"""
    parser = argparse.ArgumentParser(
        description="Generate AI summaries of cached content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                               # Summarize all cached files
  %(prog)s --hash 754e3a872575fdcef3    # Summarize specific hash only
  %(prog)s --limit 5                    # Maximum 5 files (skips don't count)
  %(prog)s --cache-dir custom_cache     # Custom cache directory
  %(prog)s --force                      # Overwrite existing summaries
  %(prog)s "https://example.com"        # Summarize single URL
  %(prog)s "https://example1.com" "https://example2.com"  # Multiple URLs
  %(prog)s --file urls.txt              # Specify targets from URL file
        """
    )
    
    parser.add_argument('urls', nargs='*', help='URLs to summarize (all cached if not specified)')
    parser.add_argument('-f', '--file', help='URL list file')
    parser.add_argument('--cache-dir', type=Path, default=Path('cache'), help='Cache directory')
    parser.add_argument('--hash', help='Summarize specific hash only')
    parser.add_argument('--limit', type=int, help='Maximum number to process')
    parser.add_argument('--force', action='store_true', help='Force re-summarize existing summaries')
    parser.add_argument('--model', choices=models, help=f'Gemini model to use (default: {models[0]})')
    
    parsed_args = parser.parse_args(args)
    
    # Check environment variable
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        return 1
    
    cache = Cache(parsed_args.cache_dir)
    
    # Determine target URLs
    target_urls = []
    if parsed_args.urls:
        target_urls.extend(parsed_args.urls)
    
    if parsed_args.file:
        try:
            file_urls = load_urls_from_file(parsed_args.file)
            target_urls.extend(file_urls)
        except Exception as e:
            print(f"Error loading URLs from file: {e}", file=sys.stderr)
            return 1
    
    # Filter URLInfo objects
    if parsed_args.hash:
        url_infos = filter_url_infos_by_hash(cache, parsed_args.hash)
    elif target_urls:
        url_infos = filter_url_infos_by_urls(cache, target_urls)
    else:
        url_infos = cache.get_all()
    
    try:
        summarize_urls(
            url_infos,
            cache,
            force=parsed_args.force,
            limit=parsed_args.limit,
            model=parsed_args.model
        )
        return 0
    except KeyboardInterrupt:
        print("\nSummarization interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())