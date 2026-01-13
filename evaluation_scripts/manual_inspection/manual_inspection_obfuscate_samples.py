#!/usr/bin/env python3
"""
Script to create a copy of the manual inspection TSV file with Tool A, Tool B, and Tool C columns removed.
"""

import csv
import sys
from pathlib import Path

def remove_tool_columns(input_file, output_file):
    """
    Remove Tool A, Tool B, and Tool C columns from the TSV file.
    
    Args:
        input_file (str): Path to the input TSV file
        output_file (str): Path to the output TSV file
    """
    
    # Column names to remove
    columns_to_remove = {'Tool A', 'Tool B', 'Tool C'}
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter='\t')
            
            # Read the header row
            header = next(reader)
            
            # Find indices of columns to remove
            indices_to_remove = []
            for i, col_name in enumerate(header):
                if col_name in columns_to_remove:
                    indices_to_remove.append(i)
            
            print(f"Found columns to remove at indices: {indices_to_remove}")
            print(f"Column names: {[header[i] for i in indices_to_remove]}")
            
            # Create new header without the specified columns
            new_header = [col for i, col in enumerate(header) if i not in indices_to_remove]
            
            # Write to output file
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile, delimiter='\t')
                
                # Write new header
                writer.writerow(new_header)
                
                # Process each data row
                for row in reader:
                    # Remove columns at specified indices
                    new_row = [cell for i, cell in enumerate(row) if i not in indices_to_remove]
                    writer.writerow(new_row)
        
        print(f"Successfully created {output_file}")
        print(f"Original columns: {len(header)}")
        print(f"New columns: {len(new_header)}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

def main():
    # Define input and output file paths
    input_file = "manual_inspection_sample_unobfuscated.tsv"
    output_file = "manual_inspection_sample_obfuscated.tsv"
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found in current directory.")
        print(f"Current directory: {Path.cwd()}")
        sys.exit(1)
    
    print(f"Processing {input_file}...")
    remove_tool_columns(input_file, output_file)

if __name__ == "__main__":
    main()