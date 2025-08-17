import requests
import json
import streamlit as st

class FreeAIService:
    """Free AI service using Ollama (local models)"""
    
    def __init__(self, model="llama3.1:8b"):
        self.model = model
        self.base_url = "http://localhost:11434"
    
    def summarize_text(self, text: str) -> str:
        """Summarize text using free local AI model."""
        try:
            # Truncate text if too long for local model
            if len(text) > 2000:
                text = text[:2000] + "... [truncated for faster processing]"
            
            prompt = f"Summarize this in 2-3 sentences:\n\n{text}"
            
            # First, show that processing has started
            st.info("🤖 AI is processing your request... This may take 10-30 seconds for the first time.")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "max_tokens": 200
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Summary generated successfully.")
            else:
                return f"❌ **Local AI Error**: HTTP {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "❌ **Local AI Error**: Ollama service not running. Please start Ollama with 'ollama serve'"
        except requests.exceptions.Timeout:
            return "❌ **Local AI Error**: Request timed out. The model might be processing a large document."
        except Exception as e:
            return f"❌ **Local AI Error**: {str(e)}"
    
    def answer_question(self, question: str, context: str) -> str:
        """Answer questions using free local AI model."""
        try:
            # Truncate context if too long
            if len(context) > 2000:
                context = context[:2000] + "... [truncated for faster processing]"
            
            prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
            
            # First, show that processing has started
            st.info("🤖 AI is processing your request... This may take 10-30 seconds for the first time.")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "max_tokens": 300
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Answer generated successfully.")
            else:
                return f"❌ **Local AI Error**: HTTP {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "❌ **Local AI Error**: Ollama service not running. Please start Ollama with 'ollama serve'"
        except Exception as e:
            return f"❌ **Local AI Error**: {str(e)}"
