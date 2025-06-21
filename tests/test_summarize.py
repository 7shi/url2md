#!/usr/bin/env python3
"""
Tests for summarize.py module

Usage:
    uv run pytest tests/test_summarize.py
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from url2md.urlinfo import URLInfo
from url2md.cache import Cache
from url2md.summarize import generate_summary_prompt, summarize_content


def test_schema_validation():
    """Test summarize schema structure using Pydantic schema"""
    from url2md.schema import create_summarize_schema_class
    
    # Test without language
    schema_class = create_summarize_schema_class()
    schema = schema_class.model_json_schema()
    assert schema.get('type') == 'object'
    
    required_fields = schema.get('required', [])
    properties = list(schema.get('properties', {}).keys())
    
    print(f"Required fields: {required_fields}")
    print(f"Properties: {properties}")
    
    # Check required fields
    expected_required = ['title', 'summary_one_line', 'summary_detailed', 'tags', 'is_valid_content']
    assert set(required_fields) == set(expected_required), f"Required fields mismatch: got {required_fields}"
        
    # Check properties
    assert set(properties) == set(expected_required), f"Properties mismatch: got {properties}"
    
    # Test with language
    schema_class_jp = create_summarize_schema_class(language='Japanese')
    schema_jp = schema_class_jp.model_json_schema()
    title_desc = schema_jp['properties']['title']['description']
    assert 'in Japanese' in title_desc, "Language not properly integrated"


def test_imports():
    """Test summarize.py imports"""
    # Basic imports
    from url2md.summarize import (
        generate_summary_prompt,
        summarize_content,
        summarize_urls
    )
    
    # Cache functionality
    from url2md.cache import Cache


def test_mime_type_handling():
    """Test MIME type handling (simplified version)"""
    # The get_mime_type_for_gemini function was simplified to content_type or "text/plain"
    test_cases = [
        ("text/html", "text/html"),
        ("application/pdf", "application/pdf"),
        ("text/plain", "text/plain"),
        ("", "text/plain"),  # Empty string default
        (None, "text/plain"),  # None default
    ]
    
    for content_type, expected in test_cases:
        # Test simplified processing
        result = content_type or "text/plain"
        assert result == expected, f"Input: {content_type}, Expected: {expected}, Got: {result}"


def test_prompt_generation():
    """Test prompt generation functionality"""
    from url2md.summarize import generate_summary_prompt
    
    url = "https://example.com/test"
    content_type = "text/html"
    
    prompt = generate_summary_prompt(url, content_type)
    
    # Check basic prompt structure
    required_elements = [
        "structured JSON",
        "summary_one_line",
        "summary_detailed", 
        "tags",
        "is_valid_content",
        url,
        content_type
    ]
    
    for element in required_elements:
        assert element in prompt, f"Missing element in prompt: {element}"


def test_file_operations():
    """Test file operation functionality"""
    from url2md.urlinfo import URLInfo
    from url2md.cache import Cache
    
    # Test with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Create Cache object
        cache = Cache(cache_dir)
        
        # Test summary directory creation
        summary_dir = cache.create_summary_directory()
        assert summary_dir.exists(), "Summary directory creation failed"
        
        # Test URLInfo
        test_url_info = URLInfo(
            url='https://example.com/test',
            filename='test123hash.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        # Test summary file existence check
        summary_file = cache.get_summary_path(test_url_info)
        
        # Should not exist initially
        assert not summary_file.exists(), "False positive for non-existent summary"
        
        # Create JSON file and verify existence
        summary_file.parent.mkdir(exist_ok=True)
        summary_file.write_text('{"test": "data"}')
        
        assert summary_file.exists(), "Failed to detect existing summary"


def test_json_structure():
    """Test JSON structured output"""
    from url2md.urlinfo import URLInfo
    from url2md.cache import Cache
    
    # Test data
    url_info = URLInfo(
        url='https://example.com/test',
        filename='test.html',
        fetch_date='2023-01-01T00:00:00',
        status='success',
        content_type='text/html',
        size=1024
    )
    
    summary_data = {
        'title': ['Test Page Title'],
        'summary_one_line': 'Concise test page summary',
        'summary_detailed': 'This is a detailed summary of the test page. It explains the main content and its value.',
        'tags': ['test', 'webpage', 'technology'],
        'is_valid_content': True
    }
    
    # Test with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        # Create summary directory
        summary_dir = cache.create_summary_directory()
        
        # Get summary path and save data
        summary_path = cache.get_summary_path(url_info)
        summary_path.parent.mkdir(exist_ok=True)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        assert summary_path.exists(), "JSON file was not created"
            
        # Verify JSON content
        with open(summary_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        # Check summary data
        for key, value in summary_data.items():
            assert saved_data.get(key) == value, f"Summary data mismatch for {key}"


@patch('url2md.summarize.generate_content_retry')
@patch('url2md.summarize.config_from_schema')
@patch('url2md.summarize.build_schema_from_json')
def test_summarize_content_mock(mock_build_schema, mock_config, mock_generate):
    """Test summarize_content with mocked dependencies"""
    # Setup mocks
    mock_build_schema.return_value = Mock()
    mock_config.return_value = Mock()
    # Create a mock Response object
    mock_response = Mock()
    mock_response.text = json.dumps({
        'title': 'Test Title',
        'summary_one_line': 'Test summary',
        'summary_detailed': 'Detailed test summary',
        'tags': ['test'],
        'is_valid_content': True
    })
    mock_generate.return_value = mock_response
    
    # Create test data
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        # Create test content file
        content_path = cache_dir / 'content' / 'test.html'
        content_path.parent.mkdir(exist_ok=True)
        content_path.write_text('<html><body><h1>Test</h1></body></html>')
        
        url_info = URLInfo(
            url='https://example.com/test',
            filename='test.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        # Test summarize_content
        success, summary_data, error = summarize_content(cache, url_info, model="test-model")
        
        assert success is True
        assert error is None
        assert 'title' in summary_data
        assert isinstance(summary_data['title'], list)  # Should be converted to list


def test_filter_functions():
    """Test URL filtering functions"""
    from url2md.summarize import filter_url_infos_by_urls, filter_url_infos_by_hash
    from url2md.cache import Cache
    
    # Create test cache with URLInfo objects
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = Cache(cache_dir)
        
        # Add test URLInfo objects
        url_info1 = URLInfo(
            url='https://example1.com',
            filename='test1.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=1024
        )
        
        url_info2 = URLInfo(
            url='https://example2.com',
            filename='test2.html',
            fetch_date='2023-01-01T00:00:00',
            status='success',
            content_type='text/html',
            size=2048
        )
        
        cache.add(url_info1)
        cache.add(url_info2)
        
        # Test URL filtering
        filtered_by_url = filter_url_infos_by_urls(cache, ['https://example1.com'])
        assert len(filtered_by_url) == 1
        assert filtered_by_url[0].url == 'https://example1.com'
        
        # Test hash filtering
        filtered_by_hash = filter_url_infos_by_hash(cache, url_info1.hash)
        assert len(filtered_by_hash) == 1
        assert filtered_by_hash[0].hash == url_info1.hash
        
        # Test empty filters
        all_urls = filter_url_infos_by_urls(cache, [])
        assert len(all_urls) == 2