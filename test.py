import os
import csv
import pandas as pd
from pathlib import Path

def merge_csv_files(directory_path, output_file="merged_output.csv"):
    """
    Merge all CSV files in the specified directory into a single CSV file.
    
    Args:
        directory_path (str): Path to the directory containing CSV files
        output_file (str): Name of the output merged CSV file
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Create Path object
    dir_path = Path(directory_path)
    
    # Check if directory exists
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: Directory {directory_path} does not exist.")
        return False
    
    # Get all CSV files
    csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {directory_path}")
        return False
    
    print(f"Found {len(csv_files)} CSV files to merge.")
    
    # Initialize an empty list to store DataFrames
    all_data = []
    
    # Read each CSV file and append to the list
    for csv_file in csv_files:
        file_path = os.path.join(directory_path, csv_file)
        try:
            df = pd.read_csv(file_path)
            all_data.append(df)
            print(f"Processed: {csv_file} - {len(df)} rows")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    if not all_data:
        print("No data to merge.")
        return False
    
    # Concatenate all DataFrames
    merged_df = pd.concat(all_data, ignore_index=True)
    
    # Create output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    # Save to CSV
    merged_df.to_csv(output_file, index=False)
    print(f"Successfully merged {len(merged_df)} rows from {len(csv_files)} files.")
    print(f"Merged CSV saved to: {output_file}")
    
    return True

if __name__ == "__main__":
    # Example usage
    directory = input("Enter the directory path containing CSV files: ")
    output = input("Enter the output file path (default: merged_output.csv): ") or "merged_output.csv"
    merge_csv_files(directory, output)
