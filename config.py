import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HF_API_KEY = os.getenv('HF_API_KEY')  # Hugging Face API Key
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
