#!/usr/bin/env python3
"""
Unit tests for report.py module
"""

import tempfile
from pathlib import Path

import pytest
from url2md.report import calculate_tag_match_weight, classify_url_to_theme, generate_markdown_report, group_urls_by_tag_in_theme
from url2md.cache import Cache


class TestCalculateTagMatchWeight:
    """Tests for tag matching weight calculation"""
    
    def test_exact_match(self):
        """Test exact match cases"""
        assert calculate_tag_match_weight("linguistics", "linguistics") == 1.0
        assert calculate_tag_match_weight("Python", "Python") == 1.0
    
    def test_partial_match_url_in_theme(self):
        """Test when URL tag is contained in theme tag"""
        # "math" in "applied_math" = 4/12 ≈ 0.333
        result = calculate_tag_match_weight("math", "applied_math")
        assert abs(result - 0.333) < 0.01
        
        # "learn" in "machine_learning" = 5/16 = 0.3125
        result = calculate_tag_match_weight("learn", "machine_learning")
        assert abs(result - 0.3125) < 0.01
    
    def test_partial_match_theme_in_url(self):
        """Test when theme tag is contained in URL tag"""
        # "applied_math" contains "math" = 4/12 ≈ 0.333
        result = calculate_tag_match_weight("applied_math", "math")
        assert abs(result - 0.333) < 0.01
        
        # "machine_learning_algorithm" contains "machine_learning" = 16/26 ≈ 0.615
        result = calculate_tag_match_weight("machine_learning_algorithm", "machine_learning")
        assert abs(result - 0.615) < 0.01
    
    def test_no_match(self):
        """Test no match cases"""
        assert calculate_tag_match_weight("linguistics", "mathematics") == 0.0
        assert calculate_tag_match_weight("Python", "Java") == 0.0
        assert calculate_tag_match_weight("", "linguistics") == 0.0
        assert calculate_tag_match_weight("linguistics", "") == 0.0


class TestClassifyUrlToTheme:
    """Tests for URL classification to themes"""
    
    def setup_method(self):
        """Set up test data"""
        self.themes = [
            {
                "name": "Linguistics",
                "tags": ["linguistics", "phonology", "morphology", "syntax"]
            },
            {
                "name": "Mathematics", 
                "tags": ["mathematics", "statistics", "probability", "linear_algebra"]
            },
            {
                "name": "Programming",
                "tags": ["Python", "programming", "algorithm"]
            }
        ]
        
        self.theme_weights = {
            "Linguistics": 1.0,
            "Mathematics": 1.2,  # Higher weight
            "Programming": 1.0
        }
    
    def test_perfect_match(self):
        """Test perfect match cases"""
        url_summary = {
            "tags": ["linguistics", "phonology"]
        }
        theme, score = classify_url_to_theme(url_summary, self.themes)
        assert theme == "Linguistics"
        assert score == 2.0  # Two exact matches
    
    def test_partial_match(self):
        """Test partial match cases"""
        url_summary = {
            "tags": ["applied_linguistics", "mathematics"]
        }
        theme, score = classify_url_to_theme(url_summary, self.themes)
        # "applied_linguistics" vs "linguistics" gives partial score
        # "mathematics" vs "mathematics" = 1.0
        # With weight: Mathematics score = 1.0 * 1.2 = 1.2
        assert theme == "Mathematics"
    
    def test_theme_weights(self):
        """Test theme weight application"""
        url_summary = {
            "tags": ["math"]  # Partial match with "mathematics"
        }
        theme, score = classify_url_to_theme(url_summary, self.themes, self.theme_weights)
        # Should prefer Mathematics due to higher weight
        assert theme == "Mathematics"
    
    def test_no_match(self):
        """Test when no theme matches"""
        url_summary = {
            "tags": ["cooking", "travel"]
        }
        theme, score = classify_url_to_theme(url_summary, self.themes)
        assert theme is None
        assert score == 0.0
    
    def test_empty_tags(self):
        """Test empty tags case"""
        url_summary = {
            "tags": []
        }
        theme, score = classify_url_to_theme(url_summary, self.themes)
        assert theme is None
        assert score == 0.0
    
    def test_missing_tags(self):
        """Test missing tags field"""
        url_summary = {}
        theme, score = classify_url_to_theme(url_summary, self.themes)
        assert theme is None
        assert score == 0.0


