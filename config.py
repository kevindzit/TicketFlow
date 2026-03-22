import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/ticketflow')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
