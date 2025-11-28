"""
Base class for all agent clients.
Handles common functionality like base URL configuration from environment variables.
"""
import os
from urllib.parse import urlparse
from pathlib import Path
from dotenv import load_dotenv
from abc import ABC


# Load .env file if it exists (from project root)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class BaseAgentClient(ABC):
    """
    Base class for all agent clients.
    
    Handles:
    - Base URL configuration from environment variables
    - Common API methods (list_models, etc.)
    """
    
    def __init__(self):
        """
        Initialize agent client with base URL from environment or provided value.
        
        Environment variables (in order of precedence):
        1. AGENT_SERVER_URL - Full URL (e.g., http://localhost:11434)
        """

        # Try to get from environment variable
        base_url = os.getenv("AGENT_SERVER_URL")
        
        # Ensure the URL is properly formatted
        parsed = urlparse(base_url)
        if not parsed.scheme:
            base_url = f"http://{base_url}"
        
        self.base_url = base_url.rstrip('/')
    