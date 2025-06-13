#!/usr/bin/env python3
"""
Integration tests for url2md package

These tests verify that different components work together correctly.
"""

import tempfile
import os
from pathlib import Path
import pytest
import sys
from unittest.mock import patch, Mock

from url2md.main import main
from url2md.cache import Cache
from url2md.models import URLInfo


class TestCommandIntegration:
    """Integration tests for command-line interface"""
    
    def test_main_help(self):
        """Test main help command"""
        with patch('sys.argv', ['url2md', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                from url2md.main import main
                main()
            # Help should exit with code 0
            assert exc_info.value.code == 0
    
    def test_subcommand_help(self):
        """Test subcommand help"""
        with patch('sys.argv', ['url2md', 'fetch', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                from url2md.main import main
                main()
            # Help should exit with code 0
            assert exc_info.value.code == 0
    
    def test_no_command(self):
        """Test main with no command"""
        with patch('sys.argv', ['url2md']):
            result = main()
            assert result == 1  # Should return error code
    
    def test_init_command_integration(self):
        """Test init command creates proper cache structure"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)
                
                # Test init command
                with patch.object(sys, 'argv', ['url2md', 'init', 'test_cache']):
                    result = main()
                    assert result == 0
                
                # Verify cache structure was created
                cache_dir = temp_path / "test_cache"
                assert cache_dir.exists()
                assert (cache_dir / "cache.tsv").exists()
                assert (cache_dir / "content").exists()
                assert (cache_dir / "summary").exists()
                
            finally:
                os.chdir(original_cwd)
    
    def test_init_command_existing_cache_fails(self):
        """Test init command fails when cache already exists"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)
                
                # First init should succeed
                with patch.object(sys, 'argv', ['url2md', 'init', 'test_cache']):
                    result = main()
                    assert result == 0
                
                # Second init should fail
                with patch.object(sys, 'argv', ['url2md', 'init', 'test_cache']):
                    result = main()
                    assert result == 1  # Should fail
                
            finally:
                os.chdir(original_cwd)
    
    def test_init_command_conflicting_args_fails(self):
        """Test init command fails when both --cache-dir and directory are specified"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)
                
                # Should fail with conflicting arguments
                with patch.object(sys, 'argv', ['url2md', '--cache-dir', 'foo', 'init', 'bar']):
                    result = main()
                    assert result == 1  # Should fail due to conflict
                
            finally:
                os.chdir(original_cwd)
    
    def test_init_command_with_cache_dir_global_option(self):
        """Test init command with --cache-dir global option"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)
                
                # Should work with --cache-dir
                with patch.object(sys, 'argv', ['url2md', '--cache-dir', 'custom_cache', 'init']):
                    result = main()
                    assert result == 0
                
                # Verify cache structure was created in custom location
                cache_dir = temp_path / "custom_cache"
                assert cache_dir.exists()
                assert (cache_dir / "cache.tsv").exists()
                assert (cache_dir / "content").exists()
                assert (cache_dir / "summary").exists()
                
            finally:
                os.chdir(original_cwd)


class TestCacheIntegration:
    """Integration tests for cache functionality"""
    
    def test_cache_urlinfo_integration(self):
        """Test Cache and URLInfo integration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = Cache(cache_dir)
            
            # Create URLInfo
            url_info = URLInfo(
                url='https://example.com/test',
                filename='test.html',
                fetch_date='2023-01-01T00:00:00',
                status='success',
                content_type='text/html',
                size=1024
            )
            
            # Test full workflow
            cache.add(url_info)
            cache.save()
            
            # Create content file
            content_path = cache.get_content_path(url_info)
            content_path.parent.mkdir(exist_ok=True)
            content_path.write_text('<html><body>Test content</body></html>')
            
            # Create summary
            summary_path = cache.get_summary_path(url_info)
            summary_path.parent.mkdir(exist_ok=True)
            summary_data = {
                'title': ['Test Page'],
                'summary_one_line': 'Test summary',
                'summary_detailed': 'Detailed test summary',
                'tags': ['test'],
                'is_valid_content': True
            }
            
            import json
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f)
            
            # Verify integration
            assert cache.exists(url_info.url)
            assert content_path.exists()
            assert summary_path.exists()
            
            # Test reload
            new_cache = Cache(cache_dir)
            reloaded_info = new_cache.get(url_info.url)
            assert reloaded_info is not None
            assert reloaded_info.url == url_info.url


class TestWorkflowIntegration:
    """Integration tests for complete workflows"""
    
    @patch('url2md.fetch.Cache.fetch_and_cache_url')
    def test_fetch_workflow_integration(self, mock_fetch):
        """Test fetch command workflow"""
        # Mock successful fetch
        mock_result = Mock()
        mock_result.success = True
        mock_result.downloaded = True
        mock_fetch.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            
            from url2md.main import main as url2md_main
            import sys
            from unittest.mock import patch
            
            # Test fetch command via main entry point
            with patch.object(sys, 'argv', ['url2md', '--cache-dir', str(cache_dir), 'fetch', 'https://example.com/test']):
                result = url2md_main()
                assert result == 0
            mock_fetch.assert_called_once()
    
    def test_schema_file_integration(self):
        """Test schema file accessibility"""
        from url2md.gemini import config_from_schema
        
        # Test that schema files can be loaded
        schema_files = [
            'schemas/summarize.json',
            'schemas/classify.json'
        ]
        
        for schema_file in schema_files:
            schema_path = Path(schema_file)
            assert schema_path.exists(), f"Schema file not found: {schema_file}"
            
            # Test that config can be created from schema
            try:
                config = config_from_schema(schema_file)
                assert config is not None
            except Exception as e:
                pytest.fail(f"Failed to create config from {schema_file}: {e}")


class TestModuleIntegration:
    """Integration tests for module imports and dependencies"""
    
    def test_all_imports(self):
        """Test that all modules can be imported"""
        import url2md
        import url2md.main
        import url2md.models
        import url2md.cache
        import url2md.fetch
        import url2md.summarize
        import url2md.classify
        import url2md.report
        import url2md.gemini
        import url2md.utils
        import url2md.download
        
        # Test main exports
        assert hasattr(url2md, 'URLInfo')
        assert hasattr(url2md, 'Cache')
        assert hasattr(url2md, 'CacheResult')
    
    def test_command_module_integration(self):
        """Test that command modules have required interfaces"""
        from url2md import fetch, summarize, classify, report
        
        # Each command module should have core functions (no main in centralized architecture)
        assert hasattr(fetch, 'fetch_urls')
        assert hasattr(summarize, 'summarize_urls')
        assert hasattr(classify, 'extract_tags')
        assert hasattr(report, 'generate_markdown_report')
        
        # Test that core functions are callable
        assert callable(fetch.fetch_urls)
        assert callable(summarize.summarize_urls)
        assert callable(classify.extract_tags)
        assert callable(report.generate_markdown_report)
    
    def test_gemini_integration(self):
        """Test Gemini API integration setup"""
        from url2md.gemini import (
            models, client, build_schema_from_json, 
            config_from_schema, generate_content_retry
        )
        
        # Test basic functionality exists
        assert isinstance(models, list)
        assert len(models) > 0
        assert client is not None
        assert callable(build_schema_from_json)
        assert callable(config_from_schema)
        assert callable(generate_content_retry)
    
    def test_utils_integration(self):
        """Test utility function integration"""
        from url2md.utils import extract_body_content, extract_html_title
        
        # Test functions are callable
        assert callable(extract_body_content)
        assert callable(extract_html_title)
        
        # Quick functionality test
        html = '<html><head><title>Test</title></head><body><p>Content</p></body></html>'
        title = extract_html_title(html)
        body = extract_body_content(html)
        
        assert title == 'Test'
        assert '<p>Content</p>' in body
        assert '<title>Test</title>' not in body
    
    def test_download_integration(self):
        """Test download module integration"""
        from url2md.download import PLAYWRIGHT_AVAILABLE, is_text, user_agent
        
        # Test basic exports
        assert isinstance(PLAYWRIGHT_AVAILABLE, bool)
        assert callable(is_text)
        assert isinstance(user_agent, str)
        
        # Test is_text function
        assert is_text('text/html') is True
        assert is_text('application/json') is True
        assert is_text('image/png') is False
        assert is_text('') is False