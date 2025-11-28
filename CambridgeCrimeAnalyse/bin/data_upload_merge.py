import pandas as pd
import glob
import os
import configparser

# Read config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Get folder path from config and strip any extra quotes
folder_path = config['Settings']['folder_path'].strip('"')

# Recursively get all CSV files in subfolders
csv_files = glob.glob(os.path.join(folder_path, '**', '*.csv'), recursive=True)

if not csv_files:
    print("No CSV files found in the folder or subfolders.")
else:
    # Merge all CSV files
    merged_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

    # Save the merged CSV
    merged_file_path = os.path.join(folder_path, 'merged_file.csv')
    merged_df.to_csv(merged_file_path, index=False)

    print(f"All CSV files from '{folder_path}' and subfolders have been merged into '{merged_file_path}'.")
