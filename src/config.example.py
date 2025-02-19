"""
Example configuration file for the video processing and subtitle generator.
Copy this file to config.py and update the values with your settings.
"""

# VdoCipher API credentials
VDOCIPHER_API_KEY = "your_api_key_here"

# Language settings
SOURCE_LANGUAGE = "en"  # Source language of the videos
TARGET_LANGUAGES = ["ar", "es", "fr"]  # Languages to translate subtitles into

# Processing settings
BATCH_SIZE = 10  # Number of videos to process in parallel
RETRY_ATTEMPTS = 3  # Number of retry attempts for failed operations

# Output settings
OUTPUT_DIR = "tmp"  # Directory for generated subtitle files
KEEP_TEMP_FILES = False  # Whether to keep temporary processing files 