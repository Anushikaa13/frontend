"""
Configuration file for Streamlit app
"""
import os

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 10

# Streamlit Configuration
CACHE_TTL = 60
PAGE_TITLE = "Product Management App"
LAYOUT = "wide"
