"""
Main entry point for the subtitle generation process.
Supports processing videos from a list file for parallel execution.
"""

print("=====================================")
print("DEFINITELY running updated version!!!")
print("=====================================")

import os
import sys
import csv
from src.subtitle_generator import SubtitleGenerator
from src.config import Config

def main():
    try:
        # Check if a list file was provided
        if len(sys.argv) < 2:
            print("Usage: python main.py <video_ids_file.txt>")
            print("Each line in the file should contain one video ID")
            return False
            
        # Get the list file path
        list_file_path = sys.argv[1]
        if not os.path.exists(list_file_path):
            print(f"Error: File not found: {list_file_path}")
            return False
            
        # Initialize configuration
        config = Config()
        
        # Create SubtitleGenerator instance
        generator = SubtitleGenerator()
        
        # Read video IDs from the list file
        video_ids = []
        with open(list_file_path, 'r') as f:
            for line in f:
                video_id = line.strip()
                if video_id and not video_id.startswith('#'):  # Skip empty lines and comments
                    video_ids.append(video_id)
        
        if not video_ids:
            print(f"No valid video IDs found in {list_file_path}")
            return False
            
        print(f"Processing {len(video_ids)} videos from {list_file_path}")
        
        # Process each video
        success_count = 0
        for i, video_id in enumerate(video_ids, 1):
            print(f"\nProcessing video {i}/{len(video_ids)}: {video_id}")
            
            # Ensure output is flushed immediately to the log file
            sys.stdout.flush()
            
            success, _ = generator.process_video(video_id)
            
            if success:
                success_count += 1
                print(f"✓ Successfully processed {video_id}")
            else:
                print(f"✗ Failed to process {video_id}")
            
            # Ensure output is flushed immediately to the log file
            sys.stdout.flush()
                
        print(f"\nCompleted processing {success_count}/{len(video_ids)} videos successfully")
        return success_count == len(video_ids)
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return False

if __name__ == "__main__":
    main()
