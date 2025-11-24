import base64
import requests
import uuid
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

from src.agent.base_client import BaseAgentClient
from src.agent.enum import Model

@dataclass
class TestAction:
    action_type: str  # click, type, hover, scroll, wait, etc.
    element_description: str
    coordinates: Optional[tuple] = None  # (x, y) if available
    text_input: Optional[str] = None
    confidence: float = 1.0


class LlavaClient(BaseAgentClient):
    """
    Client for interacting with LLaVA (Large Language and Vision Assistant) models via Ollama.
    Supports image understanding and vision tasks.
    """
    
    def __init__(self):
        """
        Initialize LlavaClient.
        """
        super().__init__()
        self.session = {} # TODO: Move this session management to some static storage
        self.model = Model.LLAVA_LATEST.value

    def __create_session(self, session_id: str = None) -> str:
        """create a new chat session"""
        if session_id is None:
            session_id = str(uuid.uuid4())

        self.session[session_id] = {
            'messages': [],
            'step_count': 0
        }
        return session_id

    # ? This will got to image processing module (screenrecord, crop, etc.)
    def __image_to_base64(self, image_path: str) -> str:
        """Covert image to base64 for agent"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def __build_context(self, session_id: str) -> List[Dict]:
        """Build conversation context from session history"""
        if not self.session[session_id]['messages']:
            # First message - provide system context
            return [{
                "role": "system",
                "content": """You are a web testing AI agent. You analyze screenshots and provide specific actions for testing websites.
                Always return your responses as valid JSON arrays of action objects.
                Be precise about where to click/type based on visible elements."""
            }]
        
        return self.session[session_id]['messages']

    def _parse_actions(self, actions_json: str) -> List[TestAction]:
        """Parse JSON response into TestAction objects"""
        try:
            actions_data = json.loads(actions_json)
            actions = []
            
            for action_data in actions_data:
                action = TestAction(
                    action_type=action_data.get('action_type', 'click'),
                    element_description=action_data.get('element_description', ''),
                    text_input=action_data.get('text_input'),
                    confidence=action_data.get('confidence', 1.0),
                    coordinates=action_data.get('coordinates')
                )
                actions.append(action)
            
            return actions
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw response: {actions_json}")
            return []

    def get_action(self, session_id: str, image_path: str, description: str) -> List[TestAction]:
        """
        Analyse screenshot and return action
        """
        if session_id not in self.session:
            session_id = self.__create_session(session_id)

        image_base64 = self.__image_to_base64(image_path)
        context = self.__build_context(session_id)

        prompt = f"""
            The task is to {description}

            Analyze this website screenshot and provide the next actions to perform for testing.
            Focus on interactive elements like buttons, forms, links, and navigation.
            
            Return your response as a JSON array of actions. Each action should have:
            - action_type: "click", "type", "hover", "scroll", "wait", "navigate"
            - element_description: clear description of where to perform action
            - text_input: only for "type" actions, what text to enter
            - confidence: your confidence level (0.0 to 1.0)
            - coordinates: x and y coordinates where above action should happen (this should be float value)
            
            Example:
            [
              {{
                "action_type": "click",
                "element_description": "Login button in top right corner",
                "confidence": 0.9,
                "coordinates": (720, 345)
              }}
            ]
        """

        message = {
            "model": self.model,
            "messages": [
                *context,
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }
            ],
            "stream": False,
            "format": "json"  # Request JSON response
        }

        try:
            print(f"Sending message: {message}")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=message,
                timeout=1000  # Longer timeout for vision models
            )
            print(f"Response got from agent")
            
            if response.status_code == 200:
                result = response.json()
                actions = result['message']['content']
                
                # Parse JSON response
                # actions = self._parse_actions(actions_json)
                
                # Store in session history
                self.session[session_id]['messages'].append({
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                })
                self.session[session_id]['messages'].append({
                    "role": "assistant",
                    "content": actions
                })
                self.session[session_id]['step_count'] += 1
                
                return actions
            else:
                raise Exception(f"API error: {response.text}")
                
        except Exception as e:
            print(f"Error analyzing screenshot: {e}")
            return []
