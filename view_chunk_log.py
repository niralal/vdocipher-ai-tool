#!/usr/bin/env python3
"""
Script to view and analyze chunk logs.
"""

import os
import argparse
import re

def list_chunks():
    """List all available chunk files"""
    chunks_dir = 'chunks'
    if not os.path.exists(chunks_dir):
        print("Chunks directory not found.")
        return []
    
    chunk_files = []
    for filename in os.listdir(chunks_dir):
        if filename.startswith('chunk_') and filename.endswith('.txt'):
            chunk_files.append(filename)
    
    chunk_files.sort()
    return chunk_files

def view_log(chunk_name, show_errors_only=False, search_term=None):
    """View the log for a specific chunk"""
    chunks_dir = 'chunks'
    log_file = os.path.join(chunks_dir, chunk_name.replace('.txt', '.log'))
    
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return
    
    print(f"=== Log for {chunk_name} ===")
    print(f"Log file: {log_file}")
    print(f"Last modified: {os.path.getmtime(log_file)}")
    print("=" * 60)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as file:
            content = file.readlines()
        
        # Extract video IDs and their status
        video_pattern = re.compile(r"Processing video \d+/\d+: ([a-zA-Z0-9_-]+)")
        success_pattern = re.compile(r"✓ Successfully processed ([a-zA-Z0-9_-]+)")
        fail_pattern = re.compile(r"✗ Failed to process ([a-zA-Z0-9_-]+)")
        error_pattern = re.compile(r"(Error|✗|Failed|Exception)", re.IGNORECASE)
        
        videos = []
        current_video = None
        video_lines = []
        
        for line in content:
            # Check if this is a new video
            video_match = video_pattern.search(line)
            if video_match:
                # Save previous video if any
                if current_video and video_lines:
                    videos.append({
                        'id': current_video,
                        'lines': video_lines,
                        'success': any(success_pattern.search(l) for l in video_lines),
                        'fail': any(fail_pattern.search(l) for l in video_lines),
                        'errors': [l for l in video_lines if error_pattern.search(l)]
                    })
                
                # Start new video
                current_video = video_match.group(1)
                video_lines = [line]
            elif current_video:
                video_lines.append(line)
        
        # Add the last video
        if current_video and video_lines:
            videos.append({
                'id': current_video,
                'lines': video_lines,
                'success': any(success_pattern.search(l) for l in video_lines),
                'fail': any(fail_pattern.search(l) for l in video_lines),
                'errors': [l for l in video_lines if error_pattern.search(l)]
            })
        
        # Print summary
        successful = sum(1 for v in videos if v['success'])
        failed = sum(1 for v in videos if v['fail'])
        print(f"Total videos: {len(videos)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Unknown status: {len(videos) - successful - failed}")
        print("-" * 60)
        
        # Print details based on filters
        for video in videos:
            if show_errors_only and not video['errors']:
                continue
            
            if search_term and search_term.lower() not in '\n'.join(video['lines']).lower():
                continue
            
            status = "✅ SUCCESS" if video['success'] else "❌ FAILED" if video['fail'] else "⚠️ UNKNOWN"
            print(f"\nVideo: {video['id']} - {status}")
            
            if show_errors_only:
                # Only show error lines
                for line in video['errors']:
                    print(line.strip())
            else:
                # Show all lines for this video
                for line in video['lines']:
                    print(line.strip())
        
    except Exception as e:
        print(f"Error reading log file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='View and analyze chunk logs')
    parser.add_argument('chunk', type=str, nargs='?',
                        help='Chunk name (e.g., chunk_001.txt)')
    parser.add_argument('--list', action='store_true',
                        help='List all available chunks')
    parser.add_argument('--errors-only', action='store_true',
                        help='Show only error messages')
    parser.add_argument('--search', type=str,
                        help='Search for a specific term in the logs')
    
    args = parser.parse_args()
    
    if args.list:
        chunks = list_chunks()
        if chunks:
            print("Available chunks:")
            for chunk in chunks:
                log_file = os.path.join('chunks', chunk.replace('.txt', '.log'))
                status = "✅ Log exists" if os.path.exists(log_file) else "❌ No log"
                print(f"  {chunk} - {status}")
        else:
            print("No chunks found.")
        return
    
    if not args.chunk:
        print("Please specify a chunk name or use --list to see available chunks.")
        return
    
    view_log(args.chunk, args.errors_only, args.search)

if __name__ == "__main__":
    main() 