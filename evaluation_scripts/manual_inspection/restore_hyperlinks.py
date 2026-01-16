#!/usr/bin/env python3
"""
Script to restore hyperlinks from sample TSV files to scoring TSV files.
This script merges the hyperlink information from sample files with the scoring data.
"""

import pandas as pd
import os
import sys

def restore_hyperlinks_for_file_pair(sample_file, scoring_file, output_file):
    """
    Restore hyperlinks from sample file to scoring file and save as output file.
    
    Args:
        sample_file (str): Path to the sample file with hyperlinks
        scoring_file (str): Path to the scoring file without hyperlinks
        output_file (str): Path to save the merged file with hyperlinks and scores
    """
    
    print(f"Processing: {sample_file} + {scoring_file} -> {output_file}")
    
    # Read both files
    try:
        # Read sample file (has hyperlinks but no scores)
        sample_df = pd.read_csv(sample_file, sep='\t', dtype=str)
        # Read scoring file (has scores but no hyperlinks)
        scoring_df = pd.read_csv(scoring_file, sep='\t', dtype=str)
        
        print(f"  Sample file columns: {list(sample_df.columns)}")
        print(f"  Scoring file columns: {list(scoring_df.columns)}")
        print(f"  Sample file shape: {sample_df.shape}")
        print(f"  Scoring file shape: {scoring_df.shape}")
        
    except Exception as e:
        print(f"  Error reading files: {e}")
        return False
    
    # Create a copy of the scoring dataframe to preserve all its columns and data
    result_df = scoring_df.copy()
    
    # Create a key for matching rows (Benchmark + ID should be unique)
    sample_df['key'] = sample_df['Benchmark'].astype(str) + '_' + sample_df['ID'].astype(str)
    scoring_df['key'] = scoring_df['Benchmark'].astype(str) + '_' + scoring_df['ID'].astype(str)
    
    # Create a mapping from key to hyperlinks
    hyperlink_mapping = {}
    for _, row in sample_df.iterrows():
        key = row['key']
        hyperlink_mapping[key] = {
            'Patch A': row['Patch A'],
            'Patch B': row['Patch B'], 
            'Patch C': row['Patch C']
        }
    
    # Update the result dataframe with hyperlinks
    for idx, row in result_df.iterrows():
        key = str(row['Benchmark']) + '_' + str(row['ID'])
        if key in hyperlink_mapping:
            result_df.at[idx, 'Patch A'] = hyperlink_mapping[key]['Patch A']
            result_df.at[idx, 'Patch B'] = hyperlink_mapping[key]['Patch B']
            result_df.at[idx, 'Patch C'] = hyperlink_mapping[key]['Patch C']
        else:
            print(f"  Warning: No matching hyperlinks found for key {key}")
    
    # Save the result
    try:
        result_df.to_csv(output_file, sep='\t', index=False)
        print(f"  Successfully created: {output_file}")
        return True
    except Exception as e:
        print(f"  Error saving file: {e}")
        return False

def main():
    """
    Main function to process all file pairs.
    """
    
    # Define the file pairs to process
    file_pairs = [
        {
            'sample': '1_michael_sample_obfuscated(1-50).tsv',
            'scoring': '1_michael_initial_scoring_obfuscated(1-50).tsv',
            'output': '1_michael_initial_scoring_with_hyperlinks(1-50).tsv'
        },
        {
            'sample': '2_manu_sample_obfuscated(26-75).tsv',
            'scoring': '2_manu_initial_scoring_obfuscated(26-75).tsv',
            'output': '2_manu_initial_scoring_with_hyperlinks(26-75).tsv'
        },
        {
            'sample': '3_martin_sample_obfuscated(1-25+51-75).tsv',
            'scoring': '3_martin_initial_scoring_obfuscated(1-25+51-75).tsv',
            'output': '3_martin_initial_scoring_with_hyperlinks(1-25+51-75).tsv'
        }
    ]
    
    print("Restoring hyperlinks from sample files to scoring files...")
    print("=" * 70)
    
    success_count = 0
    total_count = len(file_pairs)
    
    for pair in file_pairs:
        sample_file = pair['sample']
        scoring_file = pair['scoring']
        output_file = pair['output']
        
        # Check if files exist
        if not os.path.exists(sample_file):
            print(f"Error: Sample file not found: {sample_file}")
            continue
            
        if not os.path.exists(scoring_file):
            print(f"Error: Scoring file not found: {scoring_file}")
            continue
        
        # Process the file pair
        if restore_hyperlinks_for_file_pair(sample_file, scoring_file, output_file):
            success_count += 1
        
        print()  # Empty line for readability
    
    print("=" * 70)
    print(f"Processing complete: {success_count}/{total_count} files processed successfully")
    
    if success_count == total_count:
        print("All files processed successfully!")
    else:
        print("Some files had errors. Please check the output above.")

if __name__ == "__main__":
    main()