"""
url2md - URL analysis and classification tool

Generate Markdown reports from URLs through AI-powered content analysis,
summarization, and classification.
"""

__version__ = "0.1.0"
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

from .models import (
    URLInfo,
    load_urls_from_file,
)

from .cache import (
    Cache,
    CacheResult,
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
]

# Command modules are available as submodules:
# from url2md.fetch import main as fetch_main
# from url2md.summarize import main as summarize_main  
# from url2md.classify import main as classify_main
# from url2md.report import main as report_main