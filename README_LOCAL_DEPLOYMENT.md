# NullRepair

## 1. Setup NullRepair

### 1.1 Requirements

The VS Code Dev Container extension with VS Code.  
Tested with Docker 29.4.1

### 1.2 Installation using VS Code Dev Container

Don't open the VS Code Dev Container before completing the steps 1 to 3.

1. Clone this repository using ssh and checkout the branch `joos/auto-code-fix-baseline`.

2. Run: ```git submodule update --init --recursive``` to initialize the mini-swe-agent submodule.

3. Run: `bash checkout_benchmarks.sh`.  
This clones the target projects for the experiment into `benchmarks`.  
Refer to these folders for the logs of executed runs and for any commits created by NullRepair.

1. Reopen the project in a devcontainer using the VSCode Dev Container extension. All needed dependencies and setup steps are then executed automatically. Wait until the postcreatecommand finishes executing and the terminal is ready to use.

2. Activate the Python environment by running (if not yet active):  
```source .venv/bin/activate```

1. Configure the OpenAI API key by running the script `set_openai_key.py` and pasting the key when prompted. This will write the API key to the mini-SWE-agent configuration file and add it to a .env file.  
This is needed to run NullRepair and the baselines, which use the OpenAI API.  
For a lightweight reproduction of the experiment results from the log files, the API key is not needed (see 4.).  
```python3 set_openai_key.py```

### 1.3 Build a Prebuilt Artifact Docker Image (for submission)

For artifact submission, you can build a preconfigured Docker image archive that includes all dependencies, initialized submodules, and freshly checked-out benchmark repositories.

From the repository root:

```bash
bash create_artifact_image.sh
```

This creates `nullrepair_artifact_image.tar` (default) in the repository root. The script excludes `.env` from the image build context so API keys are not embedded.

The image is built from the persistent [Dockerfile.artifact](Dockerfile.artifact) in the repository root, and the build context is filtered by [.dockerignore](.dockerignore).

Load and run the image:

```bash
docker load -i nullrepair_artifact_image.tar
docker run --rm -it --name nullrepair_artifact nullrepair-issta-artifact:latest bash
```

Inside the container, the repository is available at `/home/vscode/NullRepairBaseline` and uses the `vscode` user to match the devcontainer environment.

## 2. Quick Run

A small example run where NullRepair is run on three errors of project eureka can be executed with the following command:  
```java -jar annotator-core/build/libs/annotator-core-1.3.16-SNAPSHOT.jar eureka --mode advanced --selectedErrorIds 2,4,5```

Expected console output (truncated):  

```text
ANNOTATOR VERSION: 3, BUILD: 6
Received arguments: eureka, --mode, advanced, --selectedErrorIds, 2,4,5
Running eureka benchmark in advanced mode.
Resolve remaining errors mode: ADVANCED
Selected error IDs: [2, 4, 5]
Configuring logging for benchmark: eureka, branch: nimak/agentic-advanced-3
Root path for logs: /home/vscode/NullRepairBaseline/evaluation_data/logs/eureka/agentic-advanced-3
Running on branch name: nimak/agentic-advanced-3
Starting annotator...
Preprocessing...
Annotating...false
Loading cache...
Loaded 0 entries from cache.
Max Depth level: 1
Analyzing at level 1, Scheduling for: 5 builds for: 14 fixes
Processing 100% [===============================================================================================================================================] 5/5 (0:00:18 / 0:00:00) 
2 : TOP LEVEL CALL TO FIX ERROR: Type='METHOD_NO_INIT', message='initializer method does not guarantee @NonNull field serverConfig (line 106) is initialized along all control-flow paths (remember to check for exceptions or early returns).'
/home/vscode/benchmarks/eureka/eureka-core/src/main/java/com/netflix/eureka/RateLimitingFilter.java:114
  public RateLimitingFilter() {}
Resetting NullAwayCodeFix state.
Sending request to OpenAI...
Response received from OpenAI.
Token usage - Uncached Prompt: 406, Cached Prompt: 0, Completion: 497, Total: 903
Cached response
Finished processing.
Time taken to fix error: 3713 ms
Writing log to file...
Logging ChatGPT token usage...
Calculating run metrics...
Running tests...
Trying to commit changes...
Commiting changes...
4 : TOP LEVEL CALL TO FIX ERROR: Type='DEREFERENCE_NULLABLE', message='dereferenced expression resourceRecordSetWithHostedZone is @Nullable'
/home/vscode/benchmarks/eureka/eureka-core/src/main/java/com/netflix/eureka/aws/Route53Binder.java:277
      resourceRecordSetWithHostedZone
...
```

Logs are then located at `evaluation_data/logs/eureka/agentic-advanced-3` and the changes made by NullRepair are committed to the branch `nimak/agentic-advanced-3` in the target project repository at `benchmarks/eureka`.

