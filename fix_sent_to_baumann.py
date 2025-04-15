import csv
import os
import shutil

# Path to the CSV file
csv_path = 'tmp/processing_results.csv'
backup_path = csv_path + '.bak'

# Create a backup of the original file
shutil.copy2(csv_path, backup_path)
print(f"Created backup at {backup_path}")

# Read the CSV file
rows = []
with open(csv_path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)  # Get the header
    rows.append(header)
    
    # Process each row
    for row in reader:
        if len(row) >= 2:  # Ensure the row has enough columns
            row[1] = 'true'  # Set sent_to_baumann to true
        rows.append(row)

# Write the updated data back to the CSV file
with open(csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(rows)

print(f"Updated {len(rows)-1} rows in {csv_path}")
print("All videos have been marked as sent to Baumann") 