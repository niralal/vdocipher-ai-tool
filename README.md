# Video Processing and Subtitle Generator

This project provides tools for processing videos and generating subtitles in multiple languages, with support for parallel processing and robust error handling.

## Project Structure

```
.
├── main.py                # Main entry point for single chunk processing
├── run_parallel.py        # Script for parallel processing of multiple chunks
├── check_status.py        # Script to check processing status
├── view_chunk_log.py      # Script to view and analyze chunk logs
├── fix_results.py         # Script to fix the results file format
├── reprocess_failed.py    # Script to identify and reprocess failed videos
├── split_video_ids.py     # Script to split a large video IDs file into chunks
├── video_ids.csv          # CSV file containing video IDs
├── chunks/                # Directory containing chunk files and logs
│   ├── chunk_001.txt      # Chunk file with video IDs
│   ├── chunk_001.log      # Log file for the chunk
│   └── chunk_001.completed # Marker file indicating the chunk is completed
├── src/
│   ├── config.py           # Configuration settings
│   ├── config.example.py   # Example configuration template
│   ├── media_processor.py  # Video/audio processing utilities
│   ├── text_processor.py   # Text processing functions
│   ├── vdocipher_client.py # VdoCipher API client
│   └── subtitle_generator.py # Subtitle generation logic
└── tmp/                   # Temporary files directory
    ├── processing_results.csv # CSV file with processing results
    └── *.srt              # Generated subtitle files
```

## Features

- Video processing and manipulation
- Automatic subtitle generation using OpenAI's Whisper
- Multi-language subtitle support (Hebrew, Russian, Arabic)
- Grammar correction for Hebrew subtitles
- Integration with VdoCipher API
- Parallel processing of multiple videos
- Robust error handling and recovery
- Detailed logging and status reporting

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
4. Create necessary directories:
   ```bash
   mkdir -p chunks tmp
   ```

## Basic Usage

### Single Video Processing

To process a single video:

```bash
python main.py video_id.txt
```

Where `video_id.txt` contains a single video ID.

### Batch Processing

1. Create a CSV file with video IDs (one per line):
   ```
   video_id_1
   video_id_2
   ...
   ```

2. Split the CSV into smaller chunks for parallel processing:
   ```bash
   python split_video_ids.py --input video_ids.csv --output-dir chunks --chunk-size 20
   ```

3. Process all chunks in parallel:
   ```bash
   python run_parallel.py --max-workers 4
   ```

## Monitoring and Management

### Check Processing Status

To check the current status of all chunks:

```bash
python check_status.py
```

This will show:
- Which chunks are completed, active, or waiting
- How many videos in each chunk have been processed
- Overall progress percentage
- Estimated time remaining

### View Chunk Logs

To list all available chunks:

```bash
python view_chunk_log.py --list
```

To view the log for a specific chunk:

```bash
python view_chunk_log.py chunk_001.txt
```

To show only error messages:

```bash
python view_chunk_log.py chunk_001.txt --errors-only
```

To search for specific terms in the log:

```bash
python view_chunk_log.py chunk_001.txt --search "Error"
```

### Fix Results File

If the results file is corrupted or missing headers:

```bash
python fix_results.py
```
python fix_results.py --mark-all-completed

This will:
- Create a backup of the original file
- Add proper headers
- Fix the format of the data

### Reprocess Failed Videos

To identify videos that failed processing:

```bash
python reprocess_failed.py --list-only
```

To create a chunk file with failed videos and reprocess them:

```bash
python reprocess_failed.py
```

You can specify a custom output file:

```bash
python reprocess_failed.py --output chunks/custom_reprocess.txt
```

## Advanced Usage

### Force Processing of All Chunks

To reprocess all chunks, even if they're marked as completed:

```bash
python run_parallel.py --force
```

### Update Completion Markers

To update completion markers for all chunks based on the results file:

```bash
python run_parallel.py --update-markers
```

### Check a Specific Chunk

To check if a specific chunk is completed:

```bash
python run_parallel.py --check-chunk chunk_001.txt
```

### Lenient Completion Check

To check a chunk with lenient completion criteria (any entry in results file counts):

```bash
python run_parallel.py --lenient-check chunk_001.txt
```

## Configuration

Edit `src/config.py` to set up:
- API credentials
- Language preferences
- Output directories
- Processing parameters

Example configuration:
```python
# API Keys
VDOCIPHER_API_KEY = "your_api_key_here"
OPENAI_API_KEY = "your_openai_key_here"
BAUMANN_API_TOKEN = "your_baumann_token_here"

# Language settings
LANGUAGE = "he"
ENABLE_GRAMMAR_CORRECTION = True
ENABLE_ARABIC_TRANSLATION = True
ENABLE_RUSSIAN_TRANSLATION = True

# Model settings
WHISPER_MODEL = "whisper-1"
GRAMMAR_MODEL = "gpt-4o-mini"
TRANSLATION_MODEL = "gpt-4o-mini"
```

## Troubleshooting

### "I/O operation on closed file" Error

If you see this error, run:

```bash
python fix_results.py
```

Then restart the processing:

```bash
python run_parallel.py
```

### Stuck Process

If the process gets stuck after marking a chunk as completed:

1. Stop the current process (Ctrl+C)
2. Remove the completion marker:
   ```bash
   rm chunks/chunk_XXX.completed
   ```
3. Restart the process:
   ```bash
   python run_parallel.py
   ```

### Missing or Corrupted Results

If the results file is missing or corrupted:

```bash
python fix_results.py
```

### Checking for Specific Errors

To search for specific errors across all chunk logs:

```bash
for f in chunks/*.log; do echo "=== $f ==="; grep -i "error" $f | head -5; echo; done
```

## Running in Production

### Run with Railway

1. Create a Railway project
2. Add environment variables to the project
3. Run the project

```bash
# Run in background with logging
railway run "python main.py > output.log 2>&1 &"

# Run in parallel with status updates
railway run "python run_parallel.py --max-workers 4 --status-interval 30"
```

### Run with Docker

1. Build the Docker image:
   ```bash
   docker build -t subtitle-generator .
   ```

2. Run the container:
   ```bash
   docker run -v $(pwd)/tmp:/app/tmp -v $(pwd)/chunks:/app/chunks subtitle-generator python run_parallel.py --max-workers 4
   ```

## Output

Generated subtitle files are saved in the `tmp/` directory in SRT format:
- Original subtitles: `[video_id]_original.srt`
- Hebrew subtitles (with grammar correction): `[video_id]_he.srt`
- Russian subtitles: `[video_id]_ru.srt`
- Arabic subtitles: `[video_id]_ar.srt`

Processing results are saved in `tmp/processing_results.csv` with the following columns:
- `video_id`: The ID of the processed video
- `sent_to_baumann`: Whether the subtitles were sent to Baumann API
- `ru_translated`: Whether Russian translation was successful
- `ar_translated`: Whether Arabic translation was successful
- `vdocipher_uploaded`: Whether subtitles were uploaded to VdoCipher

## Handling Baumann DB IDs

If you have a list of IDs from the Baumann database that have already been updated, you can:

1. Create a file with these IDs (one per line)
2. Use the following command to exclude them from processing:
   ```bash
   grep -v -f baumann_ids.txt video_ids.csv > remaining_ids.csv
   ```
3. Process only the remaining IDs:
   ```bash
   python split_video_ids.py --input remaining_ids.csv --output-dir chunks --chunk-size 20
   python run_parallel.py --max-workers 4
   ```

Alternatively, you can mark these videos as completed in the results file:
```bash
python mark_as_completed.py --input baumann_ids.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
