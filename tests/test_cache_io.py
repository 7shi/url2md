#!/usr/bin/env python3
"""
Test cache IO operations and TSV management functionality
"""

import tempfile
from pathlib import Path

from url2md.cache import Cache
from url2md.urlinfo import URLInfo


def test_cache_tsv_save_and_load():
    """Test TSV content and cache state during save/load operations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
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
        
        # Check TSV content
        tsv_content = cache.tsv_path.read_text()
        expected_header = 'url\thash\tfilename\tfetch_date\tstatus\tcontent_type\tsize\terror\n'
        expected_data = 'https://example.com/test\t910d8f18ffe4e3389648f2a252c38786\ttest.html\t2023-01-01T00:00:00\tsuccess\ttext/html\t1024\t\n'
        expected_content = expected_header + expected_data
        
        assert tsv_content == expected_content
        assert len(cache._entries) == 1
        assert cache.header == ['url', 'hash', 'filename', 'fetch_date', 'status', 'content_type', 'size', 'error']
        assert len(cache.data) == 1
        assert cache.data[0] == ['https://example.com/test', '910d8f18ffe4e3389648f2a252c38786', 'test.html', '2023-01-01T00:00:00', 'success', 'text/html', '1024', '']


def test_cache_new_instance_loading():
    """Test loading data in new cache instance"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Create and save data
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
        assert len(cache1._entries) == 1
        
        # Create new instance and load
        cache2 = Cache(cache_dir)
        assert cache2.header == ['url', 'hash', 'filename', 'fetch_date', 'status', 'content_type', 'size', 'error']
        assert len(cache2.data) == 1
        assert cache2.data[0] == ['https://example.com/test', '910d8f18ffe4e3389648f2a252c38786', 'test.html', '2023-01-01T00:00:00', 'success', 'text/html', '1024', '']
        assert len(cache2._entries) == 1
        
        retrieved = cache2.get('https://example.com/test')
        assert retrieved is not None
        assert retrieved.url == 'https://example.com/test'
        assert retrieved.filename == 'test.html'
        assert retrieved.status == 'success'


def test_tsv_empty_field_handling():
    """Test handling of empty fields in TSV data"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Create URL info with empty error field
        cache = Cache(cache_dir)
        url_info = URLInfo(
            url='https://example.com/empty-error',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024,
            error=''  # Empty error field
        )
        cache.add(url_info)
        cache.save()
        
        # Verify TSV content handles empty field correctly
        tsv_content = cache.tsv_path.read_text()
        lines = tsv_content.split('\n')  # Don't strip to preserve trailing tabs
        data_line = lines[1]
        fields = data_line.split('\t')
        
        # Should have 8 fields, with last one being empty
        assert len(fields) == 8
        assert fields[-1] == ''  # Empty error field
        
        # Reload and verify
        new_cache = Cache(cache_dir)
        retrieved = new_cache.get('https://example.com/empty-error')
        assert retrieved is not None
        assert retrieved.error == ''


def test_tsv_missing_columns_padding():
    """Test padding of TSV rows with missing columns"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Manually create TSV with missing error column
        tsv_path = cache_dir / "cache.tsv"
        cache_dir.mkdir(exist_ok=True)
        
        # Write TSV with 7 columns (missing error column)
        with open(tsv_path, 'w', encoding='utf-8') as f:
            f.write('url\thash\tfilename\tfetch_date\tstatus\tcontent_type\tsize\n')
            f.write('https://example.com/test\t910d8f18ffe4e3389648f2a252c38786\ttest.html\t2023-01-01T00:00:00\tsuccess\ttext/html\t1024\n')
        
        # Load cache and verify padding works
        cache = Cache(cache_dir)
        assert len(cache.data) == 1
        assert len(cache.data[0]) == 8  # Should be padded to 8 columns
        assert cache.data[0][-1] == ''  # Padded error field should be empty
        
        retrieved = cache.get('https://example.com/test')
        assert retrieved is not None
        assert retrieved.url == 'https://example.com/test'
        assert retrieved.error == ''  # Should default to empty string