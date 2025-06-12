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


def test_schema_files():
    """Test schema file structure"""
    schema_files = [
        ('schemas/summarize.json', {
            'required': ['title', 'summary_one_line', 'summary_detailed', 'tags', 'is_valid_content'],
            'properties': ['title', 'summary_one_line', 'summary_detailed', 'tags', 'is_valid_content']
        }),
        ('schemas/classify.json', {
            'required': ['themes', 'tag_stats'],
            'properties': ['themes', 'tag_stats']
        })
    ]
    
    for schema_file, expected in schema_files:
        schema_path = Path(schema_file)
        if not schema_path.exists():
            pytest.fail(f"{schema_file} not found")
            
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        required_fields = schema.get('required', [])
        properties = list(schema.get('properties', {}).keys())
        
        # Check required fields
        assert set(required_fields) == set(expected['required']), f"Required fields mismatch in {schema_file}"
            
        # Check properties
        assert set(properties) == set(expected['properties']), f"Properties mismatch in {schema_file}"


def test_gemini_integration():
    """Test gemini.py integration functionality"""
    with open('url2md/gemini.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Check important functions
    required_patterns = [
        # Schema support
        (r'def build_schema_from_json\(', "Schema building function"),
        (r'case "boolean":', "Boolean type support"),
        (r'if "enum" in json_data:', "Enum support"),
        
        # File upload
        (r'def upload_file\(.*?mime_type.*?\)', "File upload with mime_type"),
        (r'def delete_file\(', "File deletion function"),
        
        # Config generation
        (r'def config_from_schema\(', "Schema-based config generation"),
    ]
    
    for pattern, description in required_patterns:
        assert re.search(pattern, code, re.DOTALL), f"Missing: {description}"


def test_models_api():
    """Test models.py API structure"""
    with open('url2md/models.py', 'r', encoding='utf-8') as f:
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
        
        # Each command module should have a main function
        assert 'def main(' in code, f"Missing main function in {module_path}"


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
        'run_pipeline'
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
        'url2md/models.py',
        'url2md/cache.py',
        'url2md/fetch.py',
        'url2md/summarize.py',
        'url2md/classify.py',
        'url2md/report.py',
        'url2md/gemini.py',
        'url2md/utils.py',
        'url2md/download.py',
        'pyproject.toml',
        'README.md',
        'CLAUDE.md'
    ]
    
    for file_path in required_files:
        assert Path(file_path).exists(), f"Missing required file: {file_path}"


def test_documentation():
    """Test CLAUDE.md documentation"""
    with open('CLAUDE.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check important sections
    required_sections = [
        'summarize.py',
        'classify.py', 
        'report.py',
        'Environment Variables',
        'GEMINI_API_KEY'
    ]
    
    for section in required_sections:
        assert section in content, f"Missing documentation for: {section}"


def test_pyproject_configuration():
    """Test pyproject.toml configuration"""
    with open('pyproject.toml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check key configurations
    assert 'name = "url2md"' in content, "Package name not configured"
    assert 'CC0-1.0' in content, "License not configured correctly"
    assert 'url2md = "url2md.main:main"' in content, "Entry point not configured"
    assert 'google-genai' in content, "Gemini dependency missing"