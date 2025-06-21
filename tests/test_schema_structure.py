#!/usr/bin/env python3
"""
Test schema files and code structure without Google API dependencies

Usage:
    uv run pytest tests/test_schema_structure.py
"""

import json
import re
from pathlib import Path
import pytest


def test_schema_modules():
    """Test schema module structure"""
    schema_modules = [
        ('summarize_schema', 'build_summarize_schema', {
            'required': ['title', 'summary_one_line', 'summary_detailed', 'tags', 'is_valid_content'],
            'properties': ['title', 'summary_one_line', 'summary_detailed', 'tags', 'is_valid_content']
        }),
        ('classify_schema', 'build_classify_schema', {
            'required': ['themes', 'classification_summary'],
            'properties': ['themes', 'classification_summary']
        }),
        ('translate_schema', 'build_translate_schema', {
            'required': ['translations'],
            'properties': ['translations']
        }),
    ]
    
    for module_name, function_name, expected in schema_modules:
        try:
            module = __import__(f'url2md.{module_name}', fromlist=[function_name])
            schema_func = getattr(module, function_name)
            
            # Test schema creation
            if function_name == 'build_translate_schema':
                # translate_schema requires terms parameter
                schema = schema_func(['test', 'example'])
            else:
                schema = schema_func()
            
            required_fields = schema.get('required', [])
            properties = list(schema.get('properties', {}).keys())
            
            # Check required fields
            assert set(required_fields) == set(expected['required']), f"Required fields mismatch in {module_name}"
                
            # Check properties
            assert set(properties) == set(expected['properties']), f"Properties mismatch in {module_name}"
            
            # Test language parameter (only for non-translate schemas)
            if function_name != 'build_translate_schema':
                schema_lang = schema_func(language='English')
                assert schema_lang is not None
            
        except ImportError:
            pytest.fail(f"Cannot import {module_name}.{function_name}")
        except Exception as e:
            pytest.fail(f"Error testing {module_name}: {e}")



def test_models_api():
    """Test urlinfo.py API structure"""
    with open('url2md/urlinfo.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Check classes
    api_classes = [
        'URLInfo'
    ]
    
    for cls in api_classes:
        assert f'class {cls}' in code, f"Missing API class: {cls}"
    
    # Check functions
    api_functions = [
        'load_urls_from_file'
    ]
    
    for func in api_functions:
        assert f'def {func}(' in code, f"Missing API function: {func}"


def test_cache_api():
    """Test cache.py API structure"""
    with open('url2md/cache.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Check classes
    api_classes = [
        'Cache',
        'CacheResult'
    ]
    
    for cls in api_classes:
        assert f'class {cls}' in code, f"Missing API class: {cls}"
    
    # Check Cache class methods
    cache_methods = [
        'get_content_path',
        'get_summary_path',
        'fetch_and_cache_url',
        'load',
        'save'
    ]
    
    for method in cache_methods:
        assert f'def {method}(' in code, f"Missing Cache method: {method}"


def test_command_modules():
    """Test command module structure"""
    command_modules = [
        'url2md/fetch.py',
        'url2md/summarize.py', 
        'url2md/classify.py',
        'url2md/report.py'
    ]
    
    for module_path in command_modules:
        module_file = Path(module_path)
        assert module_file.exists(), f"Missing command module: {module_path}"
        
        with open(module_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Each command module should have core functions (centralized architecture)
        if 'fetch.py' in module_path:
            assert 'def fetch_urls(' in code, f"Missing fetch_urls function in {module_path}"
        elif 'summarize.py' in module_path:
            assert 'def summarize_urls(' in code, f"Missing summarize_urls function in {module_path}"
        elif 'classify.py' in module_path:
            assert 'def extract_tags(' in code, f"Missing extract_tags function in {module_path}"
        elif 'report.py' in module_path:
            assert 'def generate_markdown_report(' in code, f"Missing generate_markdown_report function in {module_path}"


def test_main_entry_point():
    """Test main.py entry point structure"""
    with open('url2md/main.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Check subcommand handlers
    required_handlers = [
        'run_fetch',
        'run_summarize',
        'run_classify', 
        'run_report',
        'run_workflow'
    ]
    
    for handler in required_handlers:
        assert f'def {handler}(' in code, f"Missing command handler: {handler}"
    
    # Check main function
    assert 'def main(' in code, "Missing main function"


def test_package_structure():
    """Test package file structure"""
    required_files = [
        'url2md/__init__.py',
        'url2md/main.py',
        'url2md/urlinfo.py',
        'url2md/cache.py',
        'url2md/fetch.py',
        'url2md/summarize.py',
        'url2md/classify.py',
        'url2md/report.py',
        'url2md/utils.py',
        'url2md/download.py',
        'pyproject.toml',
        'README.md',
        'CLAUDE.md'
    ]
    
    for file_path in required_files:
        assert Path(file_path).exists(), f"Missing required file: {file_path}"




def test_pyproject_configuration():
    """Test pyproject.toml configuration"""
    with open('pyproject.toml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check key configurations
    assert 'name = "url2md"' in content, "Package name not configured"
    assert 'CC0-1.0' in content, "License not configured correctly"
    assert 'url2md = "url2md.main:main"' in content, "Entry point not configured"
    assert 'google-genai' in content, "Gemini dependency missing"
