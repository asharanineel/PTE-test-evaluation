# #--- START OF FILE settings.py ---

# from pydantic_settings import BaseSettings
# from dotenv import load_dotenv
# import os

# # Load environment variables from .env file
# load_dotenv()

# class Settings(BaseSettings):
#     # MongoDB Configuration
#     MONGO_URI: str
#     MONGO_DB: str = "pte_speaking_writing_database"
#     COLLECTION_NAME: str = "speaking_writing"

#     # MySQL Configuration
#     DB_HOST: str 
#     DB_USER: str 
#     DB_PASSWORD: str
#     DB_NAME: str = "pte_database"
#     DB_PORT: str
#     mysql_auth_plugin: str = "mysql_native_password" 

#     # Mail Configuration
#     MAIL_USERNAME: str
#     MAIL_PASSWORD: str
#     MAIL_SERVER: str
#     MAIL_PORT: int = 587
#     MAIL_EVALUATOR_USERNAME: str
#     MAIL_USE_TLS: bool = True
#     MAIL_USE_SSL: bool = False

#     # AI Models API Configuration
#     DASHSCOPE_API_KEY: str
#     DASHSCOPE_MODEL_NAME: str = "qwen-plus"
#     OPENAI_API_KEY: str
#     LLM_BASE_URL: str
#     OPENAI_MODEL_NAME: str = "gpt-4o-mini-2024-07-18"

#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#         # Optionally allow extra fields if you want to ignore other unexpected variables
#         extra = "allow"

# # Instantiate settings
# settings = Settings()

# ########################## okkk ##############



# src/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional # Make sure Optional is imported
import os
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # This tells pydantic-settings where to look for the .env file.
    # It assumes .env is in the project root, one level up from src/config.py
    # --- MODIFIED: Added env_nested_delimiter and changed env_file path ---
    model_config = SettingsConfigDict(
        env_file='../.env', # Assuming .env is one level up from src/
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False, # Environment variables are often uppercase
        env_nested_delimiter='__', # For nested settings if you had them, good practice
        # NEW: Explicitly allow empty strings for Optional fields if they come from env
        # This is a common pattern for Pydantic v2+ with Optional fields
        # If an environment variable is set to an empty string, Pydantic will treat it as None
        # for Optional[str] fields.
        # This is often the default behavior, but explicitly stating it can help.
        # However, the core issue here is "Field required", not "invalid type".
    )

    # --- MAIL CONFIG ---
    MAIL_USERNAME: str = "noreply@example.com"
    MAIL_PASSWORD: str = "default_mail_pass"
    MAIL_SERVER: str = "smtp.host.com"
    MAIL_PORT: int = 587
    MAIL_EVALUATOR_USERNAME: str = "evaluator@example.com"
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False

    # --- MONGO CONFIG ---
    MONGO_URI: str = "mongodb://localhost:27017/"

    # --- MYSQL CONFIG ---
    DB_HOST: str = "localhost"
    DB_USER: str = "root"
    DB_PASSWORD: str = "default_db_pass"
    DB_PORT: int = 3306
    MYSQL_AUTH_PLUGIN: str = "mysql_native_password"

    # --- LLM CONFIG ---
    # OpenAI
    OPENAI_API_KEY: str = "sk-default_openai_key"
    #OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"

    # Google Gemini
    GEMINI_API_KEY: str = "AIzaSy_default_gemini_key"

    # Dashscope (Aliyun)
    DASHSCOPE_API_KEY: str = "sk-default_dashscope_key"
    DASHSCOPE_MODEL_NAME: str = "qwen-turbo"
    # --- MODIFIED: Ensure Optional is imported and explicitly set default to None ---
    LLM_BASE_URL: Optional[str] = None 

    # Google Cloud
    GOOGLE_CLOUD_API_KEY: Optional[str] = None 

    # Whisper STT
    WHISPER_MODEL_SIZE: str = "base"


# Instantiate settings to be imported by other modules
settings = Settings()

logger.info(f"Settings loaded: "
            f"MONGO_URI={settings.MONGO_URI}, "
            f"DB_HOST={settings.DB_HOST}, "
            f"OPENAI_MODEL_NAME={settings.OPENAI_MODEL_NAME}, "
            f"WHISPER_MODEL_SIZE={settings.WHISPER_MODEL_SIZE}")

