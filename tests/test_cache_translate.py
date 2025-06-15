#!/usr/bin/env python3
"""
Test cache integration with translation functionality
"""

import tempfile
from pathlib import Path

from url2md.cache import Cache


def test_cache_translation_integration():
    """Test integrated translation cache functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Create cache with integrated translation cache
        cache = Cache(cache_dir)
        
        # Test translation cache access
        tc = cache.translation_cache
        
        # Add some translations
        tc.add_translation('Summary', 'Japanese', '概要')
        tc.add_translation('Themes', 'Japanese', 'テーマ')
        
        assert len(tc.get_all_translations()) == 2
        assert tc.get_translation('Summary', 'Japanese') == '概要'
        
        # Save translation cache (simulate classify operation)
        tc.save()
        
        # Create new cache instance (simulate report operation)
        cache2 = Cache(cache_dir)
        tc2 = cache2.translation_cache
        
        assert len(tc2.get_all_translations()) == 2
        assert tc2.get_translation('Summary', 'Japanese') == '概要'
        assert tc2.get_translation('Themes', 'Japanese') == 'テーマ'


def test_cache_translation_file_creation():
    """Test translation cache file creation workflow"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Initially no translation file exists
        terms_path = cache_dir / "terms.tsv"
        assert not terms_path.exists()
        
        # Create cache - translation cache loads but file doesn't exist yet
        cache = Cache(cache_dir)
        tc = cache.translation_cache
        assert len(tc.get_all_translations()) == 0
        assert not terms_path.exists()
        
        # Add translations and save (simulate classify operation)
        tc.add_translation('Summary', 'Japanese', '概要')
        tc.add_translation('Total URLs', 'Japanese', '総URL数')
        tc.save()
        
        # Now terms.tsv should exist
        assert terms_path.exists()
        
        # Verify content
        content = terms_path.read_text()
        assert 'English\tLanguage\tTranslation' in content
        assert 'Summary\tJapanese\t概要' in content


def test_cache_files_separation():
    """Test that cache.tsv and terms.tsv are independent"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        cache = Cache(cache_dir)
        
        # Check both cache files exist/will be created independently
        cache_tsv = cache.tsv_path  # cache.tsv
        terms_tsv = cache.translation_cache.tsv_path  # terms.tsv
        
        assert cache_tsv != terms_tsv
        assert cache_tsv.name == "cache.tsv"
        assert terms_tsv.name == "terms.tsv"
        assert cache_tsv.parent == terms_tsv.parent  # Same directory


def test_cache_translation_workflow_simulation():
    """Test typical classify -> report workflow with translations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Simulate classify command with language
        cache_classify = Cache(cache_dir)
        
        # During classify: translations are generated and cached
        tc = cache_classify.translation_cache
        tc.add_translation('Summary', 'French', 'Résumé')
        tc.add_translation('Themes', 'French', 'Thèmes')
        tc.add_translation('Total URLs', 'French', 'URLs totales')
        tc.add_translation('Classified', 'French', 'Classifié')
        tc.add_translation('Unclassified', 'French', 'Non classifié')
        tc.save()  # Only classify saves translation cache
        
        # Simulate report command (new process)
        cache_report = Cache(cache_dir)
        
        # Report can access cached translations without LLM calls
        tc_report = cache_report.translation_cache
        assert tc_report.get_translation('Summary', 'French') == 'Résumé'
        assert tc_report.get_translation('Themes', 'French') == 'Thèmes'
        assert tc_report.get_translation('Total URLs', 'French') == 'URLs totales'
        
        # Report doesn't save translation cache
        assert len(tc_report.get_all_translations()) == 5


def test_cache_translation_multiple_languages():
    """Test caching translations for multiple languages"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        cache = Cache(cache_dir)
        tc = cache.translation_cache
        
        # Add translations for multiple languages
        tc.add_translation('Summary', 'Japanese', '概要')
        tc.add_translation('Summary', 'French', 'Résumé')
        tc.add_translation('Summary', 'Spanish', 'Resumen')
        
        tc.add_translation('Themes', 'Japanese', 'テーマ')
        tc.add_translation('Themes', 'French', 'Thèmes')
        
        tc.save()
        
        # Reload and verify all languages preserved
        cache2 = Cache(cache_dir)
        tc2 = cache2.translation_cache
        
        assert len(tc2.get_all_translations()) == 5
        assert tc2.get_translation('Summary', 'Japanese') == '概要'
        assert tc2.get_translation('Summary', 'French') == 'Résumé'
        assert tc2.get_translation('Summary', 'Spanish') == 'Resumen'
        assert tc2.get_translation('Themes', 'Japanese') == 'テーマ'
        assert tc2.get_translation('Themes', 'French') == 'Thèmes'