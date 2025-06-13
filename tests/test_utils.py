#!/usr/bin/env python3
"""
Tests for utils.py HTML processing functions
"""

import pytest
from url2md.utils import extract_body_content, extract_html_title


class TestExtractBodyContent:
    """Tests for extract_body_content function"""
    
    def test_basic_body_extraction(self):
        """Test basic body content extraction"""
        html = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Title</h1>
            <p>Content</p>
        </body>
        </html>
        """
        result = extract_body_content(html)
        assert "<h1>Title</h1>" in result
        assert "<p>Content</p>" in result
        assert "<title>Test</title>" not in result
    
    def test_script_and_style_removal(self):
        """Test script and style tag removal"""
        html = """
        <body>
            <h1>Title</h1>
            <script>alert('test');</script>
            <p>Content</p>
            <style>body { color: red; }</style>
            <div>More content</div>
        </body>
        """
        result = extract_body_content(html)
        assert "<h1>Title</h1>" in result
        assert "<p>Content</p>" in result
        assert "<div>More content</div>" in result
        assert "alert('test');" not in result
        assert "color: red;" not in result
    
    def test_case_insensitive_tags(self):
        """Test case-insensitive tag processing"""
        html = """
        <BODY>
            <H1>Title</H1>
            <SCRIPT>alert('test');</SCRIPT>
            <P>Content</P>
            <STYLE>body { color: red; }</STYLE>
        </BODY>
        """
        result = extract_body_content(html)
        assert "<H1>Title</H1>" in result
        assert "<P>Content</P>" in result
        assert "alert('test');" not in result
        assert "color: red;" not in result
    
    def test_no_body_tag(self):
        """Test processing when no body tag exists"""
        html = """
        <h1>Title</h1>
        <script>alert('test');</script>
        <p>Content</p>
        """
        result = extract_body_content(html)
        assert "<h1>Title</h1>" in result
        assert "<p>Content</p>" in result
        assert "alert('test');" not in result
    
    def test_nested_script_tags(self):
        """Test nested script tag handling"""
        html = """
        <body>
            <div>
                <script>
                    function test() {
                        console.log('nested');
                    }
                </script>
                <p>Content</p>
            </div>
        </body>
        """
        result = extract_body_content(html)
        assert "<p>Content</p>" in result
        assert "function test()" not in result
        assert "console.log" not in result
    
    def test_body_with_attributes(self):
        """Test body tag with attributes"""
        html = """
        <body class="main" id="content">
            <h1>Title</h1>
            <p>Content</p>
        </body>
        """
        result = extract_body_content(html)
        assert "<h1>Title</h1>" in result
        assert "<p>Content</p>" in result
    
    def test_body_extraction_error_handling(self):
        """Test error handling in body extraction"""
        # Test with None input that should trigger an error
        result = extract_body_content(None)
        # Should return the original input on error gracefully
        assert result is None


class TestExtractHtmlTitle:
    """Tests for extract_html_title function"""
    
    def test_basic_title_extraction(self):
        """Test basic title extraction"""
        html = """
        <html>
        <head><title>Test Page Title</title></head>
        <body>Content</body>
        </html>
        """
        result = extract_html_title(html)
        assert result == "Test Page Title"
    
    def test_title_with_html_entities(self):
        """Test title with HTML entities"""
        html = """
        <html>
        <head><title>Test &amp; Example &lt;Page&gt; &quot;Title&quot;</title></head>
        <body>Content</body>
        </html>
        """
        result = extract_html_title(html)
        assert result == 'Test & Example <Page> "Title"'
    
    def test_case_insensitive_title(self):
        """Test case-insensitive title extraction"""
        html = """
        <HTML>
        <HEAD><TITLE>Uppercase Title</TITLE></HEAD>
        <BODY>Content</BODY>
        </HTML>
        """
        result = extract_html_title(html)
        assert result == "Uppercase Title"
    
    def test_title_with_attributes(self):
        """Test title tag with attributes"""
        html = """
        <html>
        <head><title lang="en">Attributed Title</title></head>
        <body>Content</body>
        </html>
        """
        result = extract_html_title(html)
        assert result == "Attributed Title"
    
    def test_multiline_title(self):
        """Test multiline title"""
        html = """
        <html>
        <head>
        <title>
            Multi Line
            Title
        </title>
        </head>
        <body>Content</body>
        </html>
        """
        result = extract_html_title(html)
        assert result == "Multi Line\n            Title"
    
    def test_no_title_tag(self):
        """Test when no title tag exists"""
        html = """
        <html>
        <head></head>
        <body>Content without title</body>
        </html>
        """
        result = extract_html_title(html)
        assert result == ""
    
    def test_empty_title(self):
        """Test empty title tag"""
        html = """
        <html>
        <head><title></title></head>
        <body>Content</body>
        </html>
        """
        result = extract_html_title(html)
        assert result == ""
    
    def test_title_with_whitespace(self):
        """Test title with leading/trailing whitespace"""
        html = """
        <html>
        <head><title>   Spaced Title   </title></head>
        <body>Content</body>
        </html>
        """
        result = extract_html_title(html)
        assert result == "Spaced Title"
    
    def test_title_extraction_error_handling(self):
        """Test error handling in title extraction"""
        # Test with None input that should trigger an error
        result = extract_html_title(None)
        # Should return empty string on error gracefully
        assert result == ""