class TestGroupUrlsByTagInTheme:
    """Tests for URL grouping by tags within themes"""
    
    def test_url_tag_order_priority(self):
        """Test that URL tag order is prioritized over theme tag order"""
        urls_with_scores = [
            ("https://example1.com", 1.0),
            ("https://example2.com", 0.8),
        ]
        
        theme_tags = ["AI", "Technology", "Research"]
        
        url_summaries = {
            "https://example1.com": {
                "tags": ["Research", "AI", "Technology"]  # Research comes first
            },
            "https://example2.com": {
                "tags": ["Technology", "AI"]  # Technology comes first
            }
        }
        
        result = group_urls_by_tag_in_theme(urls_with_scores, theme_tags, url_summaries)
        
        # URL1 should go to Research (its first tag)
        assert "Research" in result
        assert ("https://example1.com", 1.0) in result["Research"]
        
        # URL2 should go to Technology (its first tag)
        assert "Technology" in result
        assert ("https://example2.com", 0.8) in result["Technology"]
    
    def test_partial_match_grouping(self):
        """Test grouping with partial tag matches (both directions)"""
        urls_with_scores = [
            ("https://example1.com", 1.0),
            ("https://example2.com", 0.9),
            ("https://example3.com", 0.8),
        ]
        
        theme_tags = ["mathematics", "programming", "ling"]
        
        url_summaries = {
            "https://example1.com": {
                "tags": ["math", "computational"]  # "math" is contained in "mathematics"
            },
            "https://example2.com": {
                "tags": ["python_programming", "algorithm"]  # "python_programming" contains "programming"
            },
            "https://example3.com": {
                "tags": ["linguistics", "phonology"]  # "linguistics" contains "ling"
            }
        }
        
        result = group_urls_by_tag_in_theme(urls_with_scores, theme_tags, url_summaries)
        
        # URL1: "math" should match with "mathematics" (url tag in theme tag)
        assert "mathematics" in result
        assert ("https://example1.com", 1.0) in result["mathematics"]
        
        # URL2: "python_programming" should match with "programming" (theme tag in url tag)
        assert "programming" in result
        assert ("https://example2.com", 0.9) in result["programming"]
        
        # URL3: "linguistics" should match with "ling" (theme tag in url tag)
        assert "ling" in result
        assert ("https://example3.com", 0.8) in result["ling"]
    
    def test_untagged_urls(self):
        """Test handling of URLs without matching tags"""
        urls_with_scores = [
            ("https://example1.com", 1.0),
            ("https://example2.com", 0.8),
        ]
        
        theme_tags = ["AI", "Technology"]
        
        url_summaries = {
            "https://example1.com": {
                "tags": ["AI"]
            },
            "https://example2.com": {
                "tags": ["Biology", "Chemistry"]  # No matching tags
            }
        }
        
        result = group_urls_by_tag_in_theme(urls_with_scores, theme_tags, url_summaries)
        
        # URL1 should be in AI
        assert "AI" in result
        assert ("https://example1.com", 1.0) in result["AI"]
        
        # URL2 should be in _untagged
        assert "_untagged" in result
        assert ("https://example2.com", 0.8) in result["_untagged"]


class TestGenerateMarkdownReport:
    """Tests for Markdown report generation"""
    
    def test_basic_report_generation(self):
        """Test basic report generation"""
        url_classifications = {
            "https://example1.com": {"theme": "Linguistics", "score": 0.8},
            "https://example2.com": {"theme": "Programming", "score": 0.9}
        }
        
        classification_data = {
            "themes": [
                {
                    "theme_name": "Linguistics",
                    "theme_description": "Linguistics and language topics",
                    "tags": ["linguistics", "phonology"]
                },
                {
                    "theme_name": "Programming",
                    "theme_description": "Programming and software development",
                    "tags": ["Python", "programming"]
                }
            ]
        }
        
        url_summaries = {
            "https://example1.com": {
                "title": ["Linguistics Introduction"],
                "summary_one_line": "Basic linguistics concepts"
            },
            "https://example2.com": {
                "title": ["Python Tutorial"],
                "summary_one_line": "Learn Python programming"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = Cache(Path(temp_dir))
            report = generate_markdown_report(cache, url_classifications, classification_data, url_summaries)
        
        # Check basic structure
        assert "# Summary" in report
        assert "# Themes" in report
        assert "**Total URLs**: 2" in report
        assert "**Classified**: 2" in report
        assert "**Unclassified**: 0" in report
        assert "## Linguistics (1 URLs)" in report
        assert "## Programming (1 URLs)" in report
        assert "[Linguistics Introduction](https://example1.com)" in report
        assert "Basic linguistics concepts" in report
    
    def test_with_unclassified_urls(self):
        """Test report with unclassified URLs"""
        url_classifications = {
            "https://example1.com": {"theme": "Linguistics", "score": 0.8}
        }
        
        classification_data = {
            "themes": [
                {
                    "theme_name": "Linguistics",
                    "theme_description": "Linguistics and language topics",
                    "tags": ["linguistics"]
                }
            ]
        }
        
        url_summaries = {
            "https://example1.com": {
                "title": ["Linguistics Introduction"],
                "summary_one_line": "Basic linguistics concepts"
            },
            "https://example2.com": {
                "title": ["Unrelated Content"],
                "summary_one_line": "Some other content"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = Cache(Path(temp_dir))
            report = generate_markdown_report(cache, url_classifications, classification_data, url_summaries)
        
        assert "**Total URLs**: 2" in report
        assert "**Classified**: 1" in report
        assert "**Unclassified**: 1" in report
        assert "## Unclassified (1 URLs)" in report
        assert "[Unrelated Content](https://example2.com)" in report
    
    def test_empty_classifications(self):
        """Test empty classification results"""
        url_classifications = {}
        classification_data = {"themes": {}}
        url_summaries = {}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = Cache(Path(temp_dir))
            report = generate_markdown_report(cache, url_classifications, classification_data, url_summaries)
        
        assert "# Summary" in report
        assert "**Total URLs**: 0" in report
        assert "**Classified**: 0" in report
        assert "**Unclassified**: 0" in report


if __name__ == "__main__":
    pytest.main([__file__])