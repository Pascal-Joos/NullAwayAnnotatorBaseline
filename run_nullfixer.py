import subprocess
import os
from pathlib import Path


BENCHMARKS = [
              "eureka", 
              "litiengine", 
              "mockito",
              "gson", 
              "jadx", 
              "libgdx", 
              "glide", 
              "conductor", 
              "retrofit", 
              "spring-boot", 
              "wala-util", 
              "zuul"
              ]
ANNOTATOR_JAR = "/opt/nullrepair.jar"

def prepare(benchmark):
    return

def run_annotator(benchmark):
    prepare(benchmark)
    commands = []
    commands += ["java", "-jar", ANNOTATOR_JAR]
    commands += [benchmark]
    commands += ["advanced"]
    print(commands)
    subprocess.call(commands)

    prepare(benchmark)
    commands = []
    commands += ["java", "-jar", ANNOTATOR_JAR]
    commands += [benchmark]
    commands += ["basic"]
    print(commands)
    subprocess.call(commands)

    prepare(benchmark)
    commands = []
    commands += ["java", "-jar", ANNOTATOR_JAR]
    commands += [benchmark]
    commands += ["agent_baseline"]
    print(commands)
    subprocess.call(commands)
    
    

for benchmark in BENCHMARKS:
    # pkill -f '.*GradleDaemon.*'
    print(f"Running NullRepair for {benchmark}...")
    subprocess.run(["pkill", "-f", "GradleDaemon"])
    run_annotator(benchmark)
    print(f"Finished running NullRepair for {benchmark}.")
print("All benchmarks processed.")