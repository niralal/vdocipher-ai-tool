"""
Main entry point for the subtitle generation process.
Supports both single video and batch processing from CSV.
"""

import os
from src.subtitle_generator import SubtitleGenerator
from src.config import Config

def main():
    try:
        # Initialize configuration
        config = Config()
        
        # Create SubtitleGenerator instance
        generator = SubtitleGenerator()
        
        # Get the mode from config
        mode = config.MODE.lower()
        
        if mode == 'single':
            # Process single video
            video_id = config.VIDEO_ID
            print(f"\nProcessing single video: {video_id}")
            success = generator.process_video(video_id)
            print("Single processing:", "Success" if success else "Failed")
            
        elif mode == 'batch':
            # Process multiple videos from CSV
            csv_path = config.VIDEO_IDS_CSV
            print(f"\nProcessing videos from: {csv_path}")
            success = generator.process_videos_from_csv(csv_path)
            print("Batch processing:", "Success" if success else "Failed")
            
        else:
            print(f"Invalid mode: {mode}. Must be 'single' or 'batch'")
            return False
            
        return success
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return False

if __name__ == "__main__":
    main()
