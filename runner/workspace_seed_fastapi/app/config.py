import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventory.db")
API_KEY = os.getenv("API_KEY", "")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
