"""
Configuration settings for the subtitle generation system.
Uses environment variables for deployment.
"""
import os

class Config:
    @staticmethod
    def load_env():
        """Load environment variables directly from .env file"""
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            print(f"Looking for .env at: {env_path}")
            
            with open(env_path, 'r') as f:
                print("Reading .env file...")
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        os.environ[key] = value
                        if key == 'OPENAI_API_KEY':
                            print(f"Set {key}={value[:10]}...{value[-10:]}")
                        else:
                            print(f"Set {key}")
        except Exception as e:
            print(f"Error loading .env file: {e}")

    # Force reload environment variables
    print("\nConfig initialization:")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Current file location: {__file__}")
    load_env()
    
    # Video ID or CSV file path for processing
    VIDEO_ID = os.getenv("VIDEO_ID", "d6dd0e1ce3cf4bc0a65d91865a1e13a8")
    VIDEO_IDS_CSV = os.getenv("VIDEO_IDS_CSV", "video_ids.csv")
    
    # API Keys
    VDOCIPHER_API_KEY = os.getenv("VDOCIPHER_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    BAUMANN_API_TOKEN = os.getenv("BAUMANN_API_TOKEN")
    
    # Debug logging
    print("\nEnvironment variables loaded:")
    print(f"OPENAI_API_KEY = {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-10:] if OPENAI_API_KEY else 'None'}")
    print(f"VDOCIPHER_API_KEY = {VDOCIPHER_API_KEY[:5]}... (truncated)")
    print(f"MODE = {os.getenv('MODE')}")
    
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
