import asyncio
import os
import time
from typing import Optional, List, Dict, Any

from agents.config import (
    GROQ_API_KEY,
    GEMINI_API_KEY,
    GROQ_PRIMARY_MODEL,
    GROQ_BACKUP_MODEL,
    GEMINI_FALLBACK_MODEL,
    GROQ_MAX_RPM,
    GROQ_MIN_INTERVAL,
    GEMINI_MAX_RPM,
    GEMINI_MIN_INTERVAL,
    DEFAULT_TEMPERATURE,
)
from agents.rate_limiter import AsyncRateLimiter

class ResilientLLMClient:
    """
    Unified, rate-limited LLM client for all GhostProcess Dark Factory agents.
    - Proactive rate limiting prevents 429 errors.
    - Automatic retry with exponential backoff on transient errors.
    - Seamless fallback from Groq to Gemini if Groq is overloaded.
    """
    def __init__(self):
        self.groq_limiter = AsyncRateLimiter(max_rpm=GROQ_MAX_RPM, min_interval_seconds=GROQ_MIN_INTERVAL)
        self.gemini_limiter = AsyncRateLimiter(max_rpm=GEMINI_MAX_RPM, min_interval_seconds=GEMINI_MIN_INTERVAL)
        
        self.groq_client = None
        if GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=GROQ_API_KEY)
            except Exception as e:
                print(f"[WARN] Failed to initialize Groq client: {e}")

        self.gemini_client = None
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"[WARN] Failed to initialize Gemini client: {e}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_retries: int = 3,
        force_fallback: bool = False,
    ) -> str:
        """
        Generates content using Groq as primary, falling back to Gemini if needed.
        Guarantees paced execution with rate limiting and exponential backoff.
        """
        # 1. Try Groq Primary (if available and not forced fallback)
        if self.groq_client and not force_fallback:
            for attempt in range(1, max_retries + 1):
                try:
                    await self.groq_limiter.acquire()
                    
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})

                    # Execute in async thread pool to prevent event loop blocking
                    response = await asyncio.to_thread(
                        self.groq_client.chat.completions.create,
                        model=GROQ_PRIMARY_MODEL,
                        messages=messages,
                        temperature=temperature,
                    )
                    content = response.choices[0].message.content
                    if content:
                        return content.strip()
                except Exception as e:
                    err_str = str(e).lower()
                    print(f"   [GROQ ATTEMPT {attempt}/{max_retries}] Exception: {e}")
                    if "rate" in err_str or "429" in err_str:
                        backoff = (2 ** attempt) + 1.0
                        print(f"   [RATE LIMIT] Backing off Groq for {backoff:.1f}s...")
                        await asyncio.sleep(backoff)
                    else:
                        # Non-rate-limit error (e.g. timeout/500)
                        await asyncio.sleep(2.0)
            
            print("   [FALLBACK] Groq attempts exhausted. Switching to Google Gemini fallback...")

        # 2. Fallback to Gemini
        if self.gemini_client:
            for attempt in range(1, max_retries + 1):
                try:
                    await self.gemini_limiter.acquire()
                    
                    full_prompt = prompt
                    if system_prompt:
                        full_prompt = f"System Instructions:\n{system_prompt}\n\nTask:\n{prompt}"

                    response = await asyncio.to_thread(
                        self.gemini_client.models.generate_content,
                        model=GEMINI_FALLBACK_MODEL,
                        contents=full_prompt,
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    print(f"   [GEMINI ATTEMPT {attempt}/{max_retries}] Exception: {e}")
                    await asyncio.sleep((2 ** attempt) + 1.0)

        raise RuntimeError("All LLM providers (Groq and Gemini) failed to generate a response.")

# Global singleton client instance
llm_client = ResilientLLMClient()
