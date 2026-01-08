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

UNSUPPORTED = ["PASS_NULLABLE", "NONNULL_FIELD_READ_BEFORE_INIT"]

GITHUB_BASE_URL = "https://github.com/Pascal-Joos/{}/commit/{}"

BENCHMARKS_LOGS = "/home/vscode/Desktop/logs"

AGENT_BASELINE_VERSION = "agentic-agent_baseline-2-evaluation-run-gpt5.1"
BASIC_VERSION = "agentic-basic-2-evaluation-run-gpt5.1"
ADVANCED_VERSION = "agentic-advanced-2-evaluation-run-gpt5.1"

def make_github_url(commit_hash, benchmark, name):
    url = GITHUB_BASE_URL.format(benchmark, commit_hash)
    return f'=HYPERLINK("{url}", "{name}")'

errors = {AGENT_BASELINE_VERSION:{}, BASIC_VERSION:{}, ADVANCED_VERSION: {}}

def filter_errors(benchmark, version):
    commits_file_path = os.path.join(BENCHMARKS_LOGS, benchmark, version, "commits.tsv")
    metrics_file_path = os.path.join(BENCHMARKS_LOGS, benchmark, version, "metrics.tsv")
    if not os.path.exists(commits_file_path) or not os.path.exists(metrics_file_path):
        return
    if(benchmark not in errors[version]):
        errors[version][benchmark] = {}
        
    commits_dict = {}
    metrics_dict = {}
    
    with open(commits_file_path, newline="", encoding="utf-8") as f:
        commits_reader = csv.DictReader(f, delimiter="\t")
        for commit_row in commits_reader:
            commits_dict[commit_row["ID"]] = commit_row
    
    with open(metrics_file_path, newline="", encoding="utf-8") as mf:
        metrics_reader = csv.DictReader(mf, delimiter="\t")
        for metric_row in metrics_reader:
            metrics_dict[metric_row["ID"]] = metric_row
    
    # Match commits and metrics by ID
    for commit_id in commits_dict:
        if commit_id not in metrics_dict:
            continue
        commit_row = commits_dict[commit_id]
        metric_row = metrics_dict[commit_id]
        
        if not metric_row["PATCH_GENERATED"] or commit_row["TYPE"] in UNSUPPORTED:
            continue
        # Check that target error is resolved and no failing tests. Maybe these are to strict conditions.
        if metric_row["TARGET_ERROR_RESOLVED"] and not metric_row["FAILING_TESTS"]:
            info = {
                "id": commit_row["ID"],
                "hash": commit_row["HASH"],
                "type": commit_row["TYPE"],
                "message": commit_row["Message"],
                "path": commit_row["PATH"],
                "expression": commit_row["EXPRESSION"],
            }
            errors[version][benchmark][commit_row["ID"]] = info


def main():
    for benchmark in PROJECTS:
        filter_errors(benchmark, BASIC_VERSION)
        filter_errors(benchmark, ADVANCED_VERSION)
        filter_errors(benchmark, AGENT_BASELINE_VERSION)

    sample = []

    for benchmark in PROJECTS:
        ids_in_basic = set(errors[BASIC_VERSION][benchmark].keys())
        ids_in_advanced = set(errors[ADVANCED_VERSION][benchmark].keys())
        ids_in_agent_baseline = set(errors[AGENT_BASELINE_VERSION][benchmark].keys())
        
        common_ids = ids_in_agent_baseline.intersection(ids_in_basic).intersection(ids_in_advanced)
        for e_id in common_ids:
            basic_error = errors[BASIC_VERSION][benchmark][e_id]
            advanced_error = errors[ADVANCED_VERSION][benchmark][e_id]
            agent_baseline_error = errors[AGENT_BASELINE_VERSION][benchmark][e_id]
            sample.append({
                "benchmark": benchmark,
                "id": e_id,
                "hash_basic": basic_error["hash"],
                "hash_advanced": advanced_error["hash"],
                "hash_agent_baseline": agent_baseline_error["hash"],
                "type": basic_error["type"],
                "message": basic_error["message"],
                "path": basic_error["path"],
                "expression": basic_error["expression"],
            })
    
    # select a random sample of 75:
    sample = random.sample(sample, 75)
    print("benchmark, id, hash_basic, hash_advanced, hash_agent_baseline, type, message, path, expression")
    for item in sample:
        keys = ["hash_basic", "hash_advanced", "hash_agent_baseline"]
        shuffled_keys = random.sample(keys, len(keys))
        print(f"{item['benchmark']}\t{item['id']}\t{make_github_url(item[shuffled_keys[0]], item['benchmark'], 'Github')}\t{make_github_url(item[shuffled_keys[1]], item['benchmark'], 'Github')}\t{make_github_url(item[shuffled_keys[2]], item['benchmark'], 'Github')}\t{item['type']}\t{item['message']}\t{item['path']}\t{item['expression']}")
if __name__ == "__main__":
    main()


