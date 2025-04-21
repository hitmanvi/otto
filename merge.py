import os
import json
import csv
from pathlib import Path

def merge_walmart_data():
    """
    Merge all JSON files in data/walmart directory into a single CSV file.
    """
    # Define paths
    data_dir = "data/walmart"
    output_json = "data/walmart_merged.json"
    output_csv = "data/walmart_merged.csv"
    
    # Create output directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        print(f"Error: Directory {data_dir} does not exist.")
        return
    
    # Get all JSON files
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return
    
    # Filter files to only process those with seller_id less than 5000
    filtered_json_files = []
    for json_file in json_files:
        try:
            # Extract seller_id from filename (removing .json extension)
            seller_id = int(json_file.split('.')[0])
            if seller_id < 5000:
                filtered_json_files.append(json_file)
        except ValueError:
            # Skip files that don't have numeric names
            print(f"Skipping file with non-numeric name: {json_file}")
    
    # Update json_files list to only include filtered files
    json_files = filtered_json_files
    print(f"Processing {len(json_files)} files with seller_id < 5000")

    # Merge all JSON data
    merged_data = []
    for json_file in json_files:
        file_path = os.path.join(data_dir, json_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_data.append(data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    # Save merged JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    # Convert to CSV
    if merged_data:
        # Get field names from the first record
        fieldnames = merged_data[0].keys()
        
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(merged_data)
        
        print(f"Successfully merged {len(merged_data)} records.")
        print(f"Merged JSON saved to: {output_json}")
        print(f"Merged CSV saved to: {output_csv}")
    else:
        print("No data to merge.")

if __name__ == "__main__":
    merge_walmart_data()
