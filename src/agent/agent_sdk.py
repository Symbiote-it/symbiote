import requests

from enum import Enum

class Model(Enum):
    PHI3_MINI = "phi3"

class DockerOllamaClient:
    def __init__(self, host="localhost", port=11434):
        self.base_url = f"http://{host}:{port}"

    def generate(self, prompt: str, model: Model):
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': model.value,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3,
                        'top_p': 0.9
                    }
                }
            )

            if response.status_code == 200:
                return response.json()['response']
            else:
                raise Exception(f"Ollama error: {response.text}")
    
    def list_models(self):
        response = requests.get(f"{self.base_url}/api/tags")
        return response.json()
