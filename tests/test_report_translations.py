#!/usr/bin/env python3
"""
Test report generation with translation functionality
"""

import tempfile
from pathlib import Path

from url2md.report import generate_markdown_report
from url2md.cache import Cache


class TestReportTranslations:
    """Tests for translation functionality in report generation"""
    
    def test_with_translations(self):
        """Test report generation with translations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = Cache(cache_dir)
            
            # Setup translation cache
            tc = cache.translation_cache
            tc.add_translation("Summary", "Japanese", "概要")
            tc.add_translation("Themes", "Japanese", "テーマ")
            tc.add_translation("Total URLs", "Japanese", "合計URL数")
            tc.add_translation("Classified", "Japanese", "分類済")
            tc.add_translation("Unclassified", "Japanese", "未分類")
            tc.add_translation("URLs", "Japanese", "URL")
            tc.add_translation("Other", "Japanese", "その他")
            
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
                "language": "Japanese"
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

            report = generate_markdown_report(cache, url_classifications, classification_data, url_summaries)

            # Check translated headers
            assert "# 概要" in report
            assert "# テーマ" in report
            assert "合計URL数" in report
            assert "分類済" in report
            assert "未分類" in report
            assert "URL" in report

    def test_with_partial_translations(self):
        """Test report generation with partial translations (some terms missing)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = Cache(cache_dir)
            
            # Setup partial translation cache (only Summary translated)
            tc = cache.translation_cache
            tc.add_translation("Summary", "Japanese", "概要")
            # Other terms not translated
            
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
                "language": "Japanese"
            }

            url_summaries = {
                "https://example1.com": {
                    "title": ["Linguistics Introduction"],
                    "summary_one_line": "Basic linguistics concepts"
                }
            }

            report = generate_markdown_report(cache, url_classifications, classification_data, url_summaries)

            # Check mixed translations (translated where available, English fallback)
            assert "# 概要" in report  # Translated
            assert "# Themes" in report  # English fallback
            assert "Total URLs" in report  # English fallback

    def test_with_unclassified_urls_and_translations(self):
        """Test report with unclassified URLs and translations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = Cache(cache_dir)
            
            # Setup translation cache
            tc = cache.translation_cache
            tc.add_translation("Summary", "Japanese", "概要")
            tc.add_translation("Themes", "Japanese", "テーマ")
            tc.add_translation("Total URLs", "Japanese", "合計URL数")
            tc.add_translation("Classified", "Japanese", "分類済")
            tc.add_translation("Unclassified", "Japanese", "未分類")
            tc.add_translation("URLs", "Japanese", "URL")
            
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
                "language": "Japanese"
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

            report = generate_markdown_report(cache, url_classifications, classification_data, url_summaries)

            # Check translated headers including unclassified section
            assert "# 概要" in report
            assert "# テーマ" in report
            assert "## 未分類" in report
            assert "合計URL数" in report

    def test_with_subsections_and_translations(self):
        """Test report with theme subsections and translations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = Cache(cache_dir)
            
            # Setup translation cache
            tc = cache.translation_cache
            tc.add_translation("Summary", "Japanese", "概要")
            tc.add_translation("Themes", "Japanese", "テーマ")
            tc.add_translation("Total URLs", "Japanese", "合計URL数")
            tc.add_translation("Classified", "Japanese", "分類済")
            tc.add_translation("URLs", "Japanese", "URL")
            tc.add_translation("Other", "Japanese", "その他")
            
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
                "language": "Japanese"
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

            report = generate_markdown_report(cache, url_classifications, classification_data, url_summaries,
                                            theme_subsections=["Programming"])

            # Check translated headers and subsections
            assert "# 概要" in report
            assert "# テーマ" in report
            assert "URL" in report
            assert "### その他" in report  # "Other" subsection translated

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
        }

        url_summaries = {
            "https://example1.com": {
                "title": ["Linguistics Introduction"],
                "summary_one_line": "Basic linguistics concepts"
            }
        }

        # No cache provided, should use English
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = Cache(Path(temp_dir))
            report = generate_markdown_report(cache, url_classifications, classification_data, url_summaries)

        # Check English headers (no translations available)
        assert "# Summary" in report
        assert "# Themes" in report
        assert "Total URLs" in report
        assert "Classified" in report
        assert "Unclassified" in report