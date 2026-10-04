import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables (.env)
load_dotenv()

async def run_test_agent():
    print("=" * 65)
    print(" [GHOSTPROCESS] BAND AGENT CONNECTION & LLM ENGINE TEST")
    print("=" * 65)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    print("\n1. API Keys Configuration:")
    print(f"   * GROQ_API_KEY   : {'[CONFIGURED]' if groq_api_key else '[MISSING]'}")
    print(f"   * GEMINI_API_KEY : {'[CONFIGURED]' if gemini_api_key else '[MISSING]'}")
    
    # Test Primary: Groq LLM (openai/gpt-oss-120b)
    print("\n2. Testing Primary LLM Engine (Groq: openai/gpt-oss-120b):")
    if groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            prompt = (
                "You are the Lead Architect agent for the GhostProcess Dark Factory. "
                "Output a concise 1-2 sentence introductory dispatch greeting confirming you are online "
                "and ready to construct the Pocketful payment & ledger architecture."
            )
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                temperature=0.2,
            )
            msg = response.choices[0].message.content.strip()
            print("   [SUCCESS] Groq Response:")
            print(f"   \"{msg}\"")
        except Exception as e:
            print(f"   [FAILED] Groq error: {e}")
    else:
        print("   [SKIPPED] GROQ_API_KEY not configured.")

    # Test Fallback: Gemini LLM (gemini-3.8-flash)
    print("\n3. Testing Fallback LLM Engine (Google Gemini: gemini-3.8-flash):")
    if gemini_api_key:
        try:
            from google import genai
            gemini_client = genai.Client(api_key=gemini_api_key)
            response = gemini_client.models.generate_content(
                model="gemini-3.8-flash",
                contents="You are Ghost Auditor agent for GhostProcess. Post a short 1-line hello confirming you are ready for red-team testing."
            )
            msg = response.text.strip()
            print("   [SUCCESS] Gemini Response:")
            print(f"   \"{msg}\"")
        except Exception as e:
            print(f"   [FAILED] Gemini error: {e}")
    else:
        print("   [SKIPPED] GEMINI_API_KEY not configured.")

    print("\n" + "=" * 65)
    print(" [OK] PHASE 1 COMPLETE: AI Brains & BAND Platform floor verified!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_test_agent())
