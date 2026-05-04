# NullRepair

## 1. Setup NullRepair

### 1.1 Requirements

The VS Code Dev Container extension with VS Code.  
Tested with Docker 29.4.1

### 1.2 Installation using VS Code Dev Container

Don't open the VS Code Dev Container before completing the steps 1 to 3.

1. Clone this repository using ssh and checkout the branch `joos/auto-code-fix-baseline`.

2. Run: ```git submodule update --init --recursive``` to initialize the mini-swe-agent submodule.

3. Run: `bash checkout_logs_and_benchmarks.sh`.  
This clones the nullrepair_log_files repository into `../nullrepair_log_files` and the target projects for the experiment into `../nullness-benchmarks` (i.e., at the same level as the nullrepair repository).  
Refer to these folders for the logs of executed runs and for any commits created by NullRepair.

4. Reopen the project in a devcontainer using the VSCode Dev Container extension. All needed dependencies and setup steps are then executed automatically. Wait until the postcreatecommand finishes executing and the terminal is ready to use.

5. Activate the Python environment by running (if not yet active):  
```source .venv/bin/activate```

6. Configure the OpenAI API key by running the script `set_openai_key.py` and pasting the key when prompted. This will write the API key to the mini-SWE-agent configuration file and add it to a .env file.

## 2. Quick Run



## 3. Inspecting Logs and Data

See `../nullrepair_log_files/logs` for the logs of executed runs and `../nullness-benchmarks` for the target projects.  
The log files are organized by project and experiment mode. Each run creates a new log folder.

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
The logs of each run are stored in a new folder in `../nullrepair_log_files/logs` with the name of the project and experiment mode.

## 6. Run on Your Own Project

You can run NullRepair on new Java projects.  
The following instructions assume that the target project uses Gradle.  
The setup of a new project is illustrated with the example project https://github.com/cbeust/jcommander/tree/3-lts with Java 17.  

1. Create a fork of the project if you do not have write access.  
We have created a fork for the example project here: https://github.com/Pascal-Joos/jcommander.

2. Clone the target project to the benchmarks directory and checkout the branch you want to run on.  

    ```bash
    cd ../nullness-benchmarks
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