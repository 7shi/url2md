#!/usr/bin/env python3
"""
Tests for cache directory auto-detection functionality
"""

import tempfile
from pathlib import Path
import pytest

from url2md.utils import find_cache_dir


class TestCacheDirectoryDetection:
    """Test cache directory auto-detection functionality"""
    
    def test_find_cache_in_current_directory(self):
        """Test finding cache.tsv in current directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_dir = temp_path / "my_custom_cache"
            cache_dir.mkdir()
            
            # Create cache.tsv
            tsv_file = cache_dir / "cache.tsv"
            tsv_file.write_text("# Cache file\n")
            
            # Change to temp directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)
                result = find_cache_dir()
                # Should find the cache directory with any name
                assert result.resolve() == cache_dir.resolve()
            finally:
                os.chdir(original_cwd)
    
    def test_find_cache_in_parent_directory(self):
        """Test finding cache.tsv in parent directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_dir = temp_path / "url2md_cache"
            cache_dir.mkdir()
            
            # Create cache.tsv
            tsv_file = cache_dir / "cache.tsv"
            tsv_file.write_text("# Cache file\n")
            
            # Create subdirectory
            sub_dir = temp_path / "subdir"
            sub_dir.mkdir()
            
            # Change to subdirectory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(sub_dir)
                result = find_cache_dir()
                # Should find parent's cache directory
                assert result.resolve() == cache_dir.resolve()
            finally:
                os.chdir(original_cwd)
    
    def test_find_cache_in_grandparent_directory(self):
        """Test finding cache.tsv in grandparent directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_dir = temp_path / "data_cache"
            cache_dir.mkdir()
            
            # Create cache.tsv
            tsv_file = cache_dir / "cache.tsv"
            tsv_file.write_text("# Cache file\n")
            
            # Create nested subdirectories
            sub_dir = temp_path / "subdir" / "nested"
            sub_dir.mkdir(parents=True)
            
            # Change to nested subdirectory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(sub_dir)
                result = find_cache_dir()
                # Should find grandparent's cache directory
                assert result.resolve() == cache_dir.resolve()
            finally:
                os.chdir(original_cwd)
    
    def test_no_cache_found_raises_error(self):
        """Test that error is raised when no cache.tsv found"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # No cache directory or cache.tsv file
            
            # Change to temp directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)
                with pytest.raises(ValueError, match="No cache directory found"):
                    find_cache_dir()
            finally:
                os.chdir(original_cwd)
    
    def test_cache_dir_without_tsv_ignored(self):
        """Test that cache directory without cache.tsv is ignored"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create cache directory but no cache.tsv
            cache_dir = temp_path / "cache"
            cache_dir.mkdir()
            
            # Change to temp directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)
                with pytest.raises(ValueError, match="No cache directory found"):
                    find_cache_dir()
            finally:
                os.chdir(original_cwd)
    
    def test_find_cache_from_within_cache_dir(self):
        """Test finding cache when running from within cache/content directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_dir = temp_path / "mycache"
            cache_dir.mkdir()
            
            # Create cache.tsv
            tsv_file = cache_dir / "cache.tsv"
            tsv_file.write_text("# Cache file\n")
            
            # Create content subdirectory
            content_dir = cache_dir / "content"
            content_dir.mkdir()
            
            # Change to content directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(content_dir)
                result = find_cache_dir()
                # Should find parent cache directory
                assert result.resolve() == cache_dir.resolve()
            finally:
                os.chdir(original_cwd)
    
    def test_prefer_current_cache_directory(self):
        """Test that cache/cache.tsv in current directory is preferred"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create cache/cache.tsv in current directory
            current_cache = temp_path / "cache"
            current_cache.mkdir()
            current_tsv = current_cache / "cache.tsv"
            current_tsv.write_text("# Current cache\n")
            
            # Also create another cache in current directory
            other_cache = temp_path / "other_cache"
            other_cache.mkdir()
            other_tsv = other_cache / "cache.tsv"
            other_tsv.write_text("# Other cache\n")
            
            # Change to temp directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_path)
                result = find_cache_dir()
                # Should return relative path "cache" for current directory
                assert result == Path("cache")
            finally:
                os.chdir(original_cwd)