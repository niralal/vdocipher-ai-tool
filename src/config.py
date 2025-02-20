"""
Configuration settings for the subtitle generation system.
Uses environment variables for deployment.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # Video ID or CSV file path for processing
    VIDEO_ID = os.getenv("VIDEO_ID", "d6dd0e1ce3cf4bc0a65d91865a1e13a8")
    VIDEO_IDS_CSV = os.getenv("VIDEO_IDS_CSV", "video_ids.csv")
    
    # Processing mode: 'single' or 'batch'
    MODE = os.getenv("MODE", "batch")
    
    # API Keys
    API_KEY = os.getenv("VDOCIPHER_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Processing options
    ENABLE_GRAMMAR_CORRECTION = os.getenv("ENABLE_GRAMMAR_CORRECTION", "True").lower() == "true"
    ENABLE_ARABIC_TRANSLATION = os.getenv("ENABLE_ARABIC_TRANSLATION", "True").lower() == "true"
    ENABLE_RUSSIAN_TRANSLATION = os.getenv("ENABLE_RUSSIAN_TRANSLATION", "True").lower() == "true"
    
    # Output file paths
    AUDIO_OUTPUT = "audio.mp3"
    VIDEO_OUTPUT = "video.mp4"
    
    # Language settings
    LANGUAGE = os.getenv("LANGUAGE", "he")
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
