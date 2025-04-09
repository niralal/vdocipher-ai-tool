#!/usr/bin/env python3
"""
Script to identify and reprocess failed video jobs.
"""

import os
import csv
import argparse
import subprocess

def identify_failed_videos():
    """Identify videos that failed processing"""
    results_path = os.path.join('tmp', 'processing_results.csv')
    if not os.path.exists(results_path):
        print("Results file not found.")
        return []
    
    failed_videos = []
    try:
        with open(results_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Check if any of the required operations failed
                if (row.get('sent_to_baumann', '').lower() != 'true' or
                    row.get('ru_translated', '').lower() != 'true' or
                    row.get('ar_translated', '').lower() != 'true' or
                    row.get('vdocipher_uploaded', '').lower() != 'true'):
                    failed_videos.append({
                        'video_id': row.get('video_id'),
                        'baumann': row.get('sent_to_baumann', '').lower() == 'true',
                        'russian': row.get('ru_translated', '').lower() == 'true',
                        'arabic': row.get('ar_translated', '').lower() == 'true',
                        'vdocipher': row.get('vdocipher_uploaded', '').lower() == 'true'
                    })
    except Exception as e:
        print(f"Error reading results file: {str(e)}")
    
    return failed_videos

def create_reprocess_chunk(failed_videos, output_file='chunks/reprocess.txt'):
    """Create a chunk file with failed video IDs"""
    # Create chunks directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write the failed video IDs to the chunk file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("# Failed videos for reprocessing\n")
        for video in failed_videos:
            file.write(f"{video['video_id']}\n")
    
    print(f"Created reprocess chunk with {len(failed_videos)} videos: {output_file}")
    return output_file

def reprocess_videos(chunk_file):
    """Reprocess videos in the chunk file"""
    print(f"Reprocessing videos from {chunk_file}")
    
    # Run the main.py script with the chunk file
    process = subprocess.Popen(
        ["python", "main.py", chunk_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line-buffered
    )
    
    # Read output in real-time
    for line in process.stdout:
        print(line.strip())
    
    # Wait for process to complete
    process.wait()
    
    # Read any errors
    for line in process.stderr:
        print(f"ERROR: {line.strip()}")
    
    if process.returncode == 0:
        print(f"Successfully reprocessed videos from {chunk_file}")
        return True
    else:
        print(f"Error reprocessing videos from {chunk_file}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Identify and reprocess failed video jobs')
    parser.add_argument('--list-only', action='store_true',
                        help='Only list failed videos without reprocessing')
    parser.add_argument('--output', type=str, default='chunks/reprocess.txt',
                        help='Output file for the reprocess chunk')
    
    args = parser.parse_args()
    
    # Identify failed videos
    failed_videos = identify_failed_videos()
    
    if not failed_videos:
        print("No failed videos found.")
        return
    
    print(f"Found {len(failed_videos)} failed videos:")
    for i, video in enumerate(failed_videos, 1):
        status = []
        if not video['baumann']:
            status.append("Baumann")
        if not video['russian']:
            status.append("Russian")
        if not video['arabic']:
            status.append("Arabic")
        if not video['vdocipher']:
            status.append("VdoCipher")
        
        print(f"{i}. {video['video_id']} - Failed: {', '.join(status)}")
    
    if args.list_only:
        print("Use --list-only=false to reprocess these videos")
        return
    
    # Create a chunk file with failed video IDs
    chunk_file = create_reprocess_chunk(failed_videos, args.output)
    
    # Ask for confirmation before reprocessing
    response = input(f"Reprocess {len(failed_videos)} failed videos? (y/n): ")
    if response.lower() == 'y':
        reprocess_videos(chunk_file)
    else:
        print("Reprocessing cancelled.")
        print(f"You can manually reprocess later with: python main.py {chunk_file}")

if __name__ == "__main__":
    main() 