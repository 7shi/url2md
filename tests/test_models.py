#!/usr/bin/env python3
"""
Tests for models.py module
"""

import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch, mock_open

from url2md.models import URLInfo, load_urls_from_file


class TestURLInfo:
    """Tests for URLInfo data class"""
    
    def test_urlinfo_creation(self):
        """Test URLInfo creation and post_init"""
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        # Check that hash and domain are generated
        assert url_info.hash, "Hash not generated"
        assert url_info.domain == 'example.com', f"Domain mismatch: {url_info.domain}"
        assert len(url_info.hash) == 32, "Hash should be MD5 (32 chars)"
    
    def test_urlinfo_tsv_serialization(self):
        """Test TSV serialization/deserialization"""
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024,
            error='test error'
        )
        
        # Test serialization
        tsv_line = url_info.to_tsv_line()
        assert url_info.url in tsv_line
        assert url_info.hash in tsv_line
        assert url_info.filename in tsv_line
        
        # Test deserialization
        reconstructed = URLInfo.from_tsv_line(tsv_line)
        assert reconstructed.url == url_info.url
        assert reconstructed.hash == url_info.hash
        assert reconstructed.filename == url_info.filename
        assert reconstructed.status == url_info.status
        assert reconstructed.content_type == url_info.content_type
        assert reconstructed.size == url_info.size
        assert reconstructed.error == url_info.error
    
    def test_urlinfo_error_escaping(self):
        """Test error message escaping in TSV"""
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='error',
            content_type='text/html',
            size=0,
            error='Error with\ttab and\nnewline'
        )
        
        tsv_line = url_info.to_tsv_line()
        # Tabs and newlines should be replaced with spaces
        assert '\t' not in tsv_line.split('\t')[-1]  # Error field
        assert '\n' not in tsv_line
        assert '\r' not in tsv_line
    
    def test_urlinfo_invalid_tsv(self):
        """Test handling of invalid TSV lines"""
        # Too few fields
        with pytest.raises(ValueError):
            URLInfo.from_tsv_line('url\thash\tfilename')
        
        # Empty line
        with pytest.raises(ValueError):
            URLInfo.from_tsv_line('')
    
    def test_urlinfo_domain_extraction(self):
        """Test domain extraction from various URLs"""
        test_cases = [
            ('https://example.com/path', 'example.com'),
            ('http://subdomain.example.org', 'subdomain.example.org'),
            ('https://Example.COM/path', 'example.com'),  # Should be lowercase
            ('invalid-url', ''),  # Invalid URL should result in empty domain
        ]
        
        for url, expected_domain in test_cases:
            url_info = URLInfo(
                url=url,
                filename='test.html',
                fetch_date='2023-01-01T00:00:00',
                status='success',
                content_type='text/html',
                size=1024
            )
            assert url_info.domain == expected_domain, f"Domain mismatch for {url}"
    
    @patch('url2md.models.requests.get')
    def test_fetch_content_requests(self, mock_get):
        """Test fetch_content using requests"""
        # Mock successful response
        mock_response = mock_get.return_value
        mock_response.content = b'test content'
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.raise_for_status.return_value = None
        
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        content = url_info.fetch_content(use_playwright=False)
        assert content == b'test content'
        assert url_info.content_type == 'text/html'
        
        # Verify requests was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == url_info.url
        assert 'User-Agent' in kwargs['headers']
    
    @patch('url2md.models.requests.get')
    def test_fetch_content_error_handling(self, mock_get):
        """Test fetch_content error handling"""
        # Mock timeout error
        mock_get.side_effect = Exception("Connection timeout")
        
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        with pytest.raises(Exception) as exc_info:
            url_info.fetch_content(use_playwright=False)
        
        assert "Connection timeout" in str(exc_info.value)


class TestLoadUrlsFromFile:
    """Tests for load_urls_from_file function"""
    
    def test_load_urls_from_regular_file(self):
        """Test loading URLs from regular file"""
        test_content = """# Comment line
https://example1.com
https://example2.com
# Another comment

https://example3.com
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            urls = load_urls_from_file(temp_file_path)
            expected_urls = ['https://example1.com', 'https://example2.com', 'https://example3.com']
            assert urls == expected_urls
        finally:
            Path(temp_file_path).unlink()
    
    def test_load_urls_empty_file(self):
        """Test loading URLs from empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write('')
            temp_file_path = temp_file.name
        
        try:
            urls = load_urls_from_file(temp_file_path)
            assert urls == []
        finally:
            Path(temp_file_path).unlink()
    
    def test_load_urls_comments_only(self):
        """Test loading URLs from file with only comments"""
        test_content = """# Comment 1
# Comment 2
# Comment 3
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            urls = load_urls_from_file(temp_file_path)
            assert urls == []
        finally:
            Path(temp_file_path).unlink()
    
    @patch('sys.stdin')
    def test_load_urls_from_stdin(self, mock_stdin):
        """Test loading URLs from stdin"""
        mock_stdin.__iter__.return_value = [
            '# Comment\n',
            'https://example1.com\n',
            '\n',  # Empty line
            'https://example2.com\n'
        ]
        
        urls = load_urls_from_file('-')
        expected_urls = ['https://example1.com', 'https://example2.com']
        assert urls == expected_urls
    
    def test_load_urls_file_not_found(self):
        """Test handling of non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_urls_from_file('/nonexistent/file.txt')
    
    def test_load_urls_with_whitespace(self):
        """Test URL loading with various whitespace"""
        test_content = """  https://example1.com  
	https://example2.com	
 
https://example3.com
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            urls = load_urls_from_file(temp_file_path)
            expected_urls = ['https://example1.com', 'https://example2.com', 'https://example3.com']
            assert urls == expected_urls
        finally:
            Path(temp_file_path).unlink()