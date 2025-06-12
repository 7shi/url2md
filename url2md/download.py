#!/usr/bin/env python3
"""
Playwright dynamic rendering URL fetcher

Usage:
    uv run download.py https://httpbin.org/
    uv run download.py https://httpbin.org/user-agent
    uv run download.py https://httpbin.org/image/png -o png.png
"""

import argparse
import sys

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"

text_types = [
    'application/json',
    'application/xml',
    'application/xhtml+xml',
    'application/javascript',
    'application/ecmascript',
    'application/x-httpd-php',
    'application/x-sh',
    'application/x-yaml',
]


def is_text(content_type: str) -> bool:
    """Check if content type is text"""
    return bool(content_type and (content_type.startswith('text/') or content_type in text_types))


def download(url: str) -> tuple[str, bytes]:
    """Fetch content after dynamic rendering using Playwright"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_extra_http_headers({'User-Agent': user_agent})
        response = page.goto(url, wait_until='networkidle')
        
        if response and response.status >= 400:
            raise Exception(f"HTTP {response.status}: {response.status_text}")
        
        # Get response Content-Type
        content_type = ""
        if response:
            headers = response.headers
            content_type = headers.get('content-type', '').split(';')[0].strip()
        
        # Check content type
        if is_text(content_type):
            page.wait_for_timeout(2000)  # Wait 2 seconds
            content = page.content().encode("utf-8")
        else:
            content = response.body()
        
        browser.close()
        
        return content_type or "text/html", content


def main():
    if not PLAYWRIGHT_AVAILABLE:
        print("Error: Playwright is not available.")
        print("Install: uv add playwright && uv run playwright install")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description='Playwright dynamic rendering URL fetcher')
    parser.add_argument('url', help='URL to fetch')
    parser.add_argument('-o', '--output', help='Output filename')
    args = parser.parse_args()
    
    print(f"Fetching with dynamic rendering: {args.url}")
    content_type, content = download(args.url)
    t = is_text(content_type)
    
    print(f"Content-Type: {content_type}")
    print("Dynamic rendering complete:" if t else "Binary fetch complete:", len(content), "bytes")
    if args.output:
        with open(args.output, 'wb') as f:
            f.write(content)
        print(f"File saved: {args.output}")
    elif t:
        decoded_content = content.decode('utf-8')
        print(f"\n--- Content ---")
        print(decoded_content[:1000] + "..." if len(decoded_content) > 1000 else decoded_content)


if __name__ == "__main__":
    main()