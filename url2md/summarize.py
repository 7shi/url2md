#!/usr/bin/env python3
"""
Summarize cached web content using Gemini API

Read files from cache directory, generate summaries using Gemini API, 
and save as structured JSON files in cache/summary directory.
"""

import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import minify_html
from tqdm import tqdm

from .cache import Cache
from llm7shi import generate_content_retry, config_from_schema, config_from_schema_string, upload_file, delete_file
from .urlinfo import URLInfo
from .utils import extract_body_content, extract_html_title, get_resource_path


def generate_summary_prompt(url: str, content_type: str, language: str = None) -> str:
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
    
    if language:
        prompt_parts.append("")
        prompt_parts.append(f"IMPORTANT: Output all text content (title, summaries, tags) in {language}.")
    
    return "\n".join(prompt_parts)


def summarize_content(cache: Cache, url_info: URLInfo, model: str, schema_file: str = None, language: str = None) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """Generate structured JSON summary for a single file using Gemini"""
    
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
        if schema_file is None:
            schema_path = get_resource_path("schemas/summarize.json")
        else:
            schema_path = schema_file
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_content = f.read()
            
            # Replace { in language} placeholder with actual language or empty string
            if language:
                schema_content = schema_content.replace('{ in language}', f' in {language}')
            else:
                schema_content = schema_content.replace('{ in language}', '')
            
            config = config_from_schema_string(schema_content)
        except Exception as e:
            print(f"Error: Cannot open schema file: {schema_path}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)
        
        # Generate prompt
        prompt = generate_summary_prompt(url, content_type, language)
        
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
                error_msg = "JSON parsing error"
                print(f"  {error_msg}", file=sys.stderr)
                traceback.print_exc()
                print(f"  Response: {response[:200]}...")
                return False, {}, f"{error_msg}: {e}"
            
        finally:
            # Clean up uploaded file if exists
            if uploaded_file:
                try:
                    delete_file(uploaded_file)
                except Exception as e:
                    print("  Warning: Failed to delete uploaded file", file=sys.stderr)
                    traceback.print_exc()
        
    except Exception as e:
        error_msg = "Summary generation error"
        print(f"  {error_msg}", file=sys.stderr)
        traceback.print_exc()
        return False, {}, f"{error_msg}: {e}"


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
                  limit: Optional[int] = None, model: str = None, language: str = None) -> None:
    """
    Summarize multiple URLs
    
    Args:
        url_infos: List of URLInfo objects to summarize
        cache: Cache object
        force: Force re-summarization of existing summaries
        limit: Maximum number to process
        model: Gemini model to use
        language: Output language for summaries
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
            
            success, summary_data, error = summarize_content(cache, url_info, model=model, language=language)
            
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


def show_summary_files(cache: Cache, url_infos: List[URLInfo]) -> None:
    """Display summary file paths and contents for specified URLs"""
    if not url_infos:
        print("No URLs specified")
        return
    
    for i, url_info in enumerate(url_infos):
        if i > 0:
            print()  # Add blank line between entries
        
        # Get summary file path
        summary_file = cache.get_summary_path(url_info)
        
        print(f"URL: {url_info.url}")
        
        if not summary_file or not summary_file.exists():
            print(f"Summary file: Not found")
            continue
        
        print(f"Summary file: {summary_file}")
        
        # Display formatted content
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            print("Content:")
            print(f"  Title: {summary_data.get('title', 'N/A')}")
            print(f"  Content Type: {summary_data.get('content_type', 'N/A')}")
            print(f"  File Size: {summary_data.get('file_size', 'N/A')}")
            print(f"  Generated: {summary_data.get('generated', 'N/A')}")
            print(f"  Status: {summary_data.get('status', 'N/A')}")
            print(f"  Valid Content: {summary_data.get('is_valid_content', 'N/A')}")
            
            if 'summary_one_line' in summary_data:
                print(f"  One-line Summary: {summary_data['summary_one_line']}")
            
            if 'summary_detailed' in summary_data:
                detailed = summary_data['summary_detailed']
                if len(detailed) > 200:
                    print(f"  Detailed Summary: {detailed[:200]}...")
                else:
                    print(f"  Detailed Summary: {detailed}")
            
            if 'tags' in summary_data:
                tags = summary_data['tags']
                if isinstance(tags, list):
                    print(f"  Tags ({len(tags)}): {', '.join(tags)}")
                else:
                    print(f"  Tags: {tags}")
        
        except Exception as e:
            print(f"Error reading summary file {summary_file}", file=sys.stderr)
            traceback.print_exc()


