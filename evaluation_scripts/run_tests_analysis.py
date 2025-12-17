"""
This script analyzes the commit impact on the overall error count and triggered errors.
"""
import os
import subprocess
import shlex
import re


PROJECTS = {
    # "conductor":{
    #     "command": "conductor-core:test",
    #     "path": "core/src/main/java",
    #     "java": 11,
    #     "base": 1
    # },
    # "eureka":{
    #     "command": "eureka-core:test",
    #     "path": "eureka-core/src/main/java",
    #     "java": 17,
    #     "base": 0
    # },
    # "glide":{
    #     "command": "test",
    #     "path": "library/src/main/java",
    #     "java": 17,
    #     "base": 0
    # },
    # "gson":{
    #     "path": "gson/src/main/java",
    #     "command": "test",
    #     "java": 17,
    #     "base": 12
    # },
     "jadx":{
         "path": "jadx-core/src/main/java",
         "command": "xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' ./gradlew test -Derrorprone.disable=true",
         "java": 17,
         "base": 0
     },
    # "litiengine":{
    #     "path": "src",
    #     "command": "test",
    #     "java": 17,
    #     "base": 158
    # },
    # "mockito":{
    #     "path": "src/main/java",
    #     "command": "test -x retryTest",
    #     "java": 17,
    #     "base": 57
    # },
    # "retrofit":{
    #     "path": "retrofit/src/main/java",
    #     "command": "test",
    #     "java": 17,
    #     "base": 0
    # },
    # "spring-boot":{
    #     "path": "spring-boot-project/spring-boot/src/main/java",
    #     "command": ":spring-boot-project:spring-boot:test",
    #     "java": 17,
    #     "base": 67
    # },
    # "zuul":{
    #     "path": "zuul-core/src/main/java",
    #     "java": 17,
    #     "base": 0,
    #     "command": "test",
    # },
    #"libgdx":{
    #    "path": "gdx/src",
    #    "java": 17,
    #    "base": 0,
    #    "command": "gdx:test",
    #}
}

BENCHMARKS_PATH = "/home/vscode/nullness-benchmarks"
BENCHMARKS_LOGS = "/home/vscode/Desktop/logs"
TESTS_PATH = "/home/vscode/Desktop/auto-fix-test"
STATUS_PATH = "/home/vscode/Desktop/status"
VERSION = "agentic-basic-2-evaluation-run-gpt5.1"
EXECUTION_LOG = f"execution-{os.path.basename(__file__)}.log"

def execute(cwd, command, java_version=17):
    command = shlex.split(command)
    env = os.environ.copy()
    env["JAVA_HOME"] = f"/usr/lib/jvm/java-{java_version}-openjdk-amd64"
    with open(EXECUTION_LOG, "w") as logfile:
        subprocess.run(
            command,
            cwd=cwd,
            stdout=logfile,
            stderr=subprocess.STDOUT,
        )

def execute_test(cwd, command, commit_id, java_version=17):
    command = shlex.split(command)
    env = os.environ.copy()
    env["JAVA_HOME"] = f"/usr/lib/jvm/java-{java_version}-openjdk-amd64"
    with open(os.path.join(BENCHMARKS_LOGS, project, VERSION, f"test-log-{commit_id}.log"), "w") as logfile:
        subprocess.run(
            command,
            cwd=cwd,
            stdout=logfile,
            stderr=subprocess.STDOUT,
        )

def run_tests(project, config, commit_id):
    runner_test_path = os.path.join(BENCHMARKS_PATH, project)
    execute_test(runner_test_path, f"{config['command']} --rerun-tasks", commit_id, config.get("java", 17))
    tests_output = open(os.path.join(BENCHMARKS_LOGS, project, VERSION, f"test-log-{commit_id}.log"), "r").read()
    # print(f"Tests output for {project}:\n{tests_output}")
    if "BUILD SUCCESSFUL" in tests_output:
        return True, 0
    elif "BUILD FAILED" in tests_output:
        failed_tests = 0
        for line in reversed(tests_output.splitlines()):
            # Match patterns like "12 tests failed"
            match_simple = re.search(r"(\d+)\s+tests failed", line)
            if match_simple:
                failed_tests = int(match_simple.group(1))
                break
            # Match patterns like "1063 tests completed, 12 failed, 1 skipped"
            match_summary = re.search(r"(\d+)\s+tests completed,\s+(\d+)\s+failed", line)
            if match_summary:
                failed_tests = int(match_summary.group(2))
                break
        return False, failed_tests
    return False, tests_output

