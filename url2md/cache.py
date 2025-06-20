#!/usr/bin/env python3
"""
Cache management for url2md package

Handles URL caching, file storage, and metadata management.
"""

import mimetypes
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .urlinfo import URLInfo
from .tsv_manager import TSVManager
from .translation_cache import TranslationCache


@dataclass
class CacheResult:
    """Class representing the result of cache operations"""
    success: bool
    url_info: URLInfo
    downloaded: bool


class Cache(TSVManager):
    """Class for managing cache"""
    
    def __init__(self, cache_dir: Path = Path("cache")):
        """Initialize cache"""
        self._cache_dir = cache_dir
        self._entries: Dict[str, URLInfo] = {}  # url -> URLInfo
        self._domain_access_times: Dict[str, datetime] = {}
        
        # Initialize TSV manager
        super().__init__(cache_dir / "cache.tsv")
        
        # Initialize translation cache
        self.translation_cache = TranslationCache(cache_dir)
        
        # Create directories
        self._create_cache_directories()
        
        # Load existing data
        self.load()
    
    
    @property
    def content_dir(self) -> Path:
        """Path to content directory"""
        return self._cache_dir / "content"
    
    def create_summary_directory(self) -> Path:
        """Create and return summary directory"""
        summary_dir = self._cache_dir / "summary"
        summary_dir.mkdir(exist_ok=True)
        return summary_dir
    
    def get_summary_path(self, url_info: URLInfo) -> Optional[Path]:
        """Generate summary file path from URLInfo"""
        if not url_info.filename:
            return None
        summary_dir = self.create_summary_directory()
        # Replace filename extension with .json
        base_name = Path(url_info.filename).stem
        return summary_dir / f"{base_name}.json"
    
    def load(self) -> None:
        """Load data from cache.tsv"""
        try:
            super().load()  # Load TSV data
        except Exception as e:
            print(f"Error: Cannot open cache file: {self.tsv_path}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)
        
        self._entries.clear()
        for row in self.data:
            if len(row) >= 7:  # Ensure we have minimum required columns
                try:
                    # Pad row to 8 columns if necessary (for missing error field)
                    while len(row) < 8:
                        row.append('')
                    line = '\t'.join(row)
                    url_info = URLInfo.from_tsv_line(line)
                    self._entries[url_info.url] = url_info
                except ValueError as e:
                    print("Warning: Failed to parse TSV line", file=sys.stderr)
                    traceback.print_exc()
    
    def save(self) -> None:
        """Save data to cache.tsv"""
        try:
            # Prepare header and data
            self.header = ['url', 'hash', 'filename', 'fetch_date', 'status', 'content_type', 'size', 'error']
            self.data = []
            
            # Convert URLInfo entries to TSV rows
            for url_info in self._entries.values():
                line = url_info.to_tsv_line()
                self.data.append(line.split('\t'))
            
            # Save using parent class
            super().save()
            
        except Exception as e:
            print("Error: cache.tsv save error", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)
    
    def add(self, url_info: URLInfo) -> None:
        """Add new entry"""
        self._entries[url_info.url] = url_info
        
        # Update domain access time
        if url_info.domain:
            self._domain_access_times[url_info.domain] = datetime.now()
    
    def get(self, url: str) -> Optional[URLInfo]:
        """Get URLInfo for URL"""
        return self._entries.get(url)
    
    def exists(self, url: str) -> bool:
        """Check if URL exists in cache"""
        return url in self._entries

    def get_all(self) -> List[URLInfo]:
        """Get all entries"""
        return list(self._entries.values())
    
    def get_content_path(self, url_info: URLInfo) -> Path:
        """Get content file path from URLInfo"""
        return self.content_dir / url_info.filename
    
    def wait_for_domain_throttle(self, domain: str, wait_seconds: int = 5):
        """Domain-based throttling"""
        last_access = self._domain_access_times.get(domain)
        if last_access:
            elapsed = (datetime.now() - last_access).total_seconds()
            if elapsed < wait_seconds:
                wait_time = wait_seconds - elapsed
                print(f"  Domain access control: waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
    
    def _create_cache_directories(self):
        """Create cache directories"""
        self._cache_dir.mkdir(exist_ok=True)
        self.content_dir.mkdir(exist_ok=True)
   
    def find_available_filename(self, url_info: URLInfo):
        """Find a filename that doesn't collide"""
        
        # Get extension from MIME type
        extension = '.html'  # Default
        if url_info.content_type:
            # Get extension using mimetypes library (content_type is already clean)
            ext = mimetypes.guess_extension(url_info.content_type)
            if ext:
                extension = ext
        
        filename = f"{url_info.hash}{extension}"
        if not (self.content_dir / filename).exists():
            url_info.filename = filename
            return
        
        # Add counter if collision occurs
        counter = 1
        while True:
            filename = f"{url_info.hash}-{counter}{extension}"
            if not (self.content_dir / filename).exists():
                url_info.filename = filename
                break
            counter += 1
    
    def fetch_and_cache_url(self, url: str, use_playwright: bool = False, throttle_seconds: int = 5) -> CacheResult:
        """Fetch URL and cache it
        
        Returns:
            CacheResult: Result of cache operation
        """
        # Check if already successfully cached and file exists
        if url_info := self.get(url):
            if url_info.status == 'success' and url_info.filename and self.get_content_path(url_info).exists():
                print(f"URL already fetched: {url}")
                print(f"File: {url_info.filename}")
                print(f"Status: {url_info.status}")
                
                return CacheResult(
                    success=True,
                    url_info=url_info,
                    downloaded=False
                )
            else:
                if url_info.status == 'success':
                    print(f"Success status but file not found, retrying: {url}")
                    print(f"Filename: {url_info.filename}")
                else:
                    print(f"Retrying URL with error status: {url}")
                    print(f"Previous error: {url_info.error}")
        else:
            # Create URLInfo
            url_info = URLInfo(url=url, filename="", fetch_date="", status="", content_type="", size=0)
        
        # Domain-based throttling
        if url_info.domain:
            self.wait_for_domain_throttle(url_info.domain, throttle_seconds)
        
        # Fetch content from URL
        try:
            content = url_info.fetch_content(use_playwright=use_playwright)
            url_info.fetch_date = datetime.now().isoformat()
            
            # Clean content type (remove charset part)
            if url_info.content_type and ';' in url_info.content_type:
                url_info.content_type = url_info.content_type.split(';')[0].strip()
            
            # Find available filename
            self.find_available_filename(url_info)
            
            # Save content to file
            content_path = self.get_content_path(url_info)
            with open(content_path, 'wb') as f:
                if isinstance(content, str):
                    f.write(content.encode('utf-8'))
                else:
                    f.write(content)
            
            url_info.size = len(content)
            url_info.status = 'success'
            
            # Add to cache and save
            self.add(url_info)
            self.save()
            
            print(f"Successfully cached: {url}")
            print(f"File: {url_info.filename}")
            print(f"Size: {url_info.size} bytes")
            
            return CacheResult(
                success=True,
                url_info=url_info,
                downloaded=True
            )
            
        except Exception as e:
            # Handle error
            error_msg = str(e)
            # Remove " at http" part (Playwright error message format)
            if " at http" in error_msg:
                error_msg = error_msg.split(" at http")[0]
            
            url_info.error = error_msg
            url_info.status = 'error'
            url_info.fetch_date = datetime.now().isoformat()
            
            # Add to cache and save
            self.add(url_info)
            self.save()
            
            print(f"Failed to fetch: {url}")
            print(f"Error: {error_msg}")
            
            return CacheResult(
                success=False,
                url_info=url_info,
                downloaded=False
            )