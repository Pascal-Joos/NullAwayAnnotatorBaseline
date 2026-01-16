#!/usr/bin/env python3

import pandas as pd
import sys
import os.path

# Configuration - Input files and reviewer names
FILE1 = '2_manu_initial_scoring_obfuscated(26-75).tsv'
FILE2 = '3_martin_initial_scoring_obfuscated(1-25+51-75).tsv'

def extract_reviewer_name(filename):
    """Extract reviewer name from filename pattern like 'X_name_...' """
    basename = os.path.basename(filename)
    parts = basename.split('_')
    if len(parts) >= 2:
        return parts[1].capitalize()  # Get second part and capitalize
    return "Unknown"

def compare_scores():
    # Extract reviewer names from filenames
    reviewer1_name = extract_reviewer_name(FILE1)
    reviewer2_name = extract_reviewer_name(FILE2)
    
    # Read both TSV files
    print("Reading TSV files...")
    df1 = pd.read_csv(FILE1, sep='\t')
    df2 = pd.read_csv(FILE2, sep='\t')
    
    print(f"File 1 has {len(df1)} rows")
    print(f"File 2 has {len(df2)} rows")
    
    # Create unique identifiers for each sample
    df1['sample_id'] = df1['Benchmark'].astype(str) + '_' + df1['ID'].astype(str)
    df2['sample_id'] = df2['Benchmark'].astype(str) + '_' + df2['ID'].astype(str)
    
    # Find common samples
    common_samples = set(df1['sample_id']) & set(df2['sample_id'])
    print(f"Found {len(common_samples)} common samples")
    
    # Filter to only common samples
    df1_common = df1[df1['sample_id'].isin(common_samples)].copy()
    df2_common = df2[df2['sample_id'].isin(common_samples)].copy()
    
    # Merge on sample_id to compare scores
    merged = df1_common.merge(df2_common, on='sample_id', suffixes=('_rev1', '_rev2'))
    print(f"Merged {len(merged)} rows")
    
    # Check for score differences and agreements
    score_columns = ['SCORE (Patch A)', 'SCORE (Patch B)', 'SCORE (Patch C)']
    different_scores = []
    same_scores = []
    
    for _, row in merged.iterrows():
        score_diff = False
        has_valid_comparison = False
        
        for col in score_columns:
            if pd.notna(row[col + '_rev1']) and pd.notna(row[col + '_rev2']):
                has_valid_comparison = True
                if row[col + '_rev1'] != row[col + '_rev2']:
                    score_diff = True
                    break
        
        if has_valid_comparison:
            if score_diff:
                different_scores.append(row)
            else:
                same_scores.append(row)
    
    print(f"Found {len(different_scores)} samples with different scores")
    print(f"Found {len(same_scores)} samples with identical scores")
    
    if len(different_scores) == 0:
        print("No samples with different scores found.")
    else:
        # Create output dataframe for different scores
        result_data = []
        
        for row in different_scores:
            # Start with base columns from the first file (they should be the same)
            base_columns = ['Benchmark', 'ID', 'Patch A', 'Patch B', 'Patch C', 'Type', 'Message', 'Path', 'Expression']
            result_row = {}
            
            # Add base columns
            for col in base_columns:
                result_row[col] = row[col + '_rev1']  # Use rev1's version (should be identical)
            
            # Add Reviewer1's scores and comment
            result_row[f'SCORE (Patch A)_{reviewer1_name}'] = row['SCORE (Patch A)_rev1']
            result_row[f'SCORE (Patch B)_{reviewer1_name}'] = row['SCORE (Patch B)_rev1'] 
            result_row[f'SCORE (Patch C)_{reviewer1_name}'] = row['SCORE (Patch C)_rev1']
            result_row[f'Comment_{reviewer1_name}'] = row['Comment_rev1']
            
            # Add Reviewer2's scores and comment
            result_row[f'SCORE (Patch A)_{reviewer2_name}'] = row['SCORE (Patch A)_rev2']
            result_row[f'SCORE (Patch B)_{reviewer2_name}'] = row['SCORE (Patch B)_rev2']
            result_row[f'SCORE (Patch C)_{reviewer2_name}'] = row['SCORE (Patch C)_rev2']
            result_row[f'Comment_{reviewer2_name}'] = row['Comment_rev2']
            
            # Add consolidated score columns (empty for now)
            result_row['SCORE (Patch A) Consolidated'] = ""
            result_row['SCORE (Patch B) Consolidated'] = ""
            result_row['SCORE (Patch C) Consolidated'] = ""
            
            # Add error columns (only once, as they should be the same for both reviewers)
            error_columns = ['New or changed errors patch A', 'New or change errors patch B', 'New or changed errors patch C']
            for col in error_columns:
                # Convert to int to avoid decimal representation
                value = row[col + '_rev1']
                result_row[col] = int(value) if pd.notna(value) else ""
            
            result_data.append(result_row)
        
        # Create DataFrame and save differences file
        result_df = pd.DataFrame(result_data)
        output_file = f'scoring_differences_{reviewer1_name}_vs_{reviewer2_name}.tsv'
        result_df.to_csv(output_file, sep='\t', index=False)
        
        print(f"Created {output_file} with {len(result_df)} samples where scores differ")
    
    # Create output file for identical scores (original structure)
    if len(same_scores) > 0:
        # Use original structure from first reviewer
        same_scores_data = []
        
        for row in same_scores:
            # Get all original columns from first reviewer's data
            original_row = {}
            for col in df1.columns:
                if col != 'sample_id':  # Exclude the helper column we added
                    original_row[col] = row[col + '_rev1']
            same_scores_data.append(original_row)
        
        # Create DataFrame and save identical scores file
        same_scores_df = pd.DataFrame(same_scores_data)
        identical_output_file = f'scoring_agreements_{reviewer1_name}_vs_{reviewer2_name}.tsv'
        same_scores_df.to_csv(identical_output_file, sep='\t', index=False)
        
        print(f"Created {identical_output_file} with {len(same_scores_df)} samples where scores are identical")
    else:
        print("No samples with identical scores found.")
    
    # Print some statistics
    if len(different_scores) > 0:
        print("\nScore differences summary:")
        for i, row in enumerate(different_scores):
            print(f"\n{i+1}. {row['Benchmark_rev1']} ID {row['ID_rev1']}:")
            for patch in ['A', 'B', 'C']:
                rev1_score = row[f'SCORE (Patch {patch})_rev1']
                rev2_score = row[f'SCORE (Patch {patch})_rev2']
                if pd.notna(rev1_score) and pd.notna(rev2_score) and rev1_score != rev2_score:
                    print(f"   Patch {patch}: {reviewer1_name}={rev1_score}, {reviewer2_name}={rev2_score}")
    
    if len(same_scores) > 0:
        print(f"\nIdentical scores found in {len(same_scores)} samples:")
        for i, row in enumerate(same_scores[:5]):  # Show first 5 examples
            print(f"  {row['Benchmark_rev1']} ID {row['ID_rev1']}: Scores {row['SCORE (Patch A)_rev1']}, {row['SCORE (Patch B)_rev1']}, {row['SCORE (Patch C)_rev1']}")
        if len(same_scores) > 5:
            print(f"  ... and {len(same_scores) - 5} more")

if __name__ == "__main__":
    compare_scores()