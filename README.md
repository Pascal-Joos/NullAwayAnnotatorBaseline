# NullRepair

NullRepair is an LLM-based tool that automatically repairs nullability errors reported by [NullAway](https://github.com/uber/NullAway) based on safe usage regions. It is built on top of [NullAwayAnnotator](https://github.com/nimakarimipour/NullAwayAnnotator).

The GitHub repository of NullRepair is available at [https://github.com/Pascal-Joos/NullRepairBaseline](https://github.com/Pascal-Joos/NullRepairBaseline).

The pre-print is located at [LLM-Based_Repair_of_Static_Nullability_Errors.pdf](LLM-Based_Repair_of_Static_Nullability_Errors.pdf).

## 1. Setup NullRepair

### 1.1 Requirements

Technical requirements:

- Operating system: Linux version >= x; MacOS and Windows have not been tested.
- Installation of Docker. Has been tested on Linux with Docker 29.4.1.
- An OpenAI API key. This is needed to run NullRepair and the baselines, which use the OpenAI API. For a lightweight reproduction of the experiment results from the log files, the API key is not needed (see 3. and 4.).  

User requirements:

- Familiarity with Docker and Git.

### 1.2 Installation

Inside the docker container, run the following commands to set up the environment.

1. Activate the Python environment by running (if not yet active):  
```source .venv/bin/activate```

2. Configure the OpenAI API key by running the script `set_openai_key.py` and pasting the key when prompted. This will write the API key to the mini-SWE-agent configuration file and add it to a .env file.  
This is needed to run NullRepair and the baselines, which use the OpenAI API.  
For a lightweight reproduction of the experiment results from the log files, the API key is not needed (see 3. and 4.).  
```python3 set_openai_key.py```

## 2. Quick Run

A small example run where NullRepair is run on three nullability errors of project eureka can be executed with the following command:  
```java -jar annotator-core/build/libs/annotator-core-1.3.16-SNAPSHOT.jar eureka --mode advanced --selectedErrorIds 2,4,5```

Expected console output (truncated):  

```text
ANNOTATOR VERSION: 3, BUILD: 6
Received arguments: eureka, --mode, advanced, --selectedErrorIds, 2,4,5
Running eureka benchmark in advanced mode.
Resolve remaining errors mode: ADVANCED
Selected error IDs: [2, 4, 5]
Configuring logging for benchmark: eureka, branch: joos/advanced-3
Root path for logs: /home/vscode/NullRepairBaseline/evaluation_data/logs/eureka/advanced-3
Running on branch name: joos/advanced-3
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

Logs are then located at `evaluation_data/logs/eureka/advanced-3` and the changes made by NullRepair are committed to the branch `joos/advanced-3` in the target project repository at `benchmarks/eureka`.

## 3. Inspecting Logs and Data

Correspondence of approach names in the paper and the repository:
| Paper name | Repository name |
|---|---|
| NullRepair | advanced |
| SinglePrompt baseline | basic |
| mini-SWE-agent baseline | agent_baseline |

See `evaluation_data/logs` for the logs of executed runs and `benchmarks` for the target projects.  
The log files are organized by project and experiment mode. Each run creates a new log folder.  
For example, for the NullRepair per-patch run on eureka, refer to [evaluation_data/logs/eureka/advanced-evaluation-run-gpt5.1](evaluation_data/logs/eureka/advanced-evaluation-run-gpt5.1) for the logs of the run.  
The logs are structured as follows:

- `app.log` contains the complete execution log of the run.
- `log-<errorID>.log` contains the execution log for the specific errorID.
- `test-log-<errorID>.log` contains the log of the test execution after fixing the specific errorID.
- `metrics.tsv` contains the metrics on fix success for each error of the run.
- `token_usage.tsv` contains token usage information for each error of the run.
- `commits.tsv` contains the commit information for each error of the run, where a fix was created.
- `timers.tsv` logs the end-to-end time taken for the run.

For the created fixes, you can check the commit history of the respective run's branch (`joos/<log-folder-name>`) in the target project repository (e.g., for NullRepair per-patch on eureka it is the branch `joos/advanced-evaluation-run-gpt5.1` of `benchmarks/eureka`).  
Each fix made by NullRepair is committed separately with a commit message that includes the error ID and the error message and is then reverted in a subsequent commit.  

Aggregated stats on the runs, plots, and manual inspection results can be found in `evaluation_data/evaluation_results`, organized as follows:

- `per_patch/` — per-patch level results of the different approaches. Shows success rates, token usage, and timing per benchmark project and as total.
- `combined/` — combined level results of the different approaches. Shows success rates, token usage, and timing per benchmark project and as total.
- `manual_inspection/` — the 75-sample manual inspection dataset, per-reviewer initial scores, the consolidated scoring file (`manual_inspection_scoring_with_classification.tsv`), and derived statistics.
- `venn_diagrams/` — Venn diagrams showing overlap in resolved errors, resolved errors with no failing tests, and in manual inspection scores, across approaches.
- `stats_excluding_preliminary_study_projects/` — results with the three preliminary-study projects (conductor, litiengine, retrofit) excluded.

## 4. Reproduce Tables and Figures in the Paper

Pre-computed results are already present in `evaluation_data/evaluation_results/`. To recompute them from the log files, run the single wrapper script from the repository root:

```bash
python3 reproduce_results.py
```

Reproduced output files are written with a `_reproduced` suffix, so they sit alongside the originals without overwriting them.

This script runs the following steps in order:

1. **Evaluation statistics** (`evaluation_scripts/calculate_evaluation_stats.py`) — aggregates per-error metrics (total generated patches, total resolved errors, failing tests, token usage, cost) for all six experiment configurations (NullRepair / SinglePrompt / mini-SWE-agent × per-patch / combined). Outputs six TSV files to `evaluation_data/evaluation_results/per_patch/` and `evaluation_data/evaluation_results/combined/` with names such as `evaluation_stats_advanced_per_patch_reproduced.tsv`.

2. **Patch file-count statistics** (`evaluation_scripts/patch_file_count_stats.py`) — analyses how many Java files each generated patch touches, broken down by approach and outcome. Prints a summary table and writes `evaluation_data/evaluation_results/per_patch/patch_file_count_stats_reproduced.csv`.

3. **Manual inspection score analysis** (`evaluation_scripts/manual_inspection/analyze_manual_inspection_scores.py`) — reads the consolidated 75-sample manual inspection file and computes per-tool score distributions, win/loss/tie counts, and pairwise matchup tables. Outputs `evaluation_data/evaluation_results/manual_inspection/scoring_stats/manual_inspection_statistics_reproduced.tsv` and a `_reproduced_pairwise.tsv` companion.

4. **Inter-rater agreement** (`evaluation_scripts/manual_inspection/calculate_inter_rater_agreement.py`) — computes Cohen's Kappa across the three reviewer pairs over all scored patches and writes the full report to `evaluation_data/evaluation_results/manual_inspection/scoring_stats/agreement_analysis_reproduced.txt`.

Two additional figures require Jupyter:

- **Venn diagrams** — open and run `evaluation_scripts/create_venn_diagrams.ipynb`.
- **Manual inspection score plot** — open and run `evaluation_scripts/manual_inspection/manual_inspection_plot.ipynb`.

TODO: Test the figure plots

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

It is recommended to first run NullAwayAnnotator without NullRepair on the project and to commit (and push) any added annotations to the `nimak/auto-code-fix` branch before running NullRepair. This way, the changes made by NullRepair are more clear and the project is in a clean state before running NullRepair.

## 7. Customize NullRepair

Key parameters are set in source files and require rebuilding after a change (step 8 of section 6).

**LLM model** — edit `modelName` in `annotator-core/src/main/java/edu/ucr/cs/riple/core/Config.java` (line ~204):
```java
public String modelName = "openai/gpt-5.1";
```
Supported model strings and their pricing are listed in `ChatGPT.java`. The prefix `openai/` is stripped before the API call; any OpenAI-compatible model name can be used.

**Per-error cost budget** — edit `COST_LIMIT` in `annotator-core/src/main/java/edu/ucr/cs/riple/core/checkers/nullaway/codefix/ChatGPT.java` (line ~175):
```java
private static final double COST_LIMIT = 0.5;  // USD per error
```
NullRepair aborts LLM calls for an error once this limit is reached.

**Analysis depth** — controls how many levels of the call graph are explored when building context. Pass `--depth <n>` on the command line (default: 5):
```bash
java -jar annotator-core/build/libs/annotator-core-1.3.16-SNAPSHOT.jar eureka --mode advanced --depth 3
```

## 8. Implementation

NullRepair extends NullAwayAnnotator. The main entry point is `annotator-core/src/main/java/edu/ucr/cs/riple/core/Main.java`. The three repair modes are implemented in `annotator-core/src/main/java/edu/ucr/cs/riple/core/checkers/nullaway/codefix/`:

| Class | Mode |
| --- | --- |
| `AdvancedNullAwayCodeFix` | `advanced` (NullRepair) |
| `BasicNullAwayCodeFix` | `basic` (SinglePrompt baseline) |
| `AgentBaselineNullAwayCodeFix` | `agent_baseline` (mini-SWE-agent baseline) |

LLM communication is handled by `ChatGPT.java` in the same package. Configuration is managed by `Config.java`.
