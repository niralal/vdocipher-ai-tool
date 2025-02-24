"""
Configuration settings for the subtitle generation system.
Uses environment variables for deployment.
"""
import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # API Keys
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.VDOCIPHER_API_KEY = os.getenv('VDOCIPHER_API_KEY')
        
        # Settings
        self.MODE = os.getenv('MODE', 'batch')
        self.LANGUAGE = os.getenv('LANGUAGE', 'he')
        self.WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'whisper-1')
        self.GRAMMAR_MODEL = os.getenv('GRAMMAR_MODEL', 'gpt-3.5-turbo')
        self.TRANSLATION_MODEL = os.getenv('TRANSLATION_MODEL', 'gpt-3.5-turbo')
        
        # Features
        self.ENABLE_GRAMMAR_CORRECTION = os.getenv('ENABLE_GRAMMAR_CORRECTION', 'true').lower() == 'true'
        self.ENABLE_ARABIC_TRANSLATION = os.getenv('ENABLE_ARABIC_TRANSLATION', 'false').lower() == 'true'
        self.ENABLE_RUSSIAN_TRANSLATION = os.getenv('ENABLE_RUSSIAN_TRANSLATION', 'false').lower() == 'true'

    # Video ID or CSV file path for processing
    VIDEO_ID = os.getenv("VIDEO_ID", "d6dd0e1ce3cf4bc0a65d91865a1e13a8")
    VIDEO_IDS_CSV = os.getenv("VIDEO_IDS_CSV", "video_ids.csv")
    
    # Processing options - convert string to boolean
    ENABLE_GRAMMAR_CORRECTION = ENABLE_GRAMMAR_CORRECTION
    ENABLE_ARABIC_TRANSLATION = ENABLE_ARABIC_TRANSLATION
    ENABLE_RUSSIAN_TRANSLATION = ENABLE_RUSSIAN_TRANSLATION
    
    # Output file paths
    AUDIO_OUTPUT = "audio.mp3"
    VIDEO_OUTPUT = "video.mp4"
    
    # Language settings
    LANGUAGE = LANGUAGE
    WHISPER_MODEL = WHISPER_MODEL
