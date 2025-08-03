"""
AI Redirector - Intelligent AI model routing and multitasking CLI tool
"""

__version__ = "0.1.0"
__author__ = "STAFE GROUP AB"

# Suppress urllib3 SSL warnings that can appear during installation
import warnings
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
except (ImportError, AttributeError):
    # If urllib3 not available or warning type doesn't exist, ignore
    pass