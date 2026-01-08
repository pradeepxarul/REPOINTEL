"""
Unified LLM Client for AI-Powered Features

Supports multiple providers:
- GROQ (Primary - Fast & Cost-effective)
- OpenAI (GPT-4)
- Google (Gemini)
"""
import os
from typing import Optional, Any
from core.config import settings
from utils.logger import logger


class LLMClient:
    """
    Unified client for LLM providers (Groq, OpenAI, Google).
    
    Auto-selects provider based on available API keys:
    1. GROQ (if GROQ_API_KEY set)
    2. OpenAI (if OPENAI_API_KEY set)
    3. Google (if GOOGLE_API_KEY set)
    4. None (template mode)
    """
    
    def __init__(self):
        """Initialize LLM client with auto-detection of available provider."""
        self.provider = self._detect_provider()
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.client = self._init_client()
    
    def _detect_provider(self) -> str:
        """Auto-detect available LLM provider based on API keys."""
        # Priority: GROQ > OpenAI > Google
        if settings.GROQ_API_KEY:
            return "groq"
        elif settings.OPENAI_API_KEY:
            return "openai"
        elif settings.GOOGLE_API_KEY:
            return "google"
        else:
            return "none"
    
    def _init_client(self) -> Any:
        """Initialize the LLM client based on provider."""
        try:
            if self.provider == "groq":
                from groq import Groq
                logger.info(f"🚀 LLM Client: GROQ {self.model}")
                return Groq(api_key=settings.GROQ_API_KEY)
            
            elif self.provider == "openai":
                from openai import OpenAI
                logger.info(f"🤖 LLM Client: OpenAI {self.model}")
                return OpenAI(api_key=settings.OPENAI_API_KEY)
            
            elif self.provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                logger.info(f"🤖 LLM Client: Google {self.model}")
                return genai
            
            else:
                logger.warning("⚠️ No LLM API key configured. Using template mode.")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM client ({self.provider}): {e}")
            return None
    
    def generate_response(
        self, 
        prompt: str, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> Optional[str]:
        """
        Generate text response from LLM.
        
        Args:
            prompt: The input prompt
            temperature: Override default temperature (0.0-1.0)
            max_tokens: Override default max tokens
            json_mode: Request JSON formatted response
        
        Returns:
            Generated text or None if failed
        """
        if not self.client:
            logger.warning("📝 LLM client not available. Template mode active.")
            return None
        
        # Use instance defaults if not overridden
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            if self.provider in ["groq", "openai"]:
                kwargs = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temp,
                    "max_tokens": tokens,
                }
                
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            
            elif self.provider == "google":
                model = self.client.GenerativeModel(self.model)
                response = model.generate_content(prompt)
                return response.text
            
        except Exception as e:
            logger.error(f"❌ LLM generation failed: {e}")
            return None
    
    def generate_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Generate response with system and user prompts (GROQ/OpenAI only).
        
        Args:
            system_prompt: System instructions
            user_prompt: User input
            temperature: Override default temperature
            max_tokens: Override default max tokens
        
        Returns:
            Generated text or None if failed
        """
        if not self.client or self.provider not in ["groq", "openai"]:
            logger.warning("System prompts only supported for GROQ/OpenAI")
            return self.generate_response(user_prompt, temperature, max_tokens)
        
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temp,
                max_tokens=tokens
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ LLM generation failed: {e}")
            return None
    
    @property
    def is_available(self) -> bool:
        """Check if LLM client is available."""
        return self.client is not None


# Singleton instance
llm_client = LLMClient()
