"""
Utility script to split a large video_ids.csv file into smaller chunks
for parallel processing.
"""

import os
import csv
import argparse

def split_csv(input_file, output_dir, chunk_size):
    """Split a CSV file into smaller chunks"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Read all video IDs
    video_ids = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                video_ids.append(row[0].strip())
    
    # Calculate number of chunks
    total_videos = len(video_ids)
    num_chunks = (total_videos + chunk_size - 1) // chunk_size  # Ceiling division
    
    print(f"Splitting {total_videos} video IDs into {num_chunks} chunks of ~{chunk_size} each")
    
    # Create chunk files
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, total_videos)
        
        chunk_ids = video_ids[start_idx:end_idx]
        output_file = os.path.join(output_dir, f"chunk_{i+1:03d}.txt")
        
        with open(output_file, 'w') as f:
            for video_id in chunk_ids:
                f.write(f"{video_id}\n")
                
        print(f"Created {output_file} with {len(chunk_ids)} video IDs")
    
    return num_chunks

def main():
    parser = argparse.ArgumentParser(description='Split video_ids.csv into smaller chunks')
    parser.add_argument('--input', type=str, default='video_ids.csv', 
                        help='Input CSV file with video IDs')
    parser.add_argument('--output-dir', type=str, default='chunks', 
                        help='Output directory for chunk files')
    parser.add_argument('--chunk-size', type=int, default=10, 
                        help='Number of video IDs per chunk')
    
    args = parser.parse_args()
    
    num_chunks = split_csv(args.input, args.output_dir, args.chunk_size)
    
    print("\nTo process all chunks in parallel, open multiple terminals and run:")
    for i in range(1, num_chunks + 1):
        print(f"Terminal {i}: python main.py {args.output_dir}/chunk_{i:03d}.txt")

if __name__ == "__main__":
    main() 