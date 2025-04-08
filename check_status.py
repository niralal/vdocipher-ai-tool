#!/usr/bin/env python3
"""
Enhanced script to check the current processing status with detailed chunk information.
"""

import os
import csv
import sys
import time

def check_status():
    # Check if processing_results.csv exists
    results_path = os.path.join('tmp', 'processing_results.csv')
    if not os.path.exists(results_path):
        print("No results file found. Processing may not have started yet.")
        return
    
    # Get all processed video IDs and their status
    processed_videos = {}
    try:
        with open(results_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'video_id' in row:
                    processed_videos[row['video_id']] = {
                        'vdocipher': row.get('vdocipher_uploaded', '').lower() == 'true',
                        'baumann': row.get('sent_to_baumann', '').lower() == 'true',
                        'russian': row.get('ru_translated', '').lower() == 'true',
                        'arabic': row.get('ar_translated', '').lower() == 'true'
                    }
    except Exception as e:
        print(f"Error reading results file: {str(e)}")
        return
    
    # Get all chunk files
    chunks_dir = 'chunks'
    chunk_files = []
    
    if os.path.exists(chunks_dir):
        for filename in os.listdir(chunks_dir):
            if filename.startswith('chunk_') and filename.endswith('.txt'):
                chunk_files.append(os.path.join(chunks_dir, filename))
    
    chunk_files.sort()
    
    # Analyze each chunk
    total_videos = 0
    total_processed = 0
    total_successful = 0
    
    print("\n=== DETAILED PROCESSING STATUS ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"{'CHUNK':15} {'VIDEOS':8} {'PROCESSED':10} {'COMPLETED':10} {'PROGRESS':10}")
    print("-" * 60)
    
    for chunk_file in chunk_files:
        chunk_name = os.path.basename(chunk_file)
        
        # Read video IDs in this chunk
        chunk_videos = []
        with open(chunk_file, 'r') as f:
            for line in f:
                video_id = line.strip()
                if video_id and not video_id.startswith('#'):
                    chunk_videos.append(video_id)
        
        # Count processed and successful videos in this chunk
        chunk_processed = 0
        chunk_successful = 0
        
        for video_id in chunk_videos:
            if video_id in processed_videos:
                chunk_processed += 1
                if processed_videos[video_id]['vdocipher']:
                    chunk_successful += 1
        
        # Calculate progress percentage
        progress = (chunk_processed / len(chunk_videos) * 100) if chunk_videos else 0
        
        # Check if chunk is currently being processed
        log_file = chunk_file.replace('.txt', '.log')
        is_active = False
        if os.path.exists(log_file):
            # Check if log file was modified in the last 5 minutes
            if time.time() - os.path.getmtime(log_file) < 300:
                is_active = True
        
        # Print chunk status with progress bar
        status = "🔄 ACTIVE" if is_active else "✅ DONE" if chunk_processed == len(chunk_videos) else "⏸️ WAITING"
        progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
        
        print(f"{chunk_name:15} {len(chunk_videos):8} {chunk_processed:10} {chunk_successful:10} {progress_bar} {progress:.1f}% {status}")
        
        # Update totals
        total_videos += len(chunk_videos)
        total_processed += chunk_processed
        total_successful += chunk_successful
    
    # Print overall summary
    print("-" * 60)
    overall_progress = (total_processed / total_videos * 100) if total_videos else 0
    overall_bar = "█" * int(overall_progress / 10) + "░" * (10 - int(overall_progress / 10))
    
    print(f"{'TOTAL':15} {total_videos:8} {total_processed:10} {total_successful:10} {overall_bar} {overall_progress:.1f}%")
    print("=" * 60)
    
    # Check for active processes
    active_processes = os.popen("ps aux | grep '[p]ython main.py' | wc -l").read().strip()
    print(f"Active processing tasks: {active_processes}")
    
    # Estimate time remaining
    if total_processed > 0:
        # Try to estimate based on log file timestamps
        try:
            # Find the earliest and latest log modification times
            log_files = [f for f in os.listdir(chunks_dir) if f.endswith('.log')]
            if log_files:
                earliest_time = float('inf')
                latest_time = 0
                
                for log_file in log_files:
                    path = os.path.join(chunks_dir, log_file)
                    mod_time = os.path.getmtime(path)
                    earliest_time = min(earliest_time, mod_time)
                    latest_time = max(latest_time, mod_time)
                
                if latest_time > earliest_time:
                    elapsed_time = latest_time - earliest_time
                    videos_per_second = total_processed / elapsed_time
                    remaining_videos = total_videos - total_processed
                    
                    if videos_per_second > 0:
                        remaining_seconds = remaining_videos / videos_per_second
                        remaining_hours = remaining_seconds / 3600
                        
                        if remaining_hours > 1:
                            print(f"Estimated time remaining: {remaining_hours:.1f} hours")
                        else:
                            print(f"Estimated time remaining: {remaining_hours * 60:.0f} minutes")
        except Exception as e:
            print(f"Could not estimate time remaining: {str(e)}")

if __name__ == "__main__":
    check_status() 