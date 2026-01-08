import os
import json
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

GITHUB_BASE_URL = "https://github.com/nimakarimipour/{}/commit/{}"

def make_github_url(commit_hash, benchmark, name):
    url = GITHUB_BASE_URL.format(benchmark, commit_hash)
    return f'=HYPERLINK("{url}", "{name}")'

errors = {"agentic-basic-1":{}, "agentic-advanced-1": {}}

def filter_errors(benchmark, version):
    path = os.path.join(f"../status/{version}", f"{benchmark}-error.json")
    if not os.path.exists(path):
        return
    if(benchmark not in errors[version]):
        errors[version][benchmark] = {}
        
        
    content = open(path, "r").read()
    content = content.replace("}{", "},{")
    content = "{ \"status\": [" + content + "]}"
    result = json.loads(content)
    for status in result["status"]:
        if status["success"] == False or status["type"] in UNSUPPORTED:
            continue
        if status["triggered_errors"] < 2:
            e_id = status["id"]
            info = {
                "id": e_id,
                "hash": status["hash"],
                "type": status["type"],
                "message": status["message"],
                "path": status["path"],
                "expression": status["expression"],
            }
            errors[version][benchmark][e_id] = info


def main():
    for benchmark in PROJECTS:
        filter_errors(benchmark, "agentic-basic-1")
        filter_errors(benchmark, "agentic-advanced-1")

    sample = []

    for benchmark in PROJECTS:
        ids_in_basic = set(errors["agentic-basic-1"][benchmark].keys())
        ids_in_advanced = set(errors["agentic-advanced-1"][benchmark].keys())
        
        common_ids = ids_in_basic.intersection(ids_in_advanced)
        for e_id in common_ids:
            basic_error = errors["agentic-basic-1"][benchmark][e_id]
            advanced_error = errors["agentic-advanced-1"][benchmark][e_id]
            sample.append({
                "benchmark": benchmark,
                "id": e_id,
                "hash_basic": basic_error["hash"],
                "hash_advanced": advanced_error["hash"],
                "type": basic_error["type"],
                "message": basic_error["message"],
                "path": basic_error["path"],
                "expression": basic_error["expression"],
            })
    
    # select a random sample of 75:
    sample = random.sample(sample, 75)
    print("benchmark, id, hash_basic, hash_advanced, type, message, path, expression")
    for item in sample:
        keys = ["hash_basic", "hash_advanced"]
        shuffled_keys = random.sample(keys, len(keys))
        print(f"{item['benchmark']}\t{item['id']}\t{make_github_url(item[shuffled_keys[0]], item['benchmark'], 'Github')}\t{make_github_url(item[shuffled_keys[1]], item['benchmark'], 'Github')}\t{item['type']}\t{item['message']}\t{item['path']}\t{item['expression']}")

if __name__ == "__main__":
    main()


