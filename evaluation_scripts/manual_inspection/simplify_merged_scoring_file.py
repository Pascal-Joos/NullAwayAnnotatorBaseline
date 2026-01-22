#!/usr/bin/env python3
"""
Script to simplify the TSV file by:
1. Consolidating all comment columns into Reviewer_1_Comment, Reviewer_2_Comment, Reviewer_3_Comment, and Consolidation_Comment
2. Keeping only the consolidated score columns: SCORE (Patch A) Consolidated, SCORE (Patch B) Consolidated, SCORE (Patch C) Consolidated
3. Mapping the scores to match the reviewer comments
"""

import pandas as pd
import sys
import os

def consolidate_comments_and_scores(df):
    """Consolidate all comment patterns into standardized reviewer columns"""
    
    # Create new columns with fixed reviewer assignments:
    # Reviewer_1 = Manu, Reviewer_2 = Martin, Reviewer_3 = Michael
    new_df = df.copy()
    new_df['Reviewer_1_Comment'] = ''  # Manu
    new_df['Reviewer_2_Comment'] = ''  # Martin
    new_df['Reviewer_3_Comment'] = ''  # Michael
    new_df['Consolidation_Comment'] = ''
    new_df['SCORE_A_Reviewer_1'] = pd.NA  # Manu
    new_df['SCORE_B_Reviewer_1'] = pd.NA
    new_df['SCORE_C_Reviewer_1'] = pd.NA
    new_df['SCORE_A_Reviewer_2'] = pd.NA  # Martin
    new_df['SCORE_B_Reviewer_2'] = pd.NA
    new_df['SCORE_C_Reviewer_2'] = pd.NA
    new_df['SCORE_A_Reviewer_3'] = pd.NA  # Michael
    new_df['SCORE_B_Reviewer_3'] = pd.NA
    new_df['SCORE_C_Reviewer_3'] = pd.NA
    
    for idx, row in df.iterrows():
        
        # Map fixed reviewer assignments
        # Reviewer_1 = Manu
        if 'Comment_Manu' in row.index:
            comment = row['Comment_Manu']
            if pd.notna(comment) and comment != '' and comment != 'agreement':
                new_df.at[idx, 'Reviewer_1_Comment'] = comment
        
        new_df.at[idx, 'SCORE_A_Reviewer_1'] = row.get('SCORE (Patch A)_Manu', pd.NA)
        new_df.at[idx, 'SCORE_B_Reviewer_1'] = row.get('SCORE (Patch B)_Manu', pd.NA)
        new_df.at[idx, 'SCORE_C_Reviewer_1'] = row.get('SCORE (Patch C)_Manu', pd.NA)
        
        # Reviewer_2 = Martin
        if 'Comment_Martin' in row.index:
            comment = row['Comment_Martin']
            if pd.notna(comment) and comment != '' and comment != 'agreement':
                new_df.at[idx, 'Reviewer_2_Comment'] = comment
        
        new_df.at[idx, 'SCORE_A_Reviewer_2'] = row.get('SCORE (Patch A)_Martin', pd.NA)
        new_df.at[idx, 'SCORE_B_Reviewer_2'] = row.get('SCORE (Patch B)_Martin', pd.NA)
        new_df.at[idx, 'SCORE_C_Reviewer_2'] = row.get('SCORE (Patch C)_Martin', pd.NA)
        
        # Reviewer_3 = Michael
        if 'Comment_Michael' in row.index:
            comment = row['Comment_Michael']
            if pd.notna(comment) and comment != '' and comment != 'agreement':
                new_df.at[idx, 'Reviewer_3_Comment'] = comment
        
        new_df.at[idx, 'SCORE_A_Reviewer_3'] = row.get('SCORE (Patch A)_Michael', pd.NA)
        new_df.at[idx, 'SCORE_B_Reviewer_3'] = row.get('SCORE (Patch B)_Michael', pd.NA)
        new_df.at[idx, 'SCORE_C_Reviewer_3'] = row.get('SCORE (Patch C)_Michael', pd.NA)
        
        # Handle cases where there's only a single "Comment" column (early rows)
        if 'Comment' in row.index:
            comment = row['Comment']
            if pd.notna(comment) and comment != '' and comment != 'agreement':
                # For single comment cases, check which reviewer's scores are present
                # and assign the comment to that reviewer
                if pd.notna(row.get('SCORE (Patch A)_Manu', pd.NA)):
                    new_df.at[idx, 'Reviewer_1_Comment'] = comment
                elif pd.notna(row.get('SCORE (Patch A)_Martin', pd.NA)):
                    new_df.at[idx, 'Reviewer_2_Comment'] = comment
                elif pd.notna(row.get('SCORE (Patch A)_Michael', pd.NA)):
                    new_df.at[idx, 'Reviewer_3_Comment'] = comment
                else:
                    # If no specific reviewer scores, assume it's the first reviewer
                    new_df.at[idx, 'Reviewer_1_Comment'] = comment
                    # And use the original scores for the first reviewer
                    new_df.at[idx, 'SCORE_A_Reviewer_1'] = row.get('SCORE (Patch A)', pd.NA)
                    new_df.at[idx, 'SCORE_B_Reviewer_1'] = row.get('SCORE (Patch B)', pd.NA)
                    new_df.at[idx, 'SCORE_C_Reviewer_1'] = row.get('SCORE (Patch C)', pd.NA)
        
        # Handle consolidation comment
        if 'Consolidation Comment (Optional)' in row.index:
            consolidation = row['Consolidation Comment (Optional)']
            if pd.notna(consolidation) and consolidation != '':
                new_df.at[idx, 'Consolidation_Comment'] = consolidation
    
    return new_df

