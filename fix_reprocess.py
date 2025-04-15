import csv
import os
import shutil
import sys

# Path to the CSV file
csv_path = 'tmp/processing_results.csv'
backup_path = csv_path + '.bak'

# Create a backup of the original file if it doesn't exist
if not os.path.exists(backup_path):
    shutil.copy2(csv_path, backup_path)
    print(f"Created backup at {backup_path}")

# Read the CSV file and identify failed videos
failed_videos = []
with open(csv_path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)  # Skip the header
    
    # Process each row
    for row in reader:
        if len(row) >= 5:  # Ensure the row has all columns
            # Check if any of the processing steps failed
            if 'false' in row[1:]:
                failed_videos.append(row[0])  # Add video_id to failed list

# Write the list of failed videos to a file
os.makedirs('chunks', exist_ok=True)
with open('chunks/to_reprocess.txt', 'w') as f:
    for video_id in failed_videos:
        f.write(f"{video_id}\n")

print(f"Found {len(failed_videos)} videos that need reprocessing")
print(f"List of videos to reprocess saved to chunks/to_reprocess.txt")
print("You can now run your reprocessing script with this list") 