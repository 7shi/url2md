#!/usr/bin/env python3
"""
Translation cache management for url2md package

Handles caching of translated terms to avoid repeated LLM calls.
"""

from pathlib import Path
from typing import Dict, Optional

from .tsv_manager import TSVManager


class TranslationCache(TSVManager):
    """Translation cache management using TSV format: English\tLanguage\tTranslation"""
    
    def __init__(self, cache_dir: Path):
        """Initialize translation cache
        
        Args:
            cache_dir: Cache directory containing terms.tsv
        """
        self._translations: Dict[tuple, str] = {}  # (english, language) -> translation
        
        # Initialize TSV manager
        super().__init__(cache_dir / "terms.tsv")
        
        # Load existing translations
        self.load()
    
    def load(self) -> None:
        """Load translations from TSV file"""
        super().load()
        
        self._translations.clear()
        for row in self.data:
            if len(row) >= 3:
                english, language, translation = row[0], row[1], row[2]
                self._translations[(english, language)] = translation
    
    def save(self) -> None:
        """Save translations to TSV file"""
        # Prepare header and data
        self.header = ['English', 'Language', 'Translation']
        self.data = []
        
        # Convert translations to TSV rows
        for (english, language), translation in self._translations.items():
            row = [english, language, translation]
            self.data.append(row)
        
        # Save using parent class
        super().save()
    
    def get_translation(self, english: str, language: str) -> Optional[str]:
        """Get cached translation
        
        Args:
            english: English term
            language: Target language
            
        Returns:
            Cached translation or None if not found
        """
        return self._translations.get((english, language))
    
    def add_translation(self, english: str, language: str, translation: str) -> None:
        """Add translation to cache
        
        Args:
            english: English term
            language: Target language
            translation: Translated term
        """
        self._translations[(english, language)] = translation
    
    def has_translation(self, english: str, language: str) -> bool:
        """Check if translation exists in cache
        
        Args:
            english: English term
            language: Target language
            
        Returns:
            True if translation exists
        """
        return (english, language) in self._translations
    
    def get_all_translations(self) -> Dict[tuple, str]:
        """Get all cached translations
        
        Returns:
            Dictionary mapping (english, language) tuples to translations
        """
        return self._translations.copy()
    
    def clear(self) -> None:
        """Clear all translations from memory"""
        self._translations.clear()