import csv
import os
import random

PROJECTS = [
    "conductor",
    "eureka",
    "glide",
    "gson",
    "jadx",
    "litiengine",
    "mockito",
    "retrofit",
    "spring-boot",
    "zuul",
    "libgdx",
    "wala-util"
]

#UNSUPPORTED = ["PASS_NULLABLE", "NONNULL_FIELD_READ_BEFORE_INIT"]

GITHUB_BASE_URL = "https://github.com/Pascal-Joos/{}/commit/{}"

BENCHMARKS_LOGS = "/home/vscode/NullRepairBaseline/evaluation_data/logs"

AGENT_BASELINE_VERSION = "agent_baseline-evaluation-run-gpt5.1"
BASIC_VERSION = "basic-evaluation-run-gpt5.1"
ADVANCED_VERSION = "advanced-evaluation-run-gpt5.1"

def make_github_url(commit_hash, benchmark, name):
    url = GITHUB_BASE_URL.format(benchmark, commit_hash)
    return f'=HYPERLINK("{url}", "{name}")'

errors = {AGENT_BASELINE_VERSION:{}, BASIC_VERSION:{}, ADVANCED_VERSION: {}}



def main():
       
    with open("manual_inspection_samples_with_errors.tsv", "r", encoding="utf-8") as samples_with_errors_file:
        reader = csv.reader(samples_with_errors_file, delimiter='\t')
        # list all rows in the file that are not part of the sample
        rows = list(reader)
        header = rows[0]
        rows = rows[1:]
        for row in rows:
            benchmark = row[0]
            id = row[1]
            tool_a = row[2]
            tool_b = row[3]
            tool_c = row[4]
            patch_a = row[5]
            patch_b = row[6]
            patch_c = row[7]

            if introduced_errors(tool_a, id, patch_a, benchmark):
                introduced_errors_a = 1
            else:
                introduced_errors_a = 0
            if introduced_errors(tool_b, id, patch_b, benchmark):
                introduced_errors_b = 1
            else:
                introduced_errors_b = 0
            if introduced_errors(tool_c, id,  patch_c, benchmark):
                introduced_errors_c = 1
            else:
                introduced_errors_c = 0

            row.append(introduced_errors_a)
            row.append(introduced_errors_b)
            row.append(introduced_errors_c)
        
    with open("manual_inspection_samples_with_errors_and_introduced_errors.tsv", "w", encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter='\t')
        writer.writerow(["Benchmark", "ID", "Tool A", "Tool B", "Tool C", "Patch A", "Patch B", "Patch C", "Type", "Message", "Path", "Expression",  "SCORE(Patch A)", "SCORE(Patch B)", "SCORE(Patch C)", "Comment", "Introduced Errors Patch A", "Introduced Errors Patch B", "Introduced Errors Patch C"])
        # write rows with correct column order
        for row in rows:
            writer.writerow(row)
        

def introduced_errors(tool, id, patch, benchmark):
    if tool == "hash_basic":
        version = BASIC_VERSION
    elif tool == "hash_advanced":
        version = ADVANCED_VERSION
    elif tool == "hash_agent_baseline":
        version = AGENT_BASELINE_VERSION

    metrics_file = os.path.join(BENCHMARKS_LOGS, benchmark, version, "metrics.tsv")
    
    with open(metrics_file, "r", encoding="utf-8") as mf:
        reader = csv.reader(mf, delimiter='\t')
        rows = list(reader)
        header = rows[0]
        data_rows = rows[1:]
        for row in data_rows:
            if row[header.index("ID")] == id:
                introduced_errors = row[header.index("TRIGGERED_NEW_ERRORS")].lower() == "true"
                return introduced_errors
    print(f"Could not find ID {id} in metrics file {metrics_file}")
    return False


    

    
if __name__ == "__main__":
    main()


