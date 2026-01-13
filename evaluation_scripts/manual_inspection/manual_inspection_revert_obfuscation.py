#!/usr/bin/env python3
"""
Script to merge Tool A, Tool B, and Tool C columns from the unobfuscated file
back into the obfuscated file, creating a complete merged TSV file.
"""

import csv
import sys
from pathlib import Path

def merge_tool_columns(unobfuscated_file, obfuscated_file, output_file):
    """
    Merge Tool A, Tool B, and Tool C columns from unobfuscated file into obfuscated file.
    
    Args:
        unobfuscated_file (str): Path to the file with Tool columns
        obfuscated_file (str): Path to the file without Tool columns
        output_file (str): Path to the output merged file
    """
    
    # First, read the unobfuscated file to extract tool information
    tool_data = {}
    
    try:
        with open(unobfuscated_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile, delimiter='\t')
            
            for row in reader:
                # Use Benchmark + ID as the key for matching
                key = (row['Benchmark'], row['ID'])
                tool_data[key] = {
                    'Tool A': row['Tool A'],
                    'Tool B': row['Tool B'], 
                    'Tool C': row['Tool C']
                }
        
        print(f"Loaded tool data for {len(tool_data)} records from {unobfuscated_file}")
        
        # Now read the obfuscated file and merge the tool columns
        with open(obfuscated_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile, delimiter='\t')
            
            # Get the original fieldnames and insert Tool columns at the right positions
            original_fieldnames = reader.fieldnames
            
            # Find where to insert the Tool columns (after ID, before Patch A)
            new_fieldnames = []
            for field in original_fieldnames:
                new_fieldnames.append(field)
                if field == 'ID':
                    # Insert Tool columns after ID
                    new_fieldnames.extend(['Tool A', 'Tool B', 'Tool C'])
            
            print(f"Original columns: {len(original_fieldnames)}")
            print(f"New columns: {len(new_fieldnames)}")
            
            # Write to output file
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=new_fieldnames, delimiter='\t')
                
                # Write header
                writer.writeheader()
                
                # Process each row from obfuscated file
                matched_count = 0
                unmatched_count = 0
                
                for row in reader:
                    # Create key for matching
                    key = (row['Benchmark'], row['ID'])
                    
                    # Add tool columns if we have the data
                    if key in tool_data:
                        row.update(tool_data[key])
                        matched_count += 1
                    else:
                        # If no match found, add empty tool columns
                        row['Tool A'] = ''
                        row['Tool B'] = ''
                        row['Tool C'] = ''
                        unmatched_count += 1
                        print(f"Warning: No tool data found for {key}")
                    
                    writer.writerow(row)
                
                print(f"Successfully created {output_file}")
                print(f"Matched records: {matched_count}")
                print(f"Unmatched records: {unmatched_count}")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing files: {e}")
        sys.exit(1)

def main():
    # Define file paths
    unobfuscated_file = "manual_inspection_sample_unobfuscated.tsv"
    obfuscated_file = "manual_inspection_sample_obfuscated.tsv"
    output_file = "manual_inspection_sample_reunobfuscated.tsv"
    
    # Check if input files exist
    for file_path in [unobfuscated_file, obfuscated_file]:
        if not Path(file_path).exists():
            print(f"Error: Input file '{file_path}' not found in current directory.")
            print(f"Current directory: {Path.cwd()}")
            sys.exit(1)
    
    print(f"Merging tool columns from {unobfuscated_file} into {obfuscated_file}...")
    merge_tool_columns(unobfuscated_file, obfuscated_file, output_file)
    
    print(f"\nMerge completed! Output saved to: {output_file}")

if __name__ == "__main__":
    main()