TODO: More detailed instructions for inspecting the changes made by NullRepair and the logs of the run.

## 3. Inspecting Logs and Data

See `evaluation_data/logs` for the logs of executed runs and `benchmarks` for the target projects.  
The log files are organized by project and experiment mode. Each run creates a new log folder.

TODO: More details

## 4. Reproduce Tables and Figures in the Paper

TODO: Add instructions.

## 5. Run a large-scale Experiment

Follow the installation steps in 1. and then run one of the following commands to run a large-scale experiment on a target project.  
Run either NullRepair (advanced), the SinglePrompt baseline (basic), or the mini-SWE-agent baseline (agent_baseline).  
Per default the project is reset for each error (patch-level analysis). Set --combined to stack successful error patches (aggregate-level analysis).  

The following commands run the experiment on project eureka.  

Run NullRepair on project eureka:  
```java -jar annotator-core/build/libs/annotator-core-1.3.16-SNAPSHOT.jar eureka --mode advanced```

Run SinglePrompt baseline on project eureka:  
```java -jar annotator-core/build/libs/annotator-core-1.3.16-SNAPSHOT.jar eureka --mode basic```

Run mini-SWE-agent baseline on project eureka:  
```java -jar annotator-core/build/libs/annotator-core-1.3.16-SNAPSHOT.jar eureka --mode agent_baseline```

List of all projects: conductor, eureka, glide, gson, jadx, libgdx, litiengine, mockito, retrofit, spring-boot, wala-util, zuul

Experiments on different projects can be run in parallel. However, multiple experiments on the same project cannot be run simultaneously.  
The logs of each run are stored in a new folder in `evaluation_data/logs` with the name of the project and experiment mode.

If you want to run all experiments on all projects with all three modes and both patch-level and aggregate-level analysis, you can run the following script:  

```bash
python3 run_nullrepair_and_baselines.py
```

This is very long-running and expensive. We recommend running the experiments in smaller batches.

## 6. Run on Your Own Project

You can run NullRepair on new Java projects.  
The following instructions assume that the target project uses Gradle.  
The setup of a new project is illustrated with the example project https://github.com/cbeust/jcommander/tree/3-lts with Java 17.  

1. Create a fork of the project if you do not have write access.  
We have created a fork for the example project here: https://github.com/Pascal-Joos/jcommander.

2. Clone the target project to the benchmarks directory and checkout the branch you want to run on.  

    ```bash
    cd benchmarks
    git clone git@github.com:Pascal-Joos/jcommander.git 
    cd jcommander 
    git checkout 3-lts
    ```

3. Create a new branch from this branch named `nimak/auto-code-fix`.

    ```bash
    git checkout -b nimak/auto-code-fix
    ```

4. Update the `build.gradle` or `build.gradle.kts` file to include the NullAway dependency and annotation processing. Commit these changes.  
See the following commit for an example on how to do this:  
https://github.com/Pascal-Joos/jcommander/commit/f608a5ae8a069d05f588a4d5b1b0c130b7594bbd  
This includes adding a file prepare.sh.

5. Run the `prepare.sh` script to prepare the project for NullRepair.

6. Run the gradlew spotlessApply command and commit the changes.

    ```bash
    ./gradlew spotlessApply
    ```

7. Add the project to the list of target projects with adequate configuration in [annotator-core/src/main/java/edu/ucr/cs/riple/core/Main.java](annotator-core/src/main/java/edu/ucr/cs/riple/core/Main.java#L136).  
For our example, after line 136 add the following:  

    ```java
    benchmarks.put("jcommander", new Benchmark("com.beust.jcommander", "jcommander", "compileJava", "test"));
    ```

8. Rebuild the annotator-core module to include the new project in the configuration. Run this command from the root of the repository:

    ```bash
    ./gradlew spotlessApply
    ./gradlew build -x test
    ```

9. First run NullAwayAnnotator on the project to add nullability annotations to the code, without running NullRepair. Then, commit these changes to the `nimak/auto-code-fix` branch. This way, the changes made by NullRepair are more clear and the project is in a clean state before running NullRepair.  

    ```bash
    java -jar annotator-core/build/libs/annotator-core-1.3.16-SNAPSHOT.jar jcommander --mode disabled
    ```

10. Finally, run NullRepair on the project:  

    ```bash
    java -jar annotator-core/build/libs/annotator-core-1.3.16-SNAPSHOT.jar jcommander --mode advanced
    ```

It is recommended to first run NullAwayAnnotator without NullRepair on the project and to commit (and push) any addeded annotations to the `nimak/auto-code-fix` branch before running NullRepair. This way, the changes made by NullRepair are more clear and the project is in a clean state before running NullRepair.

## 7. Customize NullRepair

TODO: Add instructions on changing LLM-model, agent cycles/attempts, etc.

## 8. Implementation

TODO: Give a quick overview.