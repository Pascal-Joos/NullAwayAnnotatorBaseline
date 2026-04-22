# NullRepair

## 1. Setup NullRepair

### 1.1 Requirements

### 1.2 Installation using VS Code Dev Container

1. Clone this repository using ssh and checkout the branch `joos/auto-code-fix-baseline`.

2. Run: ```git submodule update --init --recursive``` to initialize the mini-swe-agent submodule.

3. Run: `bash checkout_logs_and_benchmarks.sh`.  
This clones the nullrepair_log_files repository into `../nullrepair_log_files` and the target projects for the experiment into `../nullness-benchmarks` (i.e., at the same level as the nullrepair repository).

4. Reopen the project in a devcontainer using the VSCode Dev Container extension. All needed dependencies and setup steps are then executed automatically. Wait until the postcreatecommand finishes executing and the terminal is ready to use.

5. Activate the Python environment by running (if not yet active):  
```source .venv/bin/activate```

6. Configure the OpenAI API key by running the script `set_openai_key.py` and pasting the key when prompted. This will write the API key to the mini-SWE-agent configuration file and add it to a .env file.

## 2. Quick Run

Then run either NullRepair (advanced), the basic baseline (basic), or the agentic baseline (agent_baseline).  
Per default the project is reset for each error. Set --combined to stack successful error patches.  

Example run:  
```java -jar annotator-core/build/libs/annotator-core-1.3.16-SNAPSHOT.jar eureka agent_baseline```

### Results from our evaluation

All evaluation log files, scores from the manual assessment, as well as all created plots are publicly available here: [https://github.com/Pascal-Joos/nullrepair_log_files](https://github.com/Pascal-Joos/nullrepair_log_files).

## 3. Inspecting Logs and Data

## 4. Reproduce Tables and Figures in the Paper

## 5. Run a large-scale Experiment

## 6. Run on Your Own Project

## 7. Customize NullRepair

## 8. Implementation