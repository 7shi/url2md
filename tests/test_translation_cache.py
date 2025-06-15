#!/usr/bin/env python3
"""
Test translation cache functionality
"""

import tempfile
from pathlib import Path

from url2md.translation_cache import TranslationCache


def test_translation_cache_basic_operations():
    """Test basic translation cache operations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Create translation cache
        tc = TranslationCache(cache_dir)
        
        # Initially empty
        assert len(tc.get_all_translations()) == 0
        assert tc.get_translation('Summary', 'ja') is None
        assert not tc.has_translation('Summary', 'ja')
        
        # Add translations
        tc.add_translation('Summary', 'ja', '概要')
        tc.add_translation('Themes', 'ja', 'テーマ')
        tc.add_translation('Summary', 'zh', '摘要')
        
        # Test retrieval
        assert len(tc.get_all_translations()) == 3
        assert tc.get_translation('Summary', 'ja') == '概要'
        assert tc.get_translation('Themes', 'ja') == 'テーマ'
        assert tc.get_translation('Summary', 'zh') == '摘要'
        assert tc.has_translation('Summary', 'ja')
        assert tc.has_translation('Summary', 'zh')
        assert not tc.has_translation('Missing', 'ja')


def test_translation_cache_persistence():
    """Test translation cache persistence across instances"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Create and populate cache
        tc1 = TranslationCache(cache_dir)
        tc1.add_translation('Summary', 'ja', '概要')
        tc1.add_translation('Themes', 'ja', 'テーマ')
        tc1.add_translation('Total URLs', 'ja', '総URL数')
        tc1.save()
        
        # Verify TSV file exists and has content
        assert tc1.tsv_path.exists()
        tsv_content = tc1.tsv_path.read_text()
        assert 'English\tLanguage\tTranslation' in tsv_content
        assert 'Summary\tja\t概要' in tsv_content
        assert 'Themes\tja\tテーマ' in tsv_content
        
        # Create new instance and verify data loaded
        tc2 = TranslationCache(cache_dir)
        assert len(tc2.get_all_translations()) == 3
        assert tc2.get_translation('Summary', 'ja') == '概要'
        assert tc2.get_translation('Themes', 'ja') == 'テーマ'
        assert tc2.get_translation('Total URLs', 'ja') == '総URL数'


def test_translation_cache_tsv_format():
    """Test TSV file format and structure"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        tc = TranslationCache(cache_dir)
        tc.add_translation('Summary', 'ja', '概要')
        tc.add_translation('Themes', 'zh', '主题')
        tc.save()
        
        # Check TSV structure
        lines = tc.tsv_path.read_text().strip().split('\n')
        assert len(lines) == 3  # Header + 2 data lines
        
        # Check header
        header = lines[0].split('\t')
        assert header == ['English', 'Language', 'Translation']
        
        # Check data lines
        data_lines = [line.split('\t') for line in lines[1:]]
        assert len(data_lines) == 2
        
        # Verify all entries are present (order may vary)
        entries = {(row[0], row[1]): row[2] for row in data_lines}
        assert entries[('Summary', 'ja')] == '概要'
        assert entries[('Themes', 'zh')] == '主题'


def test_translation_cache_sanitization():
    """Test sanitization of fields with tabs and newlines"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        tc = TranslationCache(cache_dir)
        
        # Add translation with problematic characters
        problematic_text = "Text with\ttabs and\nnewlines\r\nand more"
        tc.add_translation('Test\tTerm', 'ja\nLang', problematic_text)
        tc.save()
        
        # Verify sanitization in TSV file
        tsv_content = tc.tsv_path.read_text()
        
        # Should not contain raw tabs or newlines in data
        lines = tsv_content.split('\n')
        data_line = lines[1]  # Skip header
        
        # Tabs should be preserved as field separators, but content should be sanitized
        fields = data_line.split('\t')
        assert len(fields) == 3
        assert '\t' not in fields[0].replace(' ', '')  # Original tabs replaced with spaces
        assert '\n' not in fields[1]  # Original newlines replaced with spaces
        assert '\r' not in fields[2]  # Original carriage returns replaced with spaces
        
        # Reload and verify data integrity
        tc2 = TranslationCache(cache_dir)
        retrieved = tc2.get_translation('Test Term', 'ja Lang')  # Sanitized keys
        assert retrieved is not None
        assert '\t' not in retrieved
        assert '\n' not in retrieved


def test_translation_cache_clear():
    """Test clearing translation cache"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        tc = TranslationCache(cache_dir)
        tc.add_translation('Summary', 'ja', '概要')
        tc.add_translation('Themes', 'ja', 'テーマ')
        
        assert len(tc.get_all_translations()) == 2
        
        tc.clear()
        assert len(tc.get_all_translations()) == 0
        assert tc.get_translation('Summary', 'ja') is None


def test_translation_cache_multiple_languages():
    """Test handling multiple languages for same term"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        tc = TranslationCache(cache_dir)
        
        # Add same term in multiple languages
        tc.add_translation('Summary', 'ja', '概要')
        tc.add_translation('Summary', 'zh', '摘要')
        tc.add_translation('Summary', 'fr', 'Résumé')
        tc.add_translation('Summary', 'es', 'Resumen')
        
        # Verify all are stored correctly
        assert tc.get_translation('Summary', 'ja') == '概要'
        assert tc.get_translation('Summary', 'zh') == '摘要'
        assert tc.get_translation('Summary', 'fr') == 'Résumé'
        assert tc.get_translation('Summary', 'es') == 'Resumen'
        
        # Test persistence
        tc.save()
        tc2 = TranslationCache(cache_dir)
        assert len(tc2.get_all_translations()) == 4
        assert tc2.get_translation('Summary', 'fr') == 'Résumé'


def test_translation_cache_empty_file():
    """Test behavior with empty or non-existent TSV file"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        
        # Create cache with non-existent file
        tc = TranslationCache(cache_dir)
        assert len(tc.get_all_translations()) == 0
        assert not tc.tsv_path.exists()
        
        # Add and save to create file
        tc.add_translation('Test', 'ja', 'テスト')
        tc.save()
        assert tc.tsv_path.exists()
        
        # Verify content
        tc2 = TranslationCache(cache_dir)
        assert len(tc2.get_all_translations()) == 1
        assert tc2.get_translation('Test', 'ja') == 'テスト'