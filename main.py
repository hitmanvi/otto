import os
import re

def remove_files_with_copyright():
    # Get path to data folder
    data_dir = os.path.join(os.path.dirname(__file__), 'otto/data')
    
    # Loop through all html files in data folder
    for filename in os.listdir(data_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(data_dir, filename)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if copyright text exists
            if "1995 bis 2025 OTTO" in content:
                # Remove file if copyright found
                os.remove(file_path)
                print(f"Removed {filename} - contains copyright text")

if __name__ == "__main__":
    remove_files_with_copyright()
