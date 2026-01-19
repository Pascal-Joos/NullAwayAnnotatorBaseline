#!/usr/bin/env python3
"""
Script to merge all 6 scoring files into one unified file with consolidated scores.

For "agreements" files: Uses "SCORE (Patch A/B/C)" columns as the consolidated scores
For "consolidation" files: Uses "SCORE (Patch A/B/C) Consolidated" columns as the consolidated scores
"""

import pandas as pd
import os
from pathlib import Path


def main():
    # Define the file paths
    base_path = Path(".")
    
    # Agreement files (use original scores as consolidated)
    agreement_files = [
        "scoring_agreements_Manu_vs_Martin_reunobfuscated.tsv",
        "scoring_agreements_Michael_vs_Manu_reunobfuscated.tsv", 
        "scoring_agreements_Michael_vs_Martin_reunobfuscated.tsv"
    ]
    
    # Consolidation files (use consolidated scores)
    consolidation_files = [
        "scoring_consolidation_Manu_vs_Martin_with_hyperlinks_reunobfuscated.tsv",
        "scoring_consolidation_Michael_vs_Manu_with_hyperlinks_reunobfuscated.tsv",
        "scoring_consolidation_Michael_vs_Martin_with_hyperlinks_reunobfuscated.tsv"
    ]
    
    all_data = []
    
    # Process agreement files
    print("Processing agreement files...")
    for file_name in agreement_files:
        file_path = base_path / file_name
        if not file_path.exists():
            print(f"Warning: {file_name} not found, skipping...")
            continue
            
        print(f"Reading {file_name}")
        df = pd.read_csv(file_path, sep='\t')
        
        # Create consolidated score columns using original scores
        df['SCORE (Patch A) Consolidated'] = df['SCORE (Patch A)']
        df['SCORE (Patch B) Consolidated'] = df['SCORE (Patch B)']
        df['SCORE (Patch C) Consolidated'] = df['SCORE (Patch C)']
        
        # Add source file info
        df['File_Type'] = 'agreement'
        
        all_data.append(df)
    
    # Process consolidation files  
    print("Processing consolidation files...")
    for file_name in consolidation_files:
        file_path = base_path / file_name
        if not file_path.exists():
            print(f"Warning: {file_name} not found, skipping...")
            continue
            
        print(f"Reading {file_name}")
        df = pd.read_csv(file_path, sep='\t')
        
        # The consolidated scores are already in the correct columns
        # Just ensure they exist (they should already be there)
        if 'SCORE (Patch A) Consolidated' not in df.columns:
            print(f"Warning: {file_name} missing consolidated score columns")
            continue
        
        # Add source file info
        df['File_Type'] = 'consolidation'
        
        all_data.append(df)
    
    if not all_data:
        print("Error: No data files found!")
        return
    
    # Combine all data
    print("Merging all data...")
    merged_df = pd.concat(all_data, ignore_index=True)
    
    # Convert all score columns to integers
    score_columns = [
        'SCORE (Patch A) Consolidated', 'SCORE (Patch B) Consolidated', 'SCORE (Patch C) Consolidated',
        'SCORE (Patch A)', 'SCORE (Patch B)', 'SCORE (Patch C)',
        'SCORE (Patch A)_Manu', 'SCORE (Patch B)_Manu', 'SCORE (Patch C)_Manu',
        'SCORE (Patch A)_Martin', 'SCORE (Patch B)_Martin', 'SCORE (Patch C)_Martin',
        'SCORE (Patch A)_Michael', 'SCORE (Patch B)_Michael', 'SCORE (Patch C)_Michael',
        'New or changed errors patch A', 'New or change errors patch B', 'New or changed errors patch C'
    ]
    for col in score_columns:
        if col in merged_df.columns:
            # Convert to numeric first, then to int (handles any string values)
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').astype('Int64')
    
    # Define the desired column order for the output
    # Start with the core columns that should be present in all files
    core_columns = [
        'Benchmark', 'ID', 'Tool A', 'Tool B', 'Tool C',
        'Patch A', 'Patch B', 'Patch C',
        'Type', 'Message', 'Path', 'Expression',
        'SCORE (Patch A) Consolidated', 'SCORE (Patch B) Consolidated', 'SCORE (Patch C) Consolidated'
    ]
    
    # Add any additional columns that exist
    additional_columns = []
    for col in merged_df.columns:
        if col not in core_columns and col not in ['File_Type']:
            additional_columns.append(col)
    
    # Final column order
    final_columns = core_columns + additional_columns + ['File_Type']
    
    # Reorder columns (only include columns that actually exist)
    existing_columns = [col for col in final_columns if col in merged_df.columns]
    merged_df = merged_df[existing_columns]
    
    
    # Save the merged file
    output_file = "scoring_merged_all_consolidated.tsv"
    merged_df.to_csv(output_file, sep='\t', index=False)
    
    # Print summary statistics
    print(f"\nMerge completed!")
    print(f"Output file: {output_file}")
    print(f"Total rows: {len(merged_df)}")
    print(f"Agreement file rows: {len(merged_df[merged_df['File_Type'] == 'agreement'])}")
    print(f"Consolidation file rows: {len(merged_df[merged_df['File_Type'] == 'consolidation'])}")
    
    # Show unique benchmarks
    benchmarks = merged_df['Benchmark'].value_counts()
    print(f"\nBenchmarks found:")
    for benchmark, count in benchmarks.items():
        print(f"  {benchmark}: {count} rows")
    
    # Check for missing consolidated scores
    missing_a = merged_df['SCORE (Patch A) Consolidated'].isna().sum()
    missing_b = merged_df['SCORE (Patch B) Consolidated'].isna().sum()
    missing_c = merged_df['SCORE (Patch C) Consolidated'].isna().sum()
    
    if missing_a > 0 or missing_b > 0 or missing_c > 0:
        print(f"\nWarning: Missing consolidated scores found:")
        print(f"  Patch A: {missing_a} missing")
        print(f"  Patch B: {missing_b} missing") 
        print(f"  Patch C: {missing_c} missing")
    else:
        print(f"\nAll consolidated scores are present!")
    
    print(f"\nFirst few rows of consolidated scores:")
    print(merged_df[['Benchmark', 'ID', 'SCORE (Patch A) Consolidated', 'SCORE (Patch B) Consolidated', 'SCORE (Patch C) Consolidated']].head())


if __name__ == "__main__":
    main()