import json
import os
import pandas as pd

PROJECTS = {
     "conductor":{
         "command": "conductor-core:compileJava",
     },
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


def read_error_status(benchmark):
    path = os.path.join(STATUS_PATH, VERSION, f"{benchmark}-error.json")
    if not os.path.exists(path):
        return 0, "x", "x", "x"
    content = open(path, "r").read()
    content = content.replace("}{", "},{")
    content = "{ \"status\": [" + content + "]}"
    status_list = json.loads(content)
    return status_list["status"]


def read_original_metrics_file(benchmark):
    path = os.path.join(BENCHMARKS_LOGS, benchmark, VERSION, "metrics.tsv")
    metrics_df = pd.read_csv(path, sep="\t")
    return metrics_df

for benchmark in PROJECTS.keys():

    metrics_df = read_original_metrics_file(benchmark)

    status_list = read_error_status(benchmark)


    for i in range(len(status_list)):
        
        print(status_list[i]["id"])
        status_item = status_list[i]
        id = int(status_item["id"])
        
        # If the triggered errors check finds zero new errors, set TRIGGERED_NEW_ERRORS to False. 
        if status_item["success"] and status_item["triggered_errors"] == 0:
            metrics_df.at[id-1, "TRIGGERED_NEW_ERRORS"] = False

            # If also the target error is removed, then set TARGET_ERROR_RESOLVED_WITHOUT_NEW_ERRORS to True.
            # Then this accepts instances where the alg. for triggered errors based on number of errors would not accept.
            if metrics_df.at[id-1, "TARGET_ERROR_RESOLVED"] == True:
                metrics_df.at[id-1, "TARGET_ERROR_RESOLVED_WITHOUT_NEW_ERRORS"] = True

    metrics_df.to_csv(os.path.join(BENCHMARKS_LOGS, benchmark, VERSION, "metrics_updated.tsv"), sep="\t", index=False)
    
    
    
