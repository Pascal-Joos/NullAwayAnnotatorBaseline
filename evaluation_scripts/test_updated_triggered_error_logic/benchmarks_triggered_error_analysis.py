"""
This script analyzes the commit impact on the overall error count and triggered errors.
"""
import os
import subprocess
import shlex
import csv
from collections import Counter
import re

PROJECTS = {
    # "conductor":{
    #     "command": "conductor-core:compileJava",
    # },
    # "eureka":{
    #     "command": "eureka-core:compileJava",
    # },
    # "EventBus":{
    #     "command": "compileJava",
    # },
    # "glide":{
    #     "command": ":library:compileDebugJavaWithJavac"
    # },
     "gson":{
         "command": "compileJava",
     },
    # "jadx":{
    #     "command": "jadx-core:compileJava",
    # },
    #"libgdx":{
    #    "command": "gdx:compileJava",
    #},
    # "litiengine":{
    #     "command": "compileJava",
    # },
    # "mockito":{
    #     "command": "compileJava",
    # },
    # "retrofit":{
    #     "command": "retrofit:compileJava",
    # },
    # "spring-boot":{
    #     "command": ":spring-boot-project:spring-boot:compileJava",
    # },
    # "wala-util":{
    #     "command": "compileJava",
    # },
    # "zuul":{
    #     "command": "zuul-core:compileJava",
    # }
}

BENCHMARKS_PATH = "/home/vscode/nullness-benchmarks"
BENCHMARKS_LOGS = "/home/vscode/Desktop/logs"
STATUS_PATH = "/home/vscode/Desktop/status"
VERSION = "agentic-advanced-2-evaluation-run-gpt5.1"
EXECUTION_LOG = f"execution-{os.path.basename(__file__)}.log"

def execute(cwd, command):
    command = shlex.split(command)
    env = os.environ.copy()
    env['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'
    with open(EXECUTION_LOG, "w") as logfile:
        subprocess.run(
            command,
            cwd=cwd,
            stdout=logfile,
            stderr=subprocess.STDOUT
        )

def read_error(project, config):
    command = config["command"]
    benchmark_path = os.path.join(BENCHMARKS_PATH, project)
    error_file = os.path.join(benchmark_path, "annotator-out", "0", "errors.tsv")
    if os.path.exists(error_file):
        # delete file if it exists
        os.remove(error_file)
    execute(benchmark_path, f"./gradlew clean {command} --rerun-tasks --no-build-cache")
    if(not os.path.exists(error_file)):
        print(f"Error file {error_file} does not exist. No errors found.")
        return False, []
    errors = []
    with open(error_file, newline="") as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            row.pop('offset', None)  # Remove 'offset' key if it exists
            row.pop('infos', None)  # Remove 'infos' key if it exists
            if "message" in row:
                # Remove ' (line 123)' pattern from the message
                row["message"] = re.sub(r'\s*\(line \d+\)', '', row["message"])
                if("initializer method" in row["message"]):
                    row["message"] = "initializer method"
            errors.append(row)
    return True, errors

def checkout(project, commit):
    benchmark_path = os.path.join(BENCHMARKS_PATH, project)
    execute(benchmark_path, "git reset --hard")
    execute(benchmark_path, "git pull")
    execute(benchmark_path, f"git checkout {commit}")
    execute(benchmark_path, "git pull")
    

def read_commits(project):
    commits_file = os.path.join(BENCHMARKS_LOGS, project, VERSION, "commits.tsv")
    if not os.path.exists(commits_file):
        print(f"Commits file for {project} does not exist. No commits found.")
        return []
    rows = open(commits_file, 'r').readlines()
    rows = [line.strip() for line in rows if line.strip()]
    rows = rows[1:]  # Skip header
    commits = []
    for row in rows:
        # ID	TYPE	Message	EXPRESSION	PATH	HASH
        parts = row.split("\t")
        if (len(parts) == 3):
            continue
        commits.append({
            "id": parts[0],
            "type": parts[1],
            "message": parts[2],
            "expression": parts[3],
            "path": parts[4],
            "hash": parts[5]
        })
    return commits


def serialize_status(status, path):
    with open(path, 'a') as file:
        import json
        json.dump(status, file, indent=4)
    
 
os.makedirs(os.path.join(STATUS_PATH, VERSION), exist_ok=True)   

for project, config in PROJECTS.items():
    
    
    print(f"Analyzing project: {project}")
    command = config["command"]
    
    checkout(project, "nimak/auto-code-fix")
    success, base = read_error(project, config)
    if not success:
        print(f"Failed to read errors for base commit in project {project}. Skipping analysis.")
        continue
    print(len(base), "errors found in base commit")
    
    commits = read_commits(project)
    if commits is None or len(commits) == 0:
        print(f"No commits found for project {project}. Skipping analysis.")
        continue
    
    counter_base = Counter(["\t".join([row[k] for k in sorted(row.keys())]) for row in base])
    
    status_file = os.path.join(STATUS_PATH, VERSION, project + "-error.json")
    # clean up previous status file if exists, since we are appending to it
    if os.path.exists(status_file):
        os.remove(status_file)
    
    for commit in commits:
        
        
        status = {
            "id": commit["id"],
            "hash": commit["hash"],
            "type": commit["type"],
            "message": commit["message"],
            "expression": commit["expression"],
            "path": commit["path"],
            "errors": 0,
            "triggered_errors": 0,
            "success": False,
        }
            
        print(f"Processing commit {commit['id']} ({commit['hash']})")
        checkout(project, commit["hash"])
        success, errors = read_error(project, config)
        
        
        # print base errors in base.tsv
        with open("base.tsv", "w") as base_file:
            for error in base:
                base_file.write("\t".join([error[k] for k in sorted(error.keys())]) + "\n")
        # print commit errors in commit_errors.tsv
        with open("commit_errors.tsv", "w") as commit_file:
            for error in errors:
                commit_file.write("\t".join([error[k] for k in sorted(error.keys())]) + "\n")

        execution_log = open(EXECUTION_LOG, "r").read()
            
        # if("Nullability" in execution_log or "NullabilityUtil" in execution_log or "Optional.ofNullable" in execution_log):
        #     print("Fixed commit problems.")
        #     status["errors"] = 0
        #     status["triggered_errors"] = 0
        #     status["diff"] = []
        #     status["success"] = True
        #     serialize_status(status, status_file)
        #     continue
        if not success:
            serialize_status(status, status_file)
            print(f"Failed to read errors for commit {commit['id']} in project {project}. Skipping.")
            continue
                
        print(f"Found {len(errors)} errors in commit {commit['id']}")
        
        counter = Counter(["\t".join([row[k] for k in sorted(row.keys())]) for row in errors])
        diff = list((counter - counter_base).elements())
        status["errors"] = len(errors)
        status["triggered_errors"] = len(diff)
        status["diff"] = diff
        status["success"] = True
        serialize_status(status, status_file)
    print(f"Completed analysis for project: {project}")
    
print("All projects analyzed successfully.")