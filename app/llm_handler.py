import requests
from abc import ABC, abstractmethod


class LLMHandler(ABC):
    @abstractmethod
    def analyze_code(self, code):
        """
        Abstract method to be implemented by concrete LLM handlers.
        """
        pass


class OllamaHandler(LLMHandler):
    def __init__(self, llm_url="http://localhost:11434/api/generate"):
        self.llm_url = llm_url

    def analyze_code(self, code):
        """
        Sends the code to Ollama for analysis.
        """
        payload = {
            "prompt": f"Analyze this Python code: \n```\n{code}\n```\n\nProvide a structured response suitable for generating documentation.",
            "model": "llama3.2",
            "options": {"temperature": 0},
            "stream": False,
        }

        response = requests.post(self.llm_url, json=payload)
        response.raise_for_status()
        
        return response.json()


# Example of adding another LLM (hypothetical 'OtherLLM')
class OtherLLMHandler(LLMHandler):
    def __init__(self, api_key, api_url):
        # ... specific initialisation
        pass

    def analyze_code(self, code):
        # ...  implementation for OtherLLM API interaction
        pass
