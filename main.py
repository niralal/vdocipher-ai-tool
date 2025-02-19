"""
Main entry point for the subtitle generation process.
Supports both single video and batch processing from CSV.
"""

from src.subtitle_generator import SubtitleGenerator
from src.config import Config

def main():
    """
    Main function to run the subtitle generation process.
    Uses Config.MODE to determine processing type.
    """
    generator = SubtitleGenerator()
    
    if Config.MODE == "single":
        # Process single video
        success = generator.process_video(Config.VIDEO_ID)
        print("Single video processing:", "Success" if success else "Failed")
    else:
        # Process videos from CSV file
        success = generator.process_videos_from_csv(Config.VIDEO_IDS_CSV)
        print("Batch processing:", "Success" if success else "Failed")

if __name__ == "__main__":
    main()
