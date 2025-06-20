#!/usr/bin/env python3
"""
Data models for url2md package

Contains URLInfo class and related data structures.
"""

import hashlib
import mimetypes
import re
import requests
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from .download import PLAYWRIGHT_AVAILABLE, download, is_text, user_agent


@dataclass
class URLInfo:
    """Class representing cached file information"""
    url: str
    filename: str
    fetch_date: str
    status: str
    content_type: str
    size: int
    error: str = ""
    hash: str = field(init=False)
    domain: str = field(init=False)
    
    def __post_init__(self):
        """Generate hash and domain after initialization"""
        self.hash = hashlib.md5(self.url.encode('utf-8')).hexdigest()
        if not self.url:
            self.domain = ""
        else:
            try:
                parsed = urlparse(self.url)
                self.domain = parsed.netloc.lower()
            except Exception as e:
                print("URL domain extraction failed, setting empty domain", file=sys.stderr)
                traceback.print_exc()
                self.domain = ""
    
    def to_tsv_line(self) -> str:
        """Serialize to TSV line format"""
        # Escape tabs and newlines in error messages
        safe_error = self.error.replace('\t', ' ').replace('\n', ' ').replace('\r', '')
        return f"{self.url}\t{self.hash}\t{self.filename}\t{self.fetch_date}\t{self.status}\t{self.content_type}\t{self.size}\t{safe_error}"
    
    @classmethod
    def from_tsv_line(cls, line: str) -> 'URLInfo':
        """Deserialize from TSV line format"""
        parts = line.strip().split('\t')
        if len(parts) < 7:
            raise ValueError(f"Invalid TSV line: {line}")
        
        # Error field may be empty
        error = parts[7] if len(parts) > 7 else ""
        
        # Create instance then override hash
        instance = cls(
            url=parts[0],
            filename=parts[2],
            fetch_date=parts[3],
            status=parts[4],
            content_type=parts[5],
            size=int(parts[6]) if parts[6].isdigit() else 0,
            error=error
        )
        # Set hash from TSV (override the one generated from URL)
        instance.hash = parts[1]
        return instance
    
    def fetch_content(self, use_playwright: bool = False) -> str | bytes:
        """
        Fetch content from URL
        
        Args:
            use_playwright: Whether to use Playwright for dynamic rendering
        """
        if use_playwright and PLAYWRIGHT_AVAILABLE:
            # Detect binary files when using Playwright
            match = re.search(r'(\.[a-zA-Z0-9]{1,5})$', self.url)
            if match:
                extension = match.group(1).lower()
                mime_type, _ = mimetypes.guess_type('file' + extension)
                
                # Use requests if MIME type is detected and not text
                if mime_type and not is_text(mime_type):
                    print(f"Binary file detected ({mime_type}): using requests")
                    return self._fetch_content_requests()
            
            # Use Playwright for dynamic rendering
            try:
                content_type, content = download(self.url)
                self.content_type = content_type
                return content
            except Exception as e:
                print("Playwright failed, falling back to requests", file=sys.stderr)
                traceback.print_exc()
                return self._fetch_content_requests()
        else:
            # Use requests
            return self._fetch_content_requests()
    
    def _fetch_content_requests(self) -> bytes:
        """Fetch content using requests library"""
        headers = {'User-Agent': user_agent}
        
        response = requests.get(self.url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Update content type from response
        self.content_type = response.headers.get('content-type', '').split(';')[0].strip()
        
        return response.content


def load_urls_from_file(filepath: str) -> list[str]:
    """
    Load URLs from file or stdin
    
    Args:
        filepath: File path, or '-' for stdin
        
    Returns:
        List of URLs
    """
    import sys
    
    urls = []
    
    if filepath == '-':
        # Read from stdin
        for line in sys.stdin:
            url = line.strip()
            if url and not url.startswith('#'):
                urls.append(url)
    else:
        # Read from file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url and not url.startswith('#'):
                        urls.append(url)
        except Exception as e:
            print(f"Error: Cannot read URL file: {filepath}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)
    
    return urls
