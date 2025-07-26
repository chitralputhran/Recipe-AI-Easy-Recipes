"""
LLM Service for Recipe AI.
Handles interactions with language models.
"""

from typing import Dict, Any
import json
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class LLMService:
    """Service for managing LLM interactions."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4", timeout: float = 120.0, max_retries: int = 3):
        """Initialize LLM service with configuration."""
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create default LLM client
        self.client = ChatOpenAI(
            model=model_name,
            temperature=0.3,
            openai_api_key=api_key,
            max_tokens=3000,
            timeout=timeout,
            max_retries=max_retries
        )
    
    def generate_json_response(self, system_prompt: str, user_prompt: str, client_type: str = "default") -> Dict[str, Any]:
        """Generate JSON response and parse it."""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.client.invoke(messages)
            return json.loads(response.content)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise Exception(f"JSON generation failed: {e}")
