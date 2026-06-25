#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score
from itertools import combinations
import sys
import os.path

# Configuration - Input files
SCORING_FILES = [
    'evaluation_data/evaluation_results/manual_inspection/initial_scoring/1_michael_initial_scoring_obfuscated(1-50).tsv',
    'evaluation_data/evaluation_results/manual_inspection/initial_scoring/2_manu_initial_scoring_obfuscated(26-75).tsv',
    'evaluation_data/evaluation_results/manual_inspection/initial_scoring/3_martin_initial_scoring_obfuscated(1-25+51-75).tsv'
]

def extract_reviewer_name(filename):
    """Extract reviewer name from filename pattern like 'X_name_...' """
    basename = os.path.basename(filename)
    parts = basename.split('_')
    if len(parts) >= 2:
        return parts[1].capitalize()
    return f"Reviewer{basename.split('_')[0] if basename.split('_')[0].isdigit() else 'Unknown'}"

def load_scoring_data(files):
    """Load all scoring files and merge them by sample"""
    all_data = []
    reviewer_names = []
    
    for file in files:
        if not os.path.exists(file):
            print(f"Warning: File {file} not found, skipping...")
            continue
            
        df = pd.read_csv(file, sep='\t')
        reviewer_name = extract_reviewer_name(file)
        reviewer_names.append(reviewer_name)
        
        # Create sample ID for merging
        df['sample_id'] = df['Benchmark'].astype(str) + '_' + df['ID'].astype(str)
        
        # Keep only necessary columns and add reviewer suffix
        score_cols = ['sample_id', 'Benchmark', 'ID', 'Type', 'Message', 
                     'SCORE (Patch A)', 'SCORE (Patch B)', 'SCORE (Patch C)']
        df_subset = df[score_cols].copy()
        
        # Rename score columns to include reviewer name
        df_subset = df_subset.rename(columns={
            'SCORE (Patch A)': f'SCORE_A_{reviewer_name}',
            'SCORE (Patch B)': f'SCORE_B_{reviewer_name}',
            'SCORE (Patch C)': f'SCORE_C_{reviewer_name}'
        })
        
        all_data.append((df_subset, reviewer_name))
        print(f"Loaded {len(df_subset)} samples from {reviewer_name}")
    
    if len(all_data) < 2:
        raise ValueError("Need at least 2 scoring files for agreement analysis")
    
    # Merge all dataframes on sample_id
    merged = all_data[0][0].copy()
    for df_subset, reviewer_name in all_data[1:]:
        score_columns = [col for col in df_subset.columns if col.startswith('SCORE_')]
        merge_cols = ['sample_id'] + score_columns
        merged = merged.merge(df_subset[merge_cols], on='sample_id', how='outer')
    
    return merged, reviewer_names

def calculate_overall_agreement(data, reviewer_names):
    """Calculate single Cohen's Kappa across all reviewer pairs for all samples"""
    print(f"\n{'='*60}")
    print("OVERALL INTER-RATER AGREEMENT ANALYSIS")
    print(f"{'='*60}")
    
    all_scores_reviewer1 = []
    all_scores_reviewer2 = []
    comparisons = []
    reviewer_pair_counts = {}
    
    # For each sample, find which 2 reviewers scored it and collect their scores
    for _, row in data.iterrows():
        for patch in ['A', 'B', 'C']:
            # Find which reviewers scored this patch for this sample
            available_scores = []
            for reviewer in reviewer_names:
                col = f'SCORE_{patch}_{reviewer}'
                if col in data.columns and pd.notna(row[col]):
                    available_scores.append((reviewer, int(row[col])))
            
            # Should have exactly 2 reviewers per sample
            if len(available_scores) == 2:
                rev1_name, score1 = available_scores[0]
                rev2_name, score2 = available_scores[1]
                
                # Track reviewer pair
                pair = tuple(sorted([rev1_name, rev2_name]))
                reviewer_pair_counts[pair] = reviewer_pair_counts.get(pair, 0) + 1
                
                all_scores_reviewer1.append(score1)
                all_scores_reviewer2.append(score2)
                
                comparisons.append({
                    'sample_id': row['sample_id'],
                    'benchmark': row['Benchmark'],
                    'id': row['ID'],
                    'patch': patch,
                    'reviewer1': rev1_name,
                    'reviewer2': rev2_name,
                    'score1': score1,
                    'score2': score2
                })
            elif len(available_scores) > 2:
                print(f"Warning: Sample {row['sample_id']} Patch {patch} has {len(available_scores)} reviewers (expected 2)")
            # Skip samples with < 2 reviewers (no comparison possible)
    
    if len(all_scores_reviewer1) == 0:
        print("No valid score pairs found")
        return None
    
    # Calculate Cohen's Kappa across all pairs
    kappa = cohen_kappa_score(all_scores_reviewer1, all_scores_reviewer2)
    
    # Calculate statistics
    total_comparisons = len(all_scores_reviewer1)
    agreements = sum(1 for a, b in zip(all_scores_reviewer1, all_scores_reviewer2) if a == b)
    agreement_rate = agreements / total_comparisons * 100
    
    print(f"Overall Statistics:")
    print(f"  Total score comparisons: {total_comparisons}")
    print(f"  Exact agreements: {agreements} ({agreement_rate:.1f}%)")
    print(f"  Cohen's Kappa: {kappa:.3f}")
    print(f"  Interpretation: {interpret_kappa(kappa)}")
    
    # Show distribution of reviewer pairs
    print(f"\nReviewer Pair Distribution:")
    for pair, count in sorted(reviewer_pair_counts.items()):
        pct = count / total_comparisons * 100
        print(f"  {pair[0]} vs {pair[1]}: {count} comparisons ({pct:.1f}%)")
    
    # Show disagreement breakdown
    disagreements = [(s1, s2, comp) for s1, s2, comp in zip(all_scores_reviewer1, all_scores_reviewer2, comparisons) if s1 != s2]
    if disagreements:
        print(f"\nDisagreement Analysis:")
        print(f"  Total disagreements: {len(disagreements)}")
        
        # Count disagreement patterns
        disagreement_patterns = {}
        for s1, s2, comp in disagreements:
            pattern = f"{s1}→{s2}"
            disagreement_patterns[pattern] = disagreement_patterns.get(pattern, 0) + 1
        
        print(f"  Disagreement patterns:")
        for pattern, count in sorted(disagreement_patterns.items()):
            pct = count / len(disagreements) * 100
            print(f"    {pattern}: {count} ({pct:.1f}%)")
        
        # Show some example disagreements
        print(f"\n  Example disagreements:")
        for i, (s1, s2, comp) in enumerate(disagreements[:10]):
            print(f"    {comp['benchmark']} ID {comp['id']} Patch {comp['patch']}: {comp['reviewer1']}={s1}, {comp['reviewer2']}={s2}")
        if len(disagreements) > 10:
            print(f"    ... and {len(disagreements) - 10} more")
    
    return kappa

