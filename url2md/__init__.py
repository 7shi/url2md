"""
url2md - URL analysis and classification tool

Generate Markdown reports from URLs through AI-powered content analysis,
summarization, and classification.
"""

from importlib.metadata import version

__version__ = version("url2md")
__author__ = "url2md contributors"
__license__ = "CC0-1.0"

from .gemini import (
    models,
    client,
    config_text,
    build_schema_from_json,
    config_from_schema,
    generate_content_retry,
    upload_file,
    delete_file,
)

from .utils import (
    extract_body_content,
    extract_html_title,
)

from .download import (
    PLAYWRIGHT_AVAILABLE,
    download,
    is_text,
    user_agent,
)

from .urlinfo import (
    URLInfo,
    load_urls_from_file,
)

from .cache import (
    Cache,
    CacheResult,
)

from .terminal import (
    bold,
    convert_markdown,
    MarkdownStreamConverter,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    
    # Gemini API
    "models",
    "client", 
    "config_text",
    "build_schema_from_json",
    "config_from_schema",
    "generate_content_retry",
    "upload_file",
    "delete_file",
    
    # HTML utilities
    "extract_body_content",
    "extract_html_title",
    
    # Download utilities
    "PLAYWRIGHT_AVAILABLE",
    "download",
    "is_text",
    "user_agent",
    
    # Models and cache
    "URLInfo",
    "load_urls_from_file",
    "Cache",
    "CacheResult",
    
    # Terminal utilities
    "bold",
    "convert_markdown",
    "MarkdownStreamConverter",
]

# Function modules are available as submodules:
# from url2md.fetch import fetch_urls
# from url2md.summarize import summarize_urls
# from url2md.classify import extract_tags, classify_tags_with_llm
# from url2md.report import generate_markdown_report
