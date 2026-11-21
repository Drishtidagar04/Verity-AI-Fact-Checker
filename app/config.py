import os
from dotenv import load_dotenv
load_dotenv()
APP_VERSION = "1.0.0"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
TAVILY_URL = "https://api.tavily.com/search"
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
DB_PATH = os.getenv("VERITY_DB_PATH", "app/data/verity.db")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