def calculate_fleiss_kappa_approximation(data, reviewer_names):
    """Show distribution of samples across reviewer pairs"""
    print(f"\n{'='*60}")
    print("SAMPLE DISTRIBUTION ANALYSIS")
    print(f"{'='*60}")
    
    sample_counts = {}
    total_samples = 0
    
    for _, row in data.iterrows():
        # Count how many reviewers scored this sample (across all patches)
        reviewers_for_sample = set()
        for patch in ['A', 'B', 'C']:
            for reviewer in reviewer_names:
                col = f'SCORE_{patch}_{reviewer}'
                if col in data.columns and pd.notna(row[col]):
                    reviewers_for_sample.add(reviewer)
        
        if len(reviewers_for_sample) > 0:
            total_samples += 1
            if len(reviewers_for_sample) == 2:
                pair = tuple(sorted(reviewers_for_sample))
                sample_counts[pair] = sample_counts.get(pair, 0) + 1
            else:
                key = f"{len(reviewers_for_sample)}_reviewers"
                sample_counts[key] = sample_counts.get(key, 0) + 1
    
    print(f"Total samples analyzed: {total_samples}")
    print(f"Sample distribution:")
    
    # Sort tuples and strings separately
    tuple_pairs = {k: v for k, v in sample_counts.items() if isinstance(k, tuple)}
    other_counts = {k: v for k, v in sample_counts.items() if not isinstance(k, tuple)}
    
    for pair, count in sorted(tuple_pairs.items()):
        pct = count / total_samples * 100
        print(f"  {pair[0]} & {pair[1]}: {count} samples ({pct:.1f}%)")
    
    for key, count in sorted(other_counts.items()):
        pct = count / total_samples * 100
        print(f"  {key}: {count} samples ({pct:.1f}%)")
    
    return sample_counts

def interpret_kappa(kappa):
    """Interpret Cohen's Kappa value according to Landis and Koch (1977)"""
    if kappa is None:
        return "N/A"
    elif kappa < 0:
        return "Poor (worse than random)"
    elif kappa < 0.20:
        return "Slight agreement"
    elif kappa < 0.40:
        return "Fair agreement"
    elif kappa < 0.60:
        return "Moderate agreement"
    elif kappa < 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect agreement"

def main():
    import argparse
    import contextlib

    parser = argparse.ArgumentParser(description="Inter-rater agreement analysis.")
    parser.add_argument("--output", default=None, help="Write output to this file instead of stdout only.")
    args = parser.parse_args()

    def _run():
        print("Inter-Rater Agreement Analysis for NullAway Scoring")
        print("=" * 60)

        try:
            merged_data, reviewer_names = load_scoring_data(SCORING_FILES)
            print(f"\nLoaded data for reviewers: {', '.join(reviewer_names)}")
            print(f"Total unique samples: {len(merged_data)}")

            sample_distribution = calculate_fleiss_kappa_approximation(merged_data, reviewer_names)
            kappa_result = calculate_overall_agreement(merged_data, reviewer_names)

            print(f"\n{'='*60}")
            print("SUMMARY")
            print(f"{'='*60}")

            if kappa_result is not None:
                print(f"Overall Cohen's Kappa: {kappa_result:.3f} ({interpret_kappa(kappa_result)})")
            else:
                print("Unable to calculate Cohen's Kappa - no valid score pairs found")

            print(f"\nNote: This kappa value treats all reviewer pairs across all samples")
            print(f"as a single inter-rater agreement measurement, since each sample")
            print(f"is scored by exactly 2 out of 3 total reviewers.")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            with contextlib.redirect_stdout(f):
                _run()
        print(f"Agreement analysis saved to: {args.output}")
    else:
        _run()

if __name__ == "__main__":
    main()