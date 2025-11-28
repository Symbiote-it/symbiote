import requests
from src.agent.base_client import BaseAgentClient
from src.agent.enum import Model


class Phi3Client(BaseAgentClient):
    """
    Client for interacting with Phi3 models via Ollama.
    """
    
    def __init__(self):
        """
        Initialize Phi3Client.
        """
        super().__init__()

    def generate(self, prompt: str, model: Model, temperature: float = 0.3, top_p: float = 0.9, stream: bool = False):
        """
        Generate a response using Phi3 model.
        
        Args:
            prompt: The prompt to send to the model
            model: The Model enum value to use
            temperature: Sampling temperature (default: 0.3)
            top_p: Top-p sampling parameter (default: 0.9)
            stream: Whether to stream the response (default: False)
            
        Returns:
            Generated response text
        """
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                'model': model.value,
                'prompt': prompt,
                'stream': stream,
                'options': {
                    'temperature': temperature,
                    'top_p': top_p
                }
            },
            stream=stream
        )

        if response.status_code == 200:
            if stream:
                return response
            else:
                return response.json()['response']
        else:
            raise Exception(f"Ollama error: {response.text}")
