import requests

class DockerOllamaCLient:
    def __init__(self, host="localhost", port=11434):
        self.base_url = f"http://{host}:{port}"
        self.prompt = ""

    def generate(self, description: str, model, prompt: str):
            if prompt is None:
                prompt = self.prompt
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': model,
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
