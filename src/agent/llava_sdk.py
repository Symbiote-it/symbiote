import requests
from src.agent.base_client import BaseAgentClient
from src.agent.enum import Model


class LlavaClient(BaseAgentClient):
    """
    Client for interacting with LLaVA (Large Language and Vision Assistant) models via Ollama.
    Supports image understanding and vision tasks.
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize LlavaClient.
        
        Args:
            base_url: Optional base URL. If not provided, will use AGENT_SERVER_URL 
                     from environment, or default to http://localhost:11434
        """
        super().__init__(base_url)
    
    def generate(self, prompt: str, model: Model, images: list = None, temperature: float = 0.3, top_p: float = 0.9, stream: bool = False):
        """
        Generate a response using LLaVA model with optional image inputs.
        
        Args:
            prompt: The prompt to send to the model
            model: The Model enum value to use
            images: Optional list of image paths or base64 encoded images
            temperature: Sampling temperature (default: 0.3)
            top_p: Top-p sampling parameter (default: 0.9)
            stream: Whether to stream the response (default: False)
            
        Returns:
            Generated response text
        """
        payload = {
            'model': model.value,
            'prompt': prompt,
            'stream': stream,
            'options': {
                'temperature': temperature,
                'top_p': top_p
            }
        }
        
        # Add images if provided
        if images:
            payload['images'] = images
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            stream=stream
        )

        if response.status_code == 200:
            if stream:
                return response
            else:
                return response.json()['response']
        else:
            raise Exception(f"Ollama error: {response.text}")
