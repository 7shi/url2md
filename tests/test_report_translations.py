#!/usr/bin/env python3
"""
Unit tests for report translation functionality
"""

import pytest
from url2md.report import generate_markdown_report


class TestReportTranslations:
    """Tests for translation functionality in report generation"""
    
    def test_with_translations(self):
        """Test report generation with translations"""
        url_classifications = {
            "https://example1.com": {"theme": "Linguistics", "score": 0.8},
            "https://example2.com": {"theme": "Programming", "score": 0.9}
        }
        
        classification_data = {
            "themes": [
                {
                    "theme_name": "Linguistics",
                    "theme_description": "言語学とその関連分野",
                    "tags": ["linguistics", "language"]
                },
                {
                    "theme_name": "Programming", 
                    "theme_description": "プログラミングと開発",
                    "tags": ["programming", "development"]
                }
            ],
            "translations": {
                "Summary": "概要",
                "Themes": "テーマ",
                "Total URLs": "合計URL数",
                "Classified": "分類済",
                "Unclassified": "未分類",
                "URLs": "URL",
                "Other": "その他"
            }
        }
        
        url_summaries = {
            "https://example1.com": {
                "title": ["言語学入門"],
                "summary_one_line": "基本的な言語学の概念"
            },
            "https://example2.com": {
                "title": ["Pythonチュートリアル"],
                "summary_one_line": "Pythonプログラミングを学ぶ"
            }
        }
        
        report = generate_markdown_report(url_classifications, classification_data, url_summaries)
        
        # Check translated headers
        assert "# 概要" in report
        assert "# テーマ" in report
        assert "**合計URL数**: 2" in report
        assert "**分類済**: 2" in report
        assert "**未分類**: 0" in report
        assert "## Linguistics (1 URL)" in report
        assert "## Programming (1 URL)" in report
        assert "[言語学入門](https://example1.com)" in report
        assert "基本的な言語学の概念" in report
    
    def test_with_partial_translations(self):
        """Test report generation with partial translations (some terms missing)"""
        url_classifications = {
            "https://example1.com": {"theme": "Linguistics", "score": 0.8}
        }
        
        classification_data = {
            "themes": [
                {
                    "theme_name": "Linguistics",
                    "theme_description": "Language studies",
                    "tags": ["linguistics"]
                }
            ],
            "translations": {
                "Summary": "概要",
                # Missing other translations
            }
        }
        
        url_summaries = {
            "https://example1.com": {
                "title": ["Linguistics Introduction"],
                "summary_one_line": "Basic linguistics concepts"
            }
        }
        
        report = generate_markdown_report(url_classifications, classification_data, url_summaries)
        
        # Check mixed translations (translated where available, English fallback)
        assert "# 概要" in report  # Translated
        assert "# Themes" in report  # English fallback
        assert "**Total URLs**: 1" in report  # English fallback
        assert "**Classified**: 1" in report  # English fallback
    
    def test_with_unclassified_urls_and_translations(self):
        """Test report with unclassified URLs and translations"""
        url_classifications = {
            "https://example1.com": {"theme": "Linguistics", "score": 0.8}
        }
        
        classification_data = {
            "themes": [
                {
                    "theme_name": "Linguistics",
                    "theme_description": "言語学関連",
                    "tags": ["linguistics"]
                }
            ],
            "translations": {
                "Summary": "概要",
                "Themes": "テーマ",
                "Total URLs": "合計URL数",
                "Classified": "分類済",
                "Unclassified": "未分類",
                "URLs": "URL"
            }
        }
        
        url_summaries = {
            "https://example1.com": {
                "title": ["言語学入門"],
                "summary_one_line": "基本的な言語学の概念"
            },
            "https://example2.com": {
                "title": ["無関係なコンテンツ"],
                "summary_one_line": "その他のコンテンツ"
            }
        }
        
        report = generate_markdown_report(url_classifications, classification_data, url_summaries)
        
        # Check translated headers including unclassified section
        assert "# 概要" in report
        assert "# テーマ" in report
        assert "**合計URL数**: 2" in report
        assert "**分類済**: 1" in report
        assert "**未分類**: 1" in report
        assert "## Linguistics (1 URL)" in report
        assert "## 未分類 (1 URL)" in report
        assert "[無関係なコンテンツ](https://example2.com)" in report
    
    def test_with_subsections_and_translations(self):
        """Test report with theme subsections and translations"""
        url_classifications = {
            "https://example1.com": {"theme": "Programming", "score": 0.9},
            "https://example2.com": {"theme": "Programming", "score": 0.8},
            "https://example3.com": {"theme": "Programming", "score": 0.7}
        }
        
        classification_data = {
            "themes": [
                {
                    "theme_name": "Programming",
                    "theme_description": "プログラミング関連",
                    "tags": ["Python", "algorithm", "web"]
                }
            ],
            "translations": {
                "Summary": "概要",
                "Themes": "テーマ",
                "Total URLs": "合計URL数",
                "Classified": "分類済",
                "URLs": "URL",
                "Other": "その他"
            }
        }
        
        url_summaries = {
            "https://example1.com": {
                "title": ["Python基礎"],
                "summary_one_line": "Python入門",
                "tags": ["Python", "programming"]
            },
            "https://example2.com": {
                "title": ["アルゴリズム"],
                "summary_one_line": "データ構造とアルゴリズム",
                "tags": ["algorithm", "data_structure"]
            },
            "https://example3.com": {
                "title": ["その他のトピック"],
                "summary_one_line": "その他のプログラミング関連",
                "tags": ["misc", "tools"]
            }
        }
        
        report = generate_markdown_report(url_classifications, classification_data, url_summaries, 
                                        theme_subsections=["Programming"])
        
        # Check translated headers and subsections
        assert "# 概要" in report
        assert "# テーマ" in report
        assert "**合計URL数**: 3" in report
        assert "**分類済**: 3" in report
        assert "## Programming (3 URL)" in report
        assert "### その他" in report  # "Other" section should be translated
    
    def test_without_translations(self):
        """Test report generation without translations (English fallback)"""
        url_classifications = {
            "https://example1.com": {"theme": "Linguistics", "score": 0.8}
        }
        
        classification_data = {
            "themes": [
                {
                    "theme_name": "Linguistics",
                    "theme_description": "Language studies",
                    "tags": ["linguistics"]
                }
            ]
            # No translations section
        }
        
        url_summaries = {
            "https://example1.com": {
                "title": ["Linguistics Introduction"],
                "summary_one_line": "Basic linguistics concepts"
            }
        }
        
        report = generate_markdown_report(url_classifications, classification_data, url_summaries)
        
        # Check all English terms are used
        assert "# Summary" in report
        assert "# Themes" in report
        assert "**Total URLs**: 1" in report
        assert "**Classified**: 1" in report
        assert "**Unclassified**: 0" in report


if __name__ == "__main__":
    pytest.main([__file__])