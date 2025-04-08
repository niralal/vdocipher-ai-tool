# Video Processing and Subtitle Generator

This project provides tools for processing videos and generating subtitles in multiple languages.

## Project Structure

```
.
├── main.py              # Main entry point of the application
├── video_ids.csv        # CSV file containing video IDs
├── src/
│   ├── config.py           # Configuration settings (gitignored)
│   ├── config.example.py   # Example configuration template
│   ├── media_processor.py  # Video/audio processing utilities
│   ├── text_processor.py   # Text processing functions
│   ├── vdocipher_client.py # VdoCipher API client
│   └── subtitle_generator.py # Subtitle generation logic
└── tmp/                 # Temporary files directory
    └── *.srt           # Generated subtitle files
```

## Features

- Video processing and manipulation
- Automatic subtitle generation
- Multi-language subtitle support
- Integration with VdoCipher API
- SRT file generation and handling

## Prerequisites

- Python 3.x
- Required Python packages (install via pip):
  ```bash
  pip install -r requirements.txt
  ```

## Setup

1. Copy the example configuration file:
   ```bash
   cp src/config.example.py src/config.py
   ```
2. Edit `src/config.py` with your settings
3. Ensure your video IDs are listed in `video_ids.csv`

## Usage

1. Configure your settings in `src/config.py`
2. Run the main script:
   ```bash
   python main.py
   ```

## Configuration

Edit `src/config.py` to set up:
- API credentials
- Language preferences
- Output directories
- Processing parameters

Example configuration:
```python
# VdoCipher API settings
VDOCIPHER_API_KEY = "your_api_key_here"

# Language settings
SOURCE_LANGUAGE = "en"
TARGET_LANGUAGES = ["ar", "es", "fr"]

# Output settings
OUTPUT_DIR = "tmp"
```

## Output

Generated subtitle files are saved in the `tmp/` directory in SRT format:
- Original subtitles: `[video_id].srt`
- Translated subtitles: `[video_id]_[language_code].srt`


## Run the project with Railway

1. Create a Railway project
2. Add environment variables to the project
3. Run the project

# Run in background with logging
railway run "python main.py > output.log 2>&1 &"

# Run in parallel with status updates
python run_parallel.py --max-workers 4 --status-interval 30
