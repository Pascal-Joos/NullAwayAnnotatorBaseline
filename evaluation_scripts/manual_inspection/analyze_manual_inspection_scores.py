import csv
import sys
from collections import defaultdict

def analyze_scores(input_file, output_file):
    """
    Analyze manual inspection scores and calculate statistics per tool.
    
    Args:
        input_file: Path to the TSV file with manual inspection results
        output_file: Path to save the statistics TSV file
    """
    
    # Dictionary to store scores for each tool
    tool_scores = defaultdict(list)
    
    # Track wins/losses/ties
    tool_wins = defaultdict(int)
    tool_losses = defaultdict(int)
    tool_ties = defaultdict(int)
    
    # Track pairwise comparisons
    pairwise_wins = defaultdict(int)
    pairwise_losses = defaultdict(int)
    pairwise_ties = defaultdict(int)
    
    # Track individual pairwise matchups
    pairwise_matchups = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0})
    
    # Read the input TSV file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            # Get the tool assignments for this row
            tool_a = row['Tool A']
            tool_b = row['Tool B'] 
            tool_c = row['Tool C']
            
            # Get the scores (skip if empty)
            score_a = row['SCORE (Patch A) Consolidated'].strip()
            score_b = row['SCORE (Patch B) Consolidated'].strip()
            score_c = row['SCORE (Patch C) Consolidated'].strip()
            
            # Convert to integers if valid
            scores_dict = {}
            if score_a and score_a.isdigit():
                scores_dict[tool_a] = int(score_a)
                tool_scores[tool_a].append(int(score_a))
            
            if score_b and score_b.isdigit():
                scores_dict[tool_b] = int(score_b)
                tool_scores[tool_b].append(int(score_b))
                
            if score_c and score_c.isdigit():
                scores_dict[tool_c] = int(score_c)
                tool_scores[tool_c].append(int(score_c))

            if len(scores_dict) != 3:
                print(f"Warning: Incomplete scores for row ID {row['ID']}. Scores found: {scores_dict}")
            
            # Calculate wins/losses/ties for this row
            if len(scores_dict) >= 2:  # Need at least 2 scores to compare
                min_score = min(scores_dict.values())
                winners = [tool for tool, score in scores_dict.items() if score == min_score]
                
                # Overall wins/losses/ties
                for tool in scores_dict:
                    if tool in winners:
                        if len(winners) <= 1: # Single win only
                            tool_wins[tool] += 1
                        else:  # All 3 win = tie
                            tool_ties[tool] += 1
                    else:
                        tool_losses[tool] += 1
                
                # Pairwise comparisons
                tools = list(scores_dict.keys())
                for i, tool1 in enumerate(tools):
                    for tool2 in tools[i+1:]:
                        score1 = scores_dict[tool1]
                        score2 = scores_dict[tool2]
                        
                        # Create consistent pairing key (alphabetical order)
                        pair_key = f"{min(tool1, tool2)} vs {max(tool1, tool2)}"
                        
                        if score1 < score2:
                            pairwise_wins[tool1] += 1
                            pairwise_losses[tool2] += 1
                            if tool1 < tool2:
                                pairwise_matchups[pair_key]['wins'] += 1
                            else:
                                pairwise_matchups[pair_key]['losses'] += 1
                        elif score2 < score1:
                            pairwise_wins[tool2] += 1
                            pairwise_losses[tool1] += 1
                            if tool1 < tool2:
                                pairwise_matchups[pair_key]['losses'] += 1
                            else:
                                pairwise_matchups[pair_key]['wins'] += 1
                        else:  # tie
                            pairwise_ties[tool1] += 1
                            pairwise_ties[tool2] += 1
                            pairwise_matchups[pair_key]['ties'] += 1
    
    # Calculate statistics for each tool
    stats = []
    
    for tool in sorted(tool_scores.keys()):
        scores = tool_scores[tool]
        
        if not scores:  # No scores for this tool
            continue
            
        # Count scores
        count_1 = scores.count(1)
        count_2 = scores.count(2)
        count_3 = scores.count(3)
        total_scores = len(scores)
        
        # Calculate average
        avg_score = sum(scores) / len(scores) if scores else 0
        
        stats.append({
            'Tool': tool,
            'Total_Scores': total_scores,
            'Count_Score_1': count_1,
            'Count_Score_2': count_2,
            'Count_Score_3': count_3,
            'Average_Score': round(avg_score, 2),
            'Overall_Wins': tool_wins[tool],
            'Overall_Losses': tool_losses[tool],
            'Overall_Ties': tool_ties[tool]
        })
    
    # Write main statistics to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        fieldnames = ['Tool', 'Total_Scores', 'Count_Score_1', 'Count_Score_2', 'Count_Score_3', 'Average_Score', 
                     'Overall_Wins', 'Overall_Losses', 'Overall_Ties']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        
        writer.writeheader()
        for stat in stats:
            writer.writerow(stat)
    
    # Write pairwise statistics to separate file
    pairwise_file = output_file.replace('.tsv', '_pairwise.tsv')
    with open(pairwise_file, 'w', encoding='utf-8') as f:
        fieldnames = ['Matchup', 'First_Tool_Wins', 'Second_Tool_Wins', 'Ties', 'Total_Comparisons']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        
        writer.writeheader()
        for matchup, results in sorted(pairwise_matchups.items()):
            total_comparisons = results['wins'] + results['losses'] + results['ties']
            writer.writerow({
                'Matchup': matchup,
                'First_Tool_Wins': results['wins'],
                'Second_Tool_Wins': results['losses'], 
                'Ties': results['ties'],
                'Total_Comparisons': total_comparisons
            })
    
    # Print summary to console
    pairwise_file = output_file.replace('.tsv', '_pairwise.tsv')
    print(f"Analysis complete. Statistics saved to: {output_file}")
    print(f"Pairwise comparisons saved to: {pairwise_file}")
    print("\nSummary:")
    for stat in stats:
        print(f"{stat['Tool']}: {stat['Total_Scores']} scores, avg = {stat['Average_Score']}, "
              f"wins = {stat['Overall_Wins']}, ties = {stat['Overall_Ties']}, losses = {stat['Overall_Losses']}")
    
    print("\nPairwise Matchup Details:")
    for matchup, results in sorted(pairwise_matchups.items()):
        tools = matchup.split(' vs ')
        total = results['wins'] + results['losses'] + results['ties']
        print(f"{tools[0]} vs {tools[1]} ({total} comparisons): {tools[0]} wins {results['wins']}, {tools[1]} wins {results['losses']}, ties {results['ties']}")

def main():
    input_file = "scoring_merged_all_consolidated.tsv"
    output_file = "manual_inspection_statistics.tsv"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    try:
        analyze_scores(input_file, output_file)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()