def checkout(project, commit):
    benchmark_path = os.path.join(BENCHMARKS_PATH, project)
    execute(benchmark_path, "git reset --hard")
    execute(benchmark_path, "git pull")
    execute(benchmark_path, f"git checkout {commit}")
    execute(benchmark_path, "git pull")
    

def read_commits(project):
    commits_file = os.path.join(BENCHMARKS_LOGS, project, VERSION, "commits.tsv")
    rows = open(commits_file, 'r').readlines()
    rows = [line.strip() for line in rows if line.strip()]
    rows = rows[1:]  # Skip header
    commits = []
    for row in rows:
        # ID	TYPE	Message	EXPRESSION	PATH	HASH
        parts = row.split("\t")
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

def write_to_new_metrics_file(project, commit_id, failed):
    previous_metrics_file = os.path.join(BENCHMARKS_LOGS, project, VERSION, "metrics.tsv")
    new_metrics_file = os.path.join(BENCHMARKS_LOGS, project, VERSION, "metrics_new.tsv")
    if not os.path.exists(new_metrics_file):
        # create new metrics file with header
        with open(new_metrics_file, 'w') as new_file:
            new_file.write("ID\tPATCH_GENERATED\tCOMPILATION_ERROR_INTRODUCED\tTARGET_ERROR_RESOLVED\tTARGET_ERROR_RESOLVED_WITHOUT_NEW_ERRORS\tTRIGGERED_NEW_ERRORS\tEXECUTION_TIME_IN_MILLIS\tFAILING_TESTS\n")
    if not os.path.exists(previous_metrics_file):
        print(f"Previous metrics file for {project} does not exist. No metrics to copy.")
        return
    with open(previous_metrics_file, 'r') as prev_file, open(new_metrics_file, 'a') as new_file:
        # Copy over commit_id row from metrics from the previous file to the new but replace the last column "FAILING_TESTS" with the failed status
        for line in prev_file:
            if line.startswith(commit_id + "\t"):
                parts = line.strip().split("\t")
                parts[-1] = str(failed)
                new_file.write("\t".join(parts) + "\n")

def replace_src(project, config):
    benchmark_path = os.path.join(BENCHMARKS_PATH, project)
    if "path" in config:
        src_path = config["path"]
    else:
        raise ValueError(f"src path not defined for project {project}")
    # replace tests in project path with the one in TESTS_PATH
    project_src = os.path.join(benchmark_path, src_path)
    runner_src = os.path.join(TESTS_PATH, project, src_path)
    if not os.path.exists(project_src):
        raise ValueError(f"Src path {project_src} does not exist")
    os.system(f"rm -rf {runner_src}")
    os.system(f"cp -r {project_src} {os.path.dirname(runner_src)}")
    
 
os.makedirs(os.path.join(STATUS_PATH, VERSION), exist_ok=True)   

for project, config in PROJECTS.items():
    print(f"Analyzing project: {project}")
    command = config["command"]
    commits = read_commits(project)        
    status_file = os.path.join(STATUS_PATH, VERSION, project + "-test.json")
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
            "failed": 0,
            "success": True,
        }
        print(f"Processing commit {commit['id']} ({commit['hash']})")
        checkout(project, commit["hash"])
        #replace_src(project, config)
        # input("Press Enter to continue...")
        success, failed = run_tests(project, config, commit['id'])
        if success:
            serialize_status(status, status_file)
            write_to_new_metrics_file(project, commit['id'], "false")
            print(f"All tests passed for commit {commit['id']} / {len(commits)}")
            continue
        if failed == 0:
            print(f"Error in executing tests, no failed tests found for commit {commit['id']} / {len(commits)}")
            print(failed)
        print(f"{failed} tests failed for - {commit['id']} / {len(commits)}")    
        status["failed"] = failed
        status["success"] = False
        serialize_status(status, status_file)
        write_to_new_metrics_file(project, commit['id'], "true")
    print(f"Completed analysis for project: {project}")
    
print("All projects analyzed successfully.")