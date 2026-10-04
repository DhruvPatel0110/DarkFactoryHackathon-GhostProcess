import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# LLM Models
GROQ_PRIMARY_MODEL = "openai/gpt-oss-120b"
GROQ_BACKUP_MODEL = "qwen/qwen3.8-27b"
GEMINI_FALLBACK_MODEL = "gemini-3.8-flash"

# Rate Limiting Configurations (Guarantees zero 429 crashes)
# Groq free tier limit is 30 RPM; we set conservative 20 RPM with 2.5s minimum spacing
GROQ_MAX_RPM = 20
GROQ_MIN_INTERVAL = 2.5

# Gemini rate limit config (free tier is 15 RPM; set 12 RPM with 4.5s spacing)
GEMINI_MAX_RPM = 12
GEMINI_MIN_INTERVAL = 4.5

# BAND Desktop Configurations
BAND_ROOM_ID = "391f7b44-8d58-4bc0-9f98-aefec78160a4"
BAND_ROOM_NAME = "DarkFactory-GhostProcess"

# Factory Operational Bounds
MAX_REJECTION_CYCLES = 3
DEFAULT_TEMPERATURE = 0.2
