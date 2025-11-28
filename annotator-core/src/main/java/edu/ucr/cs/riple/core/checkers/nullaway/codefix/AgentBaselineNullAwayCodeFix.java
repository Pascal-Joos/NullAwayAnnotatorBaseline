package edu.ucr.cs.riple.core.checkers.nullaway.codefix;

import edu.ucr.cs.riple.core.Context;
import edu.ucr.cs.riple.core.checkers.nullaway.NullAwayError;
import edu.ucr.cs.riple.core.util.Utility;
import edu.ucr.cs.riple.injector.changes.RegionRewrite;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AgentBaselineNullAwayCodeFix extends NullAwayCodeFix {

  /** Prompt for the Agent. */
  private static final String AGENT_FIX_REQUEST_PROMPT =
      Utility.readResourceContent("prompts/agent-fix-request.txt");

  private final Logger logger;

  private final Path benchmarkDirectoryPath;

  public AgentBaselineNullAwayCodeFix(Context context, Path benchmarkDirectoryPath) {
    super(context);
    this.logger = LoggerFactory.getLogger(AgentBaselineNullAwayCodeFix.class);
    this.benchmarkDirectoryPath = benchmarkDirectoryPath;
  }

  @Override
  public Set<RegionRewrite> fix(NullAwayError error, int errorId) {
    fixUsingAgent(error, context, errorId);
    return Set.of();
  }

  /**
   * Constructs the task and invokes the agent to get a code fix for the given error.
   *
   * @param error the error to fix.
   * @param context Annotator context.
   */
  public void fixUsingAgent(NullAwayError error, Context context, int errorId) {

    String region =
        "the "
            + (error.getRegion().isOnCallable() ? "method: " : "declaration of field: ")
            + "\""
            + error.getRegion().member
            + "\"";

    Map<String, Object> placeholderMappings = new HashMap<>();
    placeholderMappings.put("errorType", error.messageType);
    placeholderMappings.put("errorMessage", error.message);
    placeholderMappings.put("errorPath", error.path);
    placeholderMappings.put("lineNumber", error.position.lineNumber + 1);
    placeholderMappings.put("errorCodeLine", error.position.diagnosticLine);
    placeholderMappings.put("errorRegion", region);
    placeholderMappings.put("workingDir", context.config.benchmarkPath);
    placeholderMappings.put(
        "totalErrors",
        Utility.readErrorsFromOutputDirectory(
                context, context.targetModuleInfo, NullAwayError.class)
            .size());
    placeholderMappings.put("initialLogFilePath", context.config.initialErrorsLogPath);
    placeholderMappings.put("errorCountInFile", countErrorsInFile(error, context));
    placeholderMappings.put(
        "buildCommand",
        context.config.buildCommand.substring(context.config.buildCommand.indexOf("./gradlew")));
    placeholderMappings.put("fileName", error.path.getFileName());

    String prompt =
        StringSubstitutor.replace(AGENT_FIX_REQUEST_PROMPT, placeholderMappings, "%(", ")");

    // Invoke the mini-swe-agent Python script and pass the prompt via stdin.
    ProcessBuilder pb =
        new ProcessBuilder(
            "python3",
            "mini-swe-agent-for-nullaway-codefix/src/minisweagent/run/nullrepair_baseline.py",
            "-m",
            context.config.modelName,
            "-d",
            this.benchmarkDirectoryPath.toString(),
            "-t",
            prompt,
            "-y",
            "-l",
            Double.toString(context.config.agentCostLimit),
            "--exit-immediately",
            "-o",
            context
                .config
                .logPath
                .getParent()
                .resolve("agent-log-" + errorId + ".traj.json")
                .toString());
    logger.info("Invoking agent with command: {}", pb.command());

    Path projectRoot = Paths.get(System.getProperty("user.dir"));
    pb.directory(projectRoot.toFile());

    pb.redirectErrorStream(true);
    AtomicReference<Process> procRef = new AtomicReference<>();

    StringBuilder output = new StringBuilder();
    try {
      Process proc = pb.start();
      procRef.set(proc);

      // Read the agent's stdout
      Thread readerThread =
          new Thread(
              () -> {
                try (BufferedReader reader =
                    new BufferedReader(
                        new InputStreamReader(proc.getInputStream(), StandardCharsets.UTF_8))) {
                  String line;
                  while ((line = reader.readLine()) != null) {
                    System.out.println(line); // interactive logging
                    output.append(line).append("\n");
                  }
                } catch (IOException e) {
                  logger.error("Error reading agent output: {}", e.getMessage());
                }
              },
              "agent-output-reader");
      readerThread.setDaemon(true);
      readerThread.start();

      // Wait for process to finish with timeout
      boolean finished = proc.waitFor(60, TimeUnit.MINUTES);
      if (!finished) {
        proc.destroyForcibly();
        logger.error("Agent invocation timed out.");
      } else {
        int exit = proc.exitValue();
        if (exit != 0) {
          logger.error("Agent exited with code: {}", exit);
        }
      }

      // Ensure all output has been consumed
      try {
        readerThread.join(10_000);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
      }

      logger.info("Agent output:\n{}", output);

    } catch (IOException | InterruptedException e) {
      logger.info("Agent output:\n{}", output);
      logger.error("Failed to invoke mini-swe-agent: {}", e.getMessage());
      if (procRef.get() != null) {
        procRef.get().destroyForcibly();
      }
      Thread.currentThread().interrupt();
    }
  }

  private long countErrorsInFile(NullAwayError error, Context context) {
    return Utility.readErrorsFromOutputDirectory(
            context, context.targetModuleInfo, NullAwayError.class)
        .stream()
        .filter(e -> e.path.equals(error.path))
        .count();
  }
}