def main():
    input_file = 'scoring_merged_all_consolidated_with_hyperlinks.tsv'
    output_file = 'scoring_merged_simplified.tsv'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found!")
        sys.exit(1)
    
    print(f"Reading {input_file}...")
    
    # Read the TSV file
    try:
        df = pd.read_csv(input_file, sep='\t', encoding='utf-8')
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"Original file has {len(df.columns)} columns and {len(df)} rows")
    
    # Consolidate comments and scores
    print("Consolidating comments and scores...")
    new_df = consolidate_comments_and_scores(df)
    
    # Convert score columns to integers
    score_cols = ['SCORE_A_Reviewer_1', 'SCORE_B_Reviewer_1', 'SCORE_C_Reviewer_1',
                  'SCORE_A_Reviewer_2', 'SCORE_B_Reviewer_2', 'SCORE_C_Reviewer_2',
                  'SCORE_A_Reviewer_3', 'SCORE_B_Reviewer_3', 'SCORE_C_Reviewer_3']
    
    for col in score_cols:
        if col in new_df.columns:
            # Convert to integer, keeping NaN as NaN
            new_df[col] = new_df[col].astype('Int64')  # Int64 supports NaN values
    
    # Define the final columns we want to keep
    basic_columns = [
        'Benchmark', 'ID', 'Tool A', 'Tool B', 'Tool C', 'Patch A', 'Patch B', 'Patch C',
        'Type', 'Message', 'Path', 'Expression'
    ]
    
    # Keep only the consolidated score columns
    consolidated_score_columns = [
        'SCORE (Patch A) Consolidated',
        'SCORE (Patch B) Consolidated', 
        'SCORE (Patch C) Consolidated'
    ]
    
    # Individual reviewer score columns
    reviewer_score_columns = [
        'SCORE_A_Reviewer_1', 'SCORE_B_Reviewer_1', 'SCORE_C_Reviewer_1',
        'SCORE_A_Reviewer_2', 'SCORE_B_Reviewer_2', 'SCORE_C_Reviewer_2',
        'SCORE_A_Reviewer_3', 'SCORE_B_Reviewer_3', 'SCORE_C_Reviewer_3'
    ]
    
    # Comment columns (after all scoring columns)
    comment_columns = [
        'Reviewer_1_Comment', 'Reviewer_2_Comment', 'Reviewer_3_Comment',
        'Consolidation_Comment'
    ]
    
    # Optional: add any other columns that might be important
    other_columns = []
    if 'File_Type' in df.columns:
        other_columns.append('File_Type')
    
    # Combine all columns we want to keep in the desired order:
    # Basic info -> Consolidated scores -> Individual reviewer scores -> Comments -> Other
    columns_to_keep = (basic_columns + consolidated_score_columns + 
                      reviewer_score_columns + comment_columns + other_columns)
    
    # Check which columns actually exist in the dataframe
    existing_columns = []
    for col in columns_to_keep:
        if col in new_df.columns:
            existing_columns.append(col)
    
    print(f"Keeping {len(existing_columns)} columns")
    
    # Create the final simplified dataframe
    simplified_df = new_df[existing_columns].copy()
    
    print(f"Simplified file has {len(simplified_df.columns)} columns and {len(simplified_df)} rows")
    
    # Write the simplified TSV file
    try:
        simplified_df.to_csv(output_file, sep='\t', index=False, encoding='utf-8')
        print(f"Successfully wrote simplified file to: {output_file}")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)
    
    # Print summary statistics
    print("\n=== SUMMARY ===")
    print(f"Original columns: {len(df.columns)}")
    print(f"Simplified columns: {len(simplified_df.columns)}")
    print(f"Columns removed: {len(df.columns) - len(simplified_df.columns)}")
    
    # Show a preview of the simplified data
    print(f"\nPreview of simplified data:")
    print(simplified_df.head(3).to_string())

if __name__ == "__main__":
    main()