"""
Configuration settings for the subtitle generation system.
Uses environment variables for deployment.
"""
import os

class Config:
    # Video ID or CSV file path for processing
    VIDEO_ID = os.getenv("VIDEO_ID", "d6dd0e1ce3cf4bc0a65d91865a1e13a8")
    VIDEO_IDS_CSV = os.getenv("VIDEO_IDS_CSV", "video_ids.csv")
    
    # API Keys
    VDOCIPHER_API_KEY = os.getenv("VDOCIPHER_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Settings
    MODE = os.getenv("MODE", "batch")
    LANGUAGE = os.getenv("LANGUAGE", "he")
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
    GRAMMAR_MODEL = os.getenv("GRAMMAR_MODEL", "gpt-4o")
    TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "gpt-4o")
    
    # Features
    ENABLE_GRAMMAR_CORRECTION = os.getenv("ENABLE_GRAMMAR_CORRECTION", "true").lower() == "true"
    ENABLE_ARABIC_TRANSLATION = os.getenv("ENABLE_ARABIC_TRANSLATION", "true").lower() == "true"
    ENABLE_RUSSIAN_TRANSLATION = os.getenv("ENABLE_RUSSIAN_TRANSLATION", "true").lower() == "true"
    
    # Output file paths
    AUDIO_OUTPUT = "audio.mp3"
    VIDEO_OUTPUT = "video.mp4"
