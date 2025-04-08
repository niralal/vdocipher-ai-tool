"""
Utility script to run multiple instances of main.py in parallel
using multiple processes.
"""

import os
import argparse
import subprocess
import concurrent.futures
import csv
import time
import re

def process_chunk(chunk_file):
    """Process a single chunk file using main.py"""
    try:
        print(f"Starting processing of {chunk_file}")
        
        # Use subprocess.Popen instead of subprocess.run to read output in real-time
        process = subprocess.Popen(
            ["python", "main.py", chunk_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line-buffered
        )
        
        # Read output in real-time
        output = []
        for line in process.stdout:
            print(f"[{os.path.basename(chunk_file)}] {line.strip()}")
            output.append(line)
            
        # Wait for process to complete
        process.wait()
        
        # Read any errors
        for line in process.stderr:
            print(f"[{os.path.basename(chunk_file)}] ERROR: {line.strip()}")
            output.append(f"ERROR: {line}")
        
        if process.returncode == 0:
            print(f"Completed {chunk_file}")
            return True, chunk_file, "".join(output)
        else:
            print(f"Error processing {chunk_file}: Return code {process.returncode}")
            return False, chunk_file, "".join(output)
            
    except Exception as e:
        print(f"Error processing {chunk_file}: {e}")
        return False, chunk_file, str(e)

def count_processed_videos():
    """Count processed videos from results file"""
    results_path = os.path.join('tmp', 'processing_results.csv')
    if not os.path.exists(results_path):
        return 0, 0
    
    total = 0
    successful = 0
    
    try:
        with open(results_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                if row.get('vdocipher_uploaded', '').lower() == 'true':
                    successful += 1
    except Exception as e:
        print(f"Error reading results: {e}")
    
    return total, successful

def print_status_summary():
    """Print a simple status summary"""
    total_processed, successful = count_processed_videos()
    
    print("\n--- Status Summary ---")
    print(f"Total videos processed: {total_processed}")
    print(f"Successfully completed: {successful}")
    if total_processed > 0:
        print(f"Success rate: {successful/total_processed*100:.1f}%")
    print("----------------------\n")

def print_detailed_status():
    """Print detailed status of all chunks"""
    # Get all processed video IDs and their status
    results_path = os.path.join('tmp', 'processing_results.csv')
    processed_videos = {}
    
    if os.path.exists(results_path):
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

def update_results_from_log(log_file):
    """Extract video IDs and status from log file and update results"""
    results_path = os.path.join('tmp', 'processing_results.csv')
    
    # Create tmp directory if it doesn't exist
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    
    # Read the log file
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
    except Exception as e:
        print(f"Error reading log file {log_file}: {e}")
        return
    
    # Search for video IDs and results in the log
    video_pattern = r"Processing video \d+/\d+: ([a-zA-Z0-9_-]+)"
    success_pattern = r"Successfully processed ([a-zA-Z0-9_-]+)"
    
    video_ids = re.findall(video_pattern, log_content)
    successful_ids = re.findall(success_pattern, log_content)
    
    # Read existing results
    results = []
    try:
        if os.path.exists(results_path):
            with open(results_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Keep all rows that don't relate to videos found in the log
                    if row.get('video_id') not in video_ids:
                        results.append(row)
    except Exception as e:
        print(f"Warning: Error reading results file: {str(e)}")
    
    # Add the new results
    for video_id in video_ids:
        success = video_id in successful_ids
        result = {
            'video_id': video_id,
            'sent_to_baumann': str(success).lower(),
            'ru_translated': str(success).lower(),
            'ar_translated': str(success).lower(),
            'vdocipher_uploaded': str(success).lower()
        }
        results.append(result)
    
    # Write the file
    try:
        with open(results_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['video_id', 'sent_to_baumann', 'ru_translated', 
                         'ar_translated', 'vdocipher_uploaded']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"✓ Updated results file from log {os.path.basename(log_file)}")
    except Exception as e:
        print(f"✗ Error updating results file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Run multiple instances of main.py in parallel')
    parser.add_argument('--chunks-dir', type=str, default='chunks', 
                        help='Directory containing chunk files')
    parser.add_argument('--max-workers', type=int, default=4, 
                        help='Maximum number of parallel processes')
    parser.add_argument('--status-interval', type=int, default=60,
                        help='Interval in seconds between status updates')
    parser.add_argument('--detailed', action='store_true', default=True,
                        help='Show detailed progress information')
    
    args = parser.parse_args()
    
    # Get all chunk files
    chunk_files = []
    for filename in os.listdir(args.chunks_dir):
        if filename.startswith('chunk_') and filename.endswith('.txt'):
            chunk_files.append(os.path.join(args.chunks_dir, filename))
    
    chunk_files.sort()  # Process in order
    
    if not chunk_files:
        print(f"No chunk files found in {args.chunks_dir}")
        return
    
    print(f"Found {len(chunk_files)} chunk files to process")
    print(f"Running with {args.max_workers} parallel workers")
    print(f"Status updates every {args.status_interval} seconds")
    
    # Count total videos to process
    total_videos = 0
    for chunk_file in chunk_files:
        with open(chunk_file, 'r') as f:
            total_videos += sum(1 for line in f if line.strip() and not line.strip().startswith('#'))
    
    print(f"Total videos to process: {total_videos}")
    
    # Process chunks in parallel
    if args.detailed:
        print_detailed_status()  # Show detailed status at the start
    else:
        print_status_summary()
    last_status_time = time.time()
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {executor.submit(process_chunk, chunk_file): chunk_file for chunk_file in chunk_files}
        
        success_count = 0
        for future in concurrent.futures.as_completed(futures):
            success, chunk_file, output = future.result()
            if success:
                success_count += 1
            
            # Write output to log file
            log_file = chunk_file.replace('.txt', '.log')
            with open(log_file, 'w') as f:
                f.write(output)
            
            # Print status summary periodically
            current_time = time.time()
            if current_time - last_status_time > args.status_interval:
                if args.detailed:
                    print_detailed_status()
                else:
                    print_status_summary()
                last_status_time = current_time
    
    # Final status summary
    print("\n=== Final Status ===")
    print(f"Completed chunks: {success_count}/{len(chunk_files)}")
    print_detailed_status()  # Always show detailed status at the end
    
    # Print any failed chunks
    if success_count < len(chunk_files):
        print("Failed chunks:")
        for future in futures:
            success, chunk_file, _ = future.result()
            if not success:
                print(f"  - {os.path.basename(chunk_file)}")

if __name__ == "__main__":
    main() 