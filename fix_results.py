#!/usr/bin/env python3
"""
Script to fix the format of the processing_results.csv file and ensure
videos from the Baumann database are marked as completed.
"""

import os
import csv
import argparse

def fix_results_file(mark_all_as_completed=False):
    """
    Fix the results file format and optionally mark all videos as completed.
    
    Args:
        mark_all_as_completed: If True, mark all videos in the file as completed
    """
    results_path = os.path.join('tmp', 'processing_results.csv')
    if not os.path.exists(results_path):
        print("Results file not found.")
        return
    
    # Read the current file
    rows = []
    try:
        with open(results_path, 'r', encoding='utf-8') as file:
            # First try to read as CSV
            try:
                reader = csv.reader(file)
                for row in reader:
                    if row:  # Skip empty rows
                        rows.append(row)
            except:
                # If CSV reading fails, reset file pointer and read line by line
                file.seek(0)
                for line in file:
                    line = line.strip()
                    if line:  # Skip empty lines
                        # Check if this is a header line
                        if line.startswith('video_id,'):
                            # This is a header, parse it as CSV
                            rows.append(line.split(','))
                        else:
                            # This is a data line, check if it has commas
                            parts = line.split(',')
                            if len(parts) > 1:
                                # Line has commas, treat as CSV
                                rows.append(parts)
                            else:
                                # Line has no commas, treat as just a video ID
                                rows.append([line])
        
        print(f"Read {len(rows)} rows from results file")
    except Exception as e:
        print(f"Error reading results file: {str(e)}")
        return
    
    # Create a properly formatted file
    try:
        # Create a backup of the original file
        backup_path = results_path + '.bak'
        if os.path.exists(results_path):
            os.rename(results_path, backup_path)
            print(f"Created backup of original file: {backup_path}")
        
        # Write the fixed file with proper headers
        with open(results_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'video_id', 'sent_to_baumann', 'ru_translated', 
                'ar_translated', 'vdocipher_uploaded'
            ])
            writer.writeheader()
            
            # Convert each row to a dictionary with proper field names
            completed_count = 0
            for row in rows:
                # Skip header row if present
                if row and row[0] == 'video_id':
                    continue
                    
                if len(row) >= 1:  # At least has a video ID
                    video_id = row[0].strip()
                    
                    # Skip empty video IDs
                    if not video_id:
                        continue
                    
                    # Get existing values or defaults
                    sent_to_baumann = 'true' if mark_all_as_completed else (row[1].lower() if len(row) > 1 and row[1] else 'false')
                    ru_translated = 'true' if mark_all_as_completed else (row[2].lower() if len(row) > 2 and row[2] else 'false')
                    ar_translated = 'true' if mark_all_as_completed else (row[3].lower() if len(row) > 3 and row[3] else 'false')
                    vdocipher_uploaded = 'true' if mark_all_as_completed else (row[4].lower() if len(row) > 4 and row[4] else 'false')
                    
                    writer.writerow({
                        'video_id': video_id,
                        'sent_to_baumann': sent_to_baumann,
                        'ru_translated': ru_translated,
                        'ar_translated': ar_translated,
                        'vdocipher_uploaded': vdocipher_uploaded
                    })
                    
                    if all(val == 'true' for val in [sent_to_baumann, ru_translated, ar_translated, vdocipher_uploaded]):
                        completed_count += 1
                else:
                    # Handle incomplete rows
                    print(f"Warning: Skipping incomplete row: {row}")
        
        print(f"Fixed results file format: {results_path}")
        print(f"Processed {len(rows)} video records")
        print(f"Videos marked as completed: {completed_count}")
        
        # Update completion markers if requested
        if mark_all_as_completed:
            try:
                import run_parallel
                print("\nUpdating completion markers for all chunks...")
                run_parallel.update_completion_markers()
            except Exception as e:
                print(f"Error updating completion markers: {str(e)}")
        
    except Exception as e:
        print(f"Error fixing results file: {str(e)}")
        # Try to restore the backup if something went wrong
        if os.path.exists(backup_path):
            os.rename(backup_path, results_path)
            print("Restored original file from backup")

def main():
    parser = argparse.ArgumentParser(description='Fix the results file format and mark videos as completed')
    parser.add_argument('--mark-all-completed', action='store_true',
                        help='Mark all videos in the results file as completed')
    parser.add_argument('--update-markers', action='store_true',
                        help='Update completion markers for all chunks after fixing the results file')
    
    args = parser.parse_args()
    
    fix_results_file(mark_all_as_completed=args.mark_all_completed)
    
    if args.update_markers and not args.mark_all_completed:
        try:
            import run_parallel
            print("\nUpdating completion markers for all chunks...")
            run_parallel.update_completion_markers()
        except Exception as e:
            print(f"Error updating completion markers: {str(e)}")

if __name__ == "__main__":
    main() 