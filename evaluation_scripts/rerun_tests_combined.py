"""
This script analyzes the commit impact on the overall error count and triggered errors.
"""
import os
import subprocess
import shlex
import re


PROJECTS = {
     "conductor":{
         "command": "./gradlew conductor-core:test",
         "path": "core/src/main/java",
         "java": 17,
         "base": 1
     },
     "eureka":{
         "command": "./gradlew eureka-core:test",
         "path": "eureka-core/src/main/java",
         "java": 17,
         "base": 0
     },
     "glide":{
         "command": "./gradlew test",
         "path": "library/src/main/java",
         "java": 17,
         "base": 0
     },
     "gson":{
         "path": "gson/src/main/java",
         "command": "./gradlew test",
         "java": 17,
         "base": 12
     },
     "jadx":{
         "path": "jadx-core/src/main/java",
         "command": "xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' ./gradlew test",
         "java": 17,
         "base": 0
     },
     "litiengine":{
         "path": "src",
         "command": "xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' ./gradlew test",
         "java": 17,
         "base": 158
     },
     "mockito":{
         "path": "src/main/java",
         "command": "./gradlew test",
         "java": 17,
         "base": 57
     },
     "retrofit":{
         "path": "retrofit/src/main/java",
         "command": "./gradlew test",
         "java": 17,
         "base": 0
     },
     "spring-boot":{
         "path": "spring-boot-project/spring-boot/src/main/java",
         "command": "./gradlew :spring-boot-project:spring-boot:test",
         "java": 17,
         "base": 67
     },
     "zuul":{
         "path": "zuul-core/src/main/java",
         "java": 17,
         "base": 0,
         "command": "./gradlew test",
     },
     "wala-util":{
        "path": "wala-util/src/main/java",
        "command": "./gradlew test",
        "java": 17,
        "base": 0
    },
     #"libgdx":{
     #    "path": "gdx/src",
     #    "java": 17,
     #    "base": 0,
     #    "command": "./gradlew gdx:test",
     #}
}

BENCHMARKS_PATH = "/home/vscode/nullness-benchmarks"
BENCHMARKS_LOGS = "/home/vscode/nullrepair_log_files/logs"
TESTS_PATH = "/home/vscode/nullrepair_log_files/auto-fix-test"
STATUS_PATH = "/home/vscode/nullrepair_log_files/status"
VERSION = "agentic-basic-2-combined-evaluation-run-gpt5.1"
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

def execute_test(cwd, command, java_version=17):
    command = shlex.split(command)
    env = os.environ.copy()
    env["JAVA_HOME"] = f"/usr/lib/jvm/java-{java_version}-openjdk-amd64"
    with open(os.path.join(BENCHMARKS_LOGS, project, VERSION, "test-log-combined-new.log"), "w") as logfile:
        subprocess.run(
            command,
            cwd=cwd,
            stdout=logfile,
            stderr=subprocess.STDOUT,
        )

def run_tests(project, config):
    runner_test_path = os.path.join(BENCHMARKS_PATH, project)
    execute_test(runner_test_path, f"{config['command']} -Derrorprone.disable=true --rerun-tasks  --continue", config.get("java", 17))
    tests_output = open(os.path.join(BENCHMARKS_LOGS, project, VERSION, "test-log-combined-new.log"), "r").read()
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

def write_to_test_failure_file(project, failed):
    test_failure_file = os.path.join(BENCHMARKS_LOGS, project, VERSION, "total-test-failures-new.tsv")
    if not os.path.exists(test_failure_file):
        # create new metrics file with header
        with open(test_failure_file, 'w') as new_file:
            new_file.write("TOTAL_TEST_FAILURES\n")
    with open(test_failure_file, 'a') as file:
        file.write(f"{failed}\n")
    

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

    last_commit = commits[-1]
    
    status = {
        "id": last_commit["id"],
        "hash": last_commit["hash"],
        "type": last_commit["type"],
        "message": last_commit["message"],
        "expression": last_commit["expression"],
        "path": last_commit["path"],
        "failed": 0,
        "success": True,
    }
    print(f"Processing commit {last_commit['id']} ({last_commit['hash']})")
    checkout(project, last_commit["hash"])
    #replace_src(project, config)
    # input("Press Enter to continue...")
    success, failed = run_tests(project, config)
    if success:
        serialize_status(status, status_file)
        write_to_test_failure_file(project, failed)
        print(f"All tests passed for commit {last_commit['id']} / {len(commits)}")
        continue
    if failed == 0:
        print(f"Error in executing tests, no failed tests found for commit {last_commit['id']} / {len(commits)}")
        print(failed)
    print(f"{failed} tests failed for - {last_commit['id']} / {len(commits)}")    
    status["failed"] = failed
    status["success"] = False
    serialize_status(status, status_file)
    write_to_test_failure_file(project, failed)
    print(f"Completed analysis for project: {project}")
    
print("All projects analyzed successfully.")