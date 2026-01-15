#!/usr/bin/env python3
"""
Script to merge calculated error counts into the unobfuscated before TSV file.
"""
import csv

# Read the calculated errors file to get the error counts
calculated_errors = {}
with open("manual_inspection_samples_with_calculated_errors.tsv", "r", encoding="utf-8") as calc_file:
    reader = csv.DictReader(calc_file, delimiter='\t')
    for row in reader:
        key = (row['Benchmark'], row['ID'])
        calculated_errors[key] = {
            'Introduced Errors Patch A': row['Introduced Errors Patch A'],
            'Introduced Errors Patch B': row['Introduced Errors Patch B'], 
            'Introduced Errors Patch C': row['Introduced Errors Patch C']
        }

# Read the unobfuscated before file and merge error counts
output_file = "manual_inspection_sample_unobfuscated_with_errors.tsv"
with open("manual_inspection_sample_unobfuscated_before.tsv", "r", encoding="utf-8") as before_file:
    reader = csv.DictReader(before_file, delimiter='\t')
    fieldnames = list(reader.fieldnames)
    
    # Add the error count columns if they don't exist
    error_columns = ['Introduced Errors Patch A', 'Introduced Errors Patch B', 'Introduced Errors Patch C']
    for col in error_columns:
        if col not in fieldnames:
            fieldnames.append(col)
    
    # Write the merged data
    with open(output_file, "w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        
        for row in reader:
            key = (row['Benchmark'], row['ID'])
            
            # Add error counts if available, otherwise set to 0
            if key in calculated_errors:
                row.update(calculated_errors[key])
            else:
                row['Introduced Errors Patch A'] = '0'
                row['Introduced Errors Patch B'] = '0' 
                row['Introduced Errors Patch C'] = '0'
            
            writer.writerow(row)

print(f"Merged file created: {output_file}")
print(f"Found error data for {len(calculated_errors)} entries")