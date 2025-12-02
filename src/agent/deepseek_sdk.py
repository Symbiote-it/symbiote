import requests
import json
from typing import List, Optional
from dataclasses import dataclass

from src.agent.base_client import BaseAgentClient
from src.agent.enum import Model
from src.db import session_manager


@dataclass
class TestAction:
    action_type: str  # click, type, hover, scroll, wait, etc.
    element_description: str
    coordinates: Optional[tuple] = None  # (x, y) if available
    text_input: Optional[str] = None
    confidence: float = 1.0


class DeepSeekClient(BaseAgentClient):
    """
    Client for interacting with DeepSeek R1 models via Ollama.
    Supports text-based web testing without image inputs.
    Uses website URLs instead of screenshots.
    """
    
    SYSTEM_PROMPT = """You are a web testing AI agent. You analyze websites and provide specific actions for testing web applications.
Always return your responses as valid JSON objects with action information.
Be precise about where to click/type based on website structure and common UI patterns.
Since you don't have visual access, use your knowledge of typical website layouts and element descriptions."""
    
    def __init__(self):
        """Initialize DeepSeekClient."""
        super().__init__()
        self.model = Model.DEEPSEEK_R1.value

    def _ensure_system_prompt(self, chat_id: int) -> None:
        """Ensure system prompt exists in chat, add if empty"""
        context = session_manager.get_context(chat_id)
        if not context:
            session_manager.add_message(chat_id, "system", self.SYSTEM_PROMPT)

    def _parse_actions(self, actions_json: str) -> List[TestAction]:
        """Parse JSON response into TestAction objects"""
        try:
            actions_data = json.loads(actions_json)
            if isinstance(actions_data, dict):
                actions_data = [actions_data]
            
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

    def get_action(self, chat_id: int, website_url: str, description: str) -> str:
        """
        Analyze website URL and return action based on description.
        
        Args:
            chat_id: Chat ID for maintaining conversation context (from session_manager)
            website_url: URL of the website to test (e.g., "https://github.com")
            description: Description of what action to perform
            
        Returns:
            JSON string containing the action to perform
        """
        # Ensure system prompt is set
        self._ensure_system_prompt(chat_id)

        prompt = f"""
The task is to {description}

Website URL: {website_url}

Analyze this website and provide the next one action to perform for testing.
Focus on interactive elements like buttons, forms, links, and navigation.
Use your knowledge of common website layouts and UI patterns.

Return your response as a JSON object with a single action. Action should have:
- action_type: "click", "type", "hover", "navigate", "scroll"
- element_description: clear description of where to perform action (e.g., "Sign in button in top right", "Search input field in header")
- text_input: only for "type" actions, what text to enter (Optional)
- confidence: your confidence level (0.0 to 1.0)
- coordinates: x and y coordinates where above action should happen (this should be pixel value and only should have x and y value)
Note: Since you don't have visual access, provide estimated coordinates based on typical website layouts.

Example:
{{
"action_type": "click",
"element_description": "Sign in button in top right corner",
"confidence": 0.85,
"coordinates": [1200, 50]
}}

Or for typing:
{{
"action_type": "type",
"element_description": "Search input field in the header",
"text_input": "python",
"confidence": 0.9,
"coordinates": [600, 100]
}}
"""
        # Store user message
        session_manager.add_message(chat_id, "user", prompt)
        
        # Get full context for LLM
        context = session_manager.get_context(chat_id)

        message = {
            "model": self.model,
            "messages": context,
            "stream": False,
            "format": "json"
        }

        try:
            print(f"Sending request to DeepSeek R1 for website: {website_url}")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=message,
                timeout=1000
            )
            print(f"Response received from agent")
            
            if response.status_code == 200:
                result = response.json()
                actions = result['message']['content']
                
                # Store assistant response
                session_manager.add_message(
                    chat_id, 
                    "assistant", 
                    actions, 
                    agent_type="deepseek-r1"
                )
                
                return actions
            else:
                raise Exception(f"API error: {response.text}")
                
        except Exception as e:
            print(f"Error analyzing website: {e}")
            return "{}"
