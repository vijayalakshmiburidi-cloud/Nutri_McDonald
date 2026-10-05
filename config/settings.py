# config/settings.py
import os
import urllib.parse
import logging
import warnings
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment configuration variables
load_dotenv()

DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT     = os.environ.get("DB_PORT")
DB_NAME     = os.environ.get("DB_NAME")
GROQ_KEY    = os.environ.get("API_KEY")

# URL encode to handle special characters in passwords securely
enc_user = urllib.parse.quote_plus(DB_USER if DB_USER else "")
enc_pass = urllib.parse.quote_plus(DB_PASSWORD if DB_PASSWORD else "")

# 1. Main Relational Database Engine Connection
engine = create_engine(
    f"mysql+pymysql://{enc_user}:{enc_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# 2. ChromaDB Persistent Client and Document Collections
chroma_client = chromadb.PersistentClient(path="./chroma_mcdonalds")
collection = chroma_client.get_or_create_collection("mcdonalds_menu")

# 3. Model Clients
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key=GROQ_KEY)

# 4. Global Running Token Trackers (Isolated internally to thread limits)
session_tokens = {"input": 0, "output": 0}

def track_tokens(response, tool_name):
    """Tracks token consumption dynamically across various model operations"""
    usage = response.usage
    session_tokens["input"]  += usage.prompt_tokens
    session_tokens["output"] += usage.completion_tokens
    print(f"[Tokens-{tool_name}] in:{usage.prompt_tokens} out:{usage.completion_tokens}")
    return response

# 5. Core Operational Logger Framework Initialization
def setup_logging():
    os.makedirs("logs", exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/agent_{today}.log"

    logger = logging.getLogger("McDAgent")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

        logger.addHandler(console)
        logger.addHandler(file_handler)
    return logger

logger = setup_logging()
print("✅ Configuration and database engines initialized successfully!")
print("-" * 40)
