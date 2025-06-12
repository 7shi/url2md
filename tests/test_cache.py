#!/usr/bin/env python3
"""
Tests for cache.py module functionality

Usage:
    uv run pytest tests/test_cache.py -v -s
"""

import tempfile
from pathlib import Path
import pytest

from url2md.cache import Cache, CacheResult
from url2md.models import URLInfo


def test_cache_initialization():
    """Test Cache initialization"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        # Check directory creation
        assert cache.content_dir.exists(), "Content directory not created"
        assert cache.tsv_path.parent.exists(), "Cache directory not created"


def test_cache_data_operations():
    """Test cache data read/write operations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        # Create test URLInfo
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        # Test add and get
        cache.add(url_info)
        retrieved = cache.get(url_info.url)
        
        assert retrieved is not None, "Failed to retrieve added URLInfo"
        assert retrieved.url == url_info.url, "URL mismatch"
        assert retrieved.hash == url_info.hash, "Hash mismatch"
        
        # Test exists
        assert cache.exists(url_info.url), "exists() returned False for added URL"
        assert not cache.exists('https://nonexistent.com'), "exists() returned True for non-existent URL"
        
        # Test get_all
        all_entries = cache.get_all()
        assert len(all_entries) == 1, "get_all() returned wrong count"
        assert all_entries[0].url == url_info.url, "get_all() returned wrong URLInfo"


def test_cache_persistence():
    """Test cache persistence across instances"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Create first cache instance and add data
        cache1 = Cache(cache_dir)
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        cache1.add(url_info)
        cache1.save()
        
        # Create second cache instance and load data
        cache2 = Cache(cache_dir)
        retrieved = cache2.get(url_info.url)
        
        assert retrieved is not None, "Failed to load data in new cache instance"
        assert retrieved.url == url_info.url, "Loaded data mismatch"


def test_cache_tsv_format():
    """Test cache.tsv format"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        # Add test data
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        cache.add(url_info)
        cache.save()
        
        # Check TSV file format
        tsv_path = cache.tsv_path
        assert tsv_path.exists(), "TSV file not created"
        
        with open(tsv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        assert len(lines) >= 2, "TSV file should have header + data lines"
        
        # Check header
        header = lines[0].strip().split('\t')
        expected_header = ['url', 'hash', 'filename', 'fetch_date', 'status', 'content_type', 'size', 'error']
        assert header == expected_header, f"Header mismatch: got {header}"
        
        # Check data line
        data_line = lines[1].strip().split('\t')
        assert data_line[0] == url_info.url, "URL mismatch in TSV"
        assert data_line[1] == url_info.hash, "Hash mismatch in TSV"
        assert data_line[2] == url_info.filename, "Filename mismatch in TSV"


def test_summary_path_generation():
    """Test summary file path generation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        # Test URLInfo
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test123.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        # Test summary path
        summary_path = cache.get_summary_path(url_info)
        assert summary_path is not None, "Summary path is None"
        assert summary_path.suffix == '.json', "Summary path should have .json extension"
        assert summary_path.stem == 'test123', "Summary path stem should match filename stem"
        
        # Test with URLInfo without filename
        url_info_no_filename = URLInfo(
            url='https://example.com/test2',
            filename='',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=0
        )
        
        summary_path_none = cache.get_summary_path(url_info_no_filename)
        assert summary_path_none is None, "Summary path should be None for empty filename"


def test_content_path_generation():
    """Test content file path generation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test123.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        content_path = cache.get_content_path(url_info)
        assert content_path == cache.content_dir / url_info.filename, "Content path mismatch"


def test_filename_collision_handling():
    """Test filename collision handling"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        # Create URLInfo with specific hash
        url_info = URLInfo(
            url='https://example.com/test',
            filename='',  # Will be generated
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        # Find available filename
        cache.find_available_filename(url_info)
        assert url_info.filename, "Filename not generated"
        assert url_info.filename.endswith('.html'), "Filename should have .html extension"
        
        # Create the file to simulate collision
        content_path = cache.get_content_path(url_info)
        content_path.parent.mkdir(exist_ok=True)
        content_path.write_text('test content')
        
        # Create another URLInfo with same hash
        url_info2 = URLInfo(
            url='https://example.com/test2',
            filename='',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        url_info2.hash = url_info.hash  # Force same hash
        
        # Find available filename (should avoid collision)
        cache.find_available_filename(url_info2)
        assert url_info2.filename != url_info.filename, "Collision not avoided"
        assert '-1' in url_info2.filename, "Counter not added for collision"


def test_domain_throttling():
    """Test domain-based throttling functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        # Test wait_for_domain_throttle method
        # This is mainly a smoke test since we can't easily test timing
        try:
            cache.wait_for_domain_throttle('example.com', wait_seconds=0.1)
        except Exception as e:
            pytest.fail(f"Domain throttling failed: {e}")


def test_cache_result():
    """Test CacheResult data class"""
    url_info = URLInfo(
        url='https://example.com/test',
        filename='test.html',
        fetch_date='2023-01-01T00:00:00',
        status='success',
        content_type='text/html',
        size=1024
    )
    
    # Test successful result
    result = CacheResult(success=True, url_info=url_info, downloaded=True)
    assert result.success is True
    assert result.downloaded is True
    assert result.url_info == url_info
    
    # Test failed result
    failed_result = CacheResult(success=False, url_info=url_info, downloaded=False)
    assert failed_result.success is False
    assert failed_result.downloaded is False