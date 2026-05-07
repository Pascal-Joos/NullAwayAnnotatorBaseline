/*
 * MIT License
 *
 * Copyright (c) 2020 Nima Karimipour
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

package edu.ucr.cs.riple.core;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.classic.encoder.PatternLayoutEncoder;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.FileAppender;
import com.google.common.io.MoreFiles;
import com.google.common.io.RecursiveDeleteOption;
import edu.ucr.cs.riple.core.util.GitUtility;
import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.slf4j.LoggerFactory;

/** Starting point. */
public class Main {

  public static final int VERSION = 3;

  public static final int BUILD_VERSION = 6;

  public static final Path ROOT_PATH = Paths.get("/home/vscode/NullRepairBaseline");

  public static class Benchmark {
    public final String annotatedPackage;
    public final String path;
    public final String buildCommand;
    public final String testCommand;

    public Benchmark(
        String annotatedPackage, String path, String buildCommand, String testCommand) {
      this.annotatedPackage = annotatedPackage;
      this.path = path;
      this.buildCommand = buildCommand;
      this.testCommand = testCommand;
    }

    @Override
    public boolean equals(Object o) {
      if (!(o instanceof Benchmark)) {
        return false;
      }
      Benchmark benchmark = (Benchmark) o;
      return Objects.equals(annotatedPackage, benchmark.annotatedPackage)
          && Objects.equals(path, benchmark.path)
          && Objects.equals(buildCommand, benchmark.buildCommand)
          && Objects.equals(testCommand, benchmark.testCommand);
    }

    @Override
    public int hashCode() {
      return Objects.hash(annotatedPackage, path, buildCommand, testCommand);
    }
  }

  // Benchmarks
  static final Map<String, Benchmark> benchmarks;

  static {
    benchmarks = new HashMap<>();
    benchmarks.put(
        "libgdx", new Benchmark("com.badlogic.gdx", "libgdx", "gdx:compileJava", "gdx:test"));
    benchmarks.put("zuul", new Benchmark("com.netflix", "zuul", "zuul-core:compileJava", "test"));
    benchmarks.put(
        "eureka",
        new Benchmark(
            "com.netflix.eureka", "eureka", "eureka-core:compileJava", "eureka-core:test"));
    benchmarks.put(
        "conductor",
        new Benchmark(
            "com.netflix.conductor",
            "conductor",
            "conductor-core:compileJava",
            "conductor-core:test"));
    benchmarks.put(
        "EventBus", new Benchmark("org.greenrobot.eventbus", "EventBus", "compileJava", "test"));
    // The glide test library:test only runs tests relevant to the library module. Other tests in
    // the project are not run by the test command.
    benchmarks.put(
        "glide",
        new Benchmark(
            "com.bumptech.glide", "glide", "library:compileDebugJavaWithJavac", "library:test"));
    benchmarks.put("jadx", new Benchmark("jadx.core", "jadx", "jadx-core:compileJava", "test"));
    benchmarks.put(
        "litiengine",
        new Benchmark("de.gurkenlabs.litiengine", "litiengine", "compileJava", "test"));
    benchmarks.put("retrofit", new Benchmark("retrofit2", "retrofit", "compileJava", "test"));
    benchmarks.put(
        "spring-boot",
        new Benchmark(
            "org.springframework.boot",
            "spring-boot",
            ":spring-boot-project:spring-boot:compileJava",
            ":spring-boot-project:spring-boot:test"));
    benchmarks.put("wala-util", new Benchmark("com.ibm.wala", "wala-util", "compileJava", "test"));
    benchmarks.put("gson", new Benchmark("com.google.gson", "gson", ":gson:compileJava", "test"));
    benchmarks.put("mockito", new Benchmark("org.mockito", "mockito", "compileJava", "test"));
  }

  // PROJECT SPECIFIC CONFIGURATION
  // Ubuntu
  public static final boolean DEBUG_MODE = false;
  public static final String DEBUG_LINE =
      "this.ownerType = ownerType == null ? null : canonicalize(ownerType);";

  public static void main(String[] args) {
    System.out.println("ANNOTATOR VERSION: " + VERSION + ", BUILD: " + BUILD_VERSION);
    System.out.println("Received arguments: " + String.join(", ", args));

    Options options = createOptions();
    CommandLineParser parser = new DefaultParser();
    CommandLine cmd;

    try {
      cmd = parser.parse(options, args);
    } catch (ParseException e) {
      System.err.println("Error parsing command line arguments: " + e.getMessage());
      printHelp(options);
      System.exit(1);
      return;
    }

    // Extract positional argument (benchmark name)
    String[] remainingArgs = cmd.getArgs();
    if (remainingArgs.length == 0) {
      System.err.println("Error: Benchmark name is required as the first argument");
      printHelp(options);
      System.exit(1);
      return;
    }
    String benchmarkName = remainingArgs[0];

    // Parse mode option
    String mode = cmd.getOptionValue("mode", "advanced");
    if (!Arrays.asList("basic", "agent_baseline", "disabled", "advanced").contains(mode)) {
      System.err.println(
          "Error: Invalid mode. Allowed values are: basic, agent_baseline, disabled, advanced");
      printHelp(options);
      System.exit(1);
      return;
    }

    // Parse boolean flags
    boolean verbose = cmd.hasOption("verbose");
    boolean combined = cmd.hasOption("combined");
    boolean pushCommits = cmd.hasOption("pushCommits");
    boolean continueRun = cmd.hasOption("continueRunAtError");
    int continueRunAtError = -1;
    if (continueRun) {
      try {
        continueRunAtError = Integer.parseInt(cmd.getOptionValue("continueRunAtError"));
      } catch (NumberFormatException e) {
        System.err.println("Error: continueRunAtError value must be an integer");
        System.exit(1);
        return;
      }
    }

    boolean selectedErrorIdsProvided = cmd.hasOption("selectedErrorIds");
    if (selectedErrorIdsProvided && continueRun) {
      System.err.println("Error: --selectedErrorIds cannot be combined with --continueRunAtError");
      printHelp(options);
      System.exit(1);
      return;
    }

    System.clearProperty("ANNOTATOR_TEST_MODE");

    System.out.println(
        "Running "
            + benchmarkName
            + " benchmark in "
            + mode
            + " mode."
            + (combined ? " Combined mode is ON." : ""));
    Benchmark benchmark = benchmarks.get(benchmarkName);
    if (benchmark == null) {
      System.err.println("Error: Unknown benchmark: " + benchmarkName);
      printHelp(options);
      System.exit(1);
      return;
    }
    Path PROJECT_PATH = ROOT_PATH.resolve("benchmarks").resolve(benchmark.path);
    deleteOutDir(benchmark);

    String fullTestCommand =
        String.format(
            "export JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-amd64 && cd %s && ANDROID_HOME=/usr/lib/android-sdk ./gradlew %s -Derrorprone.disable=true",
            PROJECT_PATH, benchmark.testCommand);

    // Special handling for benchmarks that require a screen (e.g., litiengine, jadx)
    if (benchmarkName.equals("litiengine") || benchmarkName.equals("jadx")) {
      fullTestCommand =
          String.format(
              "export JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-amd64 && cd %s && ANDROID_HOME=/usr/lib/android-sdk xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' ./gradlew %s -Derrorprone.disable=true",
              PROJECT_PATH, benchmark.testCommand);
    }

    String[] argsArray = {
      "-d",
      String.format("%s/annotator-out", PROJECT_PATH),
      "-bc",
      String.format(
          "export JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-amd64 && cd %s && ANDROID_HOME=/usr/lib/android-sdk ./gradlew %s",
          PROJECT_PATH, benchmark.buildCommand),
      "-tc",
      fullTestCommand,
      "-cp",
      String.format("%s/paths.tsv", PROJECT_PATH),
      "-i",
      "com.uber.nullaway.annotations.Initializer",
      "-n",
      "javax.annotation.Nullable",
      "-cn",
      "NULLAWAY",
      "-app",
      benchmark.annotatedPackage,
      mode.equals("disabled") ? "" : "-di", // deactivate inference
      "-rrem", // resolve remaining errors
      mode,
      // "-rboserr", // redirect build output stream and error stream
      verbose ? "-rboserr" : "",
      "--depth",
      "6",
      pushCommits ? "--pushCommits" : "",
      continueRun ? "--continueRunAtError" : "",
      continueRun ? String.valueOf(continueRunAtError) : "",
      selectedErrorIdsProvided ? "--selectedErrorIds" : "",
      selectedErrorIdsProvided ? cmd.getOptionValue("selectedErrorIds") : ""
    };

    Config config = new Config(argsArray);
    config.benchmarkName = benchmarkName;
    config.benchmarkPath = PROJECT_PATH;
    config.initialErrorsLogPath = PROJECT_PATH.resolve("initial_build_output.log");
    config.combined = combined;
    configureLogging(config);

    System.out.println("Running on branch name: " + config.branchName());
    System.out.println("Starting annotator...");
    // reset git repo
    try (GitUtility git = GitUtility.instance(config)) {
      git.resetHard();
      if (!config.continueRun) {
        git.safePull();
        git.checkoutBranch("nimak/auto-code-fix");
        git.resetHard();
        git.pull();
        git.deleteLocalBranch(config.branchName());
        if (pushCommits) {
          git.deleteRemoteBranch(config.branchName());
        }
        git.createAndCheckoutBranch(config.branchName());
        if (pushCommits) {
          git.pushBranch(config.branchName());
        }
      } else {
        git.checkoutBranch(config.branchName());
        git.resetHard();
      }
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
    // Start annotator
    Annotator annotator = new Annotator(config);
    annotator.start();

    // push
    try (GitUtility git = GitUtility.instance(config)) {
      System.out.printf("Commiting changes to branch %s...%n", config.branchName());
      git.stageAllChanges();
      git.commitChanges("Done");
      if (pushCommits) {
        System.out.printf("Pushing changes to branch %s...%n", config.branchName());
        git.pushChanges();
      }
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public static void deleteOutDir(Benchmark benchmark) {
    Path PROJECT_PATH = ROOT_PATH.resolve("benchmarks").resolve(benchmark.path);
    // delete dir
    Path outDir = PROJECT_PATH.resolve("annotator-out").resolve("0");
    if (outDir.toFile().exists()) {
      try {
        Files.walkFileTree(
            outDir,
            new SimpleFileVisitor<>() {
              @Override
              public FileVisitResult visitFile(Path file, BasicFileAttributes attrs)
                  throws IOException {
                Files.delete(file);
                return FileVisitResult.CONTINUE;
              }

              @Override
              public FileVisitResult postVisitDirectory(Path dir, IOException exc)
                  throws IOException {
                Files.delete(dir);
                return FileVisitResult.CONTINUE;
              }
            });
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    }
  }

  public static Path configureLogging(Config config) {
    System.out.println(
        "Configuring logging for benchmark: "
            + config.benchmarkName
            + ", branch: "
            + config.branchName());
    Path log_root =
        Paths.get(
            ROOT_PATH.toString(),
            "evaluation_data",
            "logs",
            config.benchmarkName,
            config.branchName().split("/")[1]
                + (config.continueRun ? "_continueAtError_" + config.continueRunAtError : ""));
    System.out.println("Root path for logs: " + log_root);
    // Delete log
    try {
      if (Files.exists(log_root)) {
        MoreFiles.deleteRecursively(log_root, RecursiveDeleteOption.ALLOW_INSECURE);
      }
      Files.createDirectories(log_root);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    String filePath = log_root.resolve("app.log").toString();

    LoggerContext context = (LoggerContext) LoggerFactory.getILoggerFactory();
    context.reset();

    PatternLayoutEncoder encoder = new PatternLayoutEncoder();
    encoder.setContext(context);
    encoder.setPattern("%d{HH:mm:ss.SSS} %-5level %class.%method%n%msg%n");
    encoder.start();

    FileAppender<ILoggingEvent> fileAppender = new FileAppender<>();
    fileAppender.setContext(context);
    fileAppender.setFile(filePath);
    fileAppender.setEncoder(encoder);
    fileAppender.start();

    Logger rootLogger = context.getLogger(Logger.ROOT_LOGGER_NAME);
    rootLogger.detachAndStopAllAppenders();
    rootLogger.addAppender(fileAppender);
    rootLogger.setLevel(Level.WARN); // Suppress most external INFO logs

    Logger myLogger = context.getLogger("edu.ucr.cs.riple"); // or your base package
    myLogger.setLevel(Level.TRACE); // See your trace/debug logs

    Thread.setDefaultUncaughtExceptionHandler(
        (thread, throwable) -> {
          rootLogger.error("Uncaught exception in thread: {}", thread.getName(), throwable);
        });
    config.logPath = log_root.resolve("app.log");
    config.metricsPath = log_root.resolve("metrics.tsv");
    config.commitHashPath = log_root.resolve("commits.tsv");
    config.timerPath = log_root.resolve("timers.tsv");
    config.combinedTestFailuresPath = log_root.resolve("total-test-failures.tsv");
    // or WARN if too noisy
    return log_root;
  }

  private static Options createOptions() {
    Options options = new Options();

    // Mode option
    options.addOption(
        Option.builder()
            .longOpt("mode")
            .option("m")
            .hasArg()
            .argName("mode")
            .desc("Execution mode: basic, agent_baseline, disable, or advanced (default: advanced)")
            .build());

    // Verbose flag
    options.addOption(
        Option.builder().longOpt("verbose").option("v").desc("Enable verbose output").build());

    // Combined mode flag
    options.addOption(
        Option.builder().longOpt("combined").option("c").desc("Enable combined mode").build());

    // Continue run at error option
    options.addOption(
        Option.builder()
            .longOpt("continueRunAtError")
            .option("r")
            .hasArg()
            .argName("iteration")
            .desc("Continue execution at specified error iteration")
            .build());

    // Push created commits to the target benchmark repositories
    options.addOption(
        Option.builder()
            .longOpt("pushCommits")
            .option("p")
            .desc(
                "Push created commits to the target benchmark repositories. Deactivated by default. Requires write access to the repos.")
            .build());

    // If only to be run on selected error IDs (e.g., for a quick run on a subset of errors)
    options.addOption(
        Option.builder()
            .longOpt("selectedErrorIds")
            .option("s")
            .hasArg()
            .argName("ids")
            .type(ArrayList.class)
            .desc(
                "Comma-separated list of error IDs to run on (e.g., 1,2,3). This must not be combined with --continueRunAtError.")
            .build());

    return options;
  }

  private static void printHelp(Options options) {
    HelpFormatter formatter = new HelpFormatter();
    formatter.printHelp(
        "java -cp <classpath> edu.ucr.cs.riple.core.Main <benchmark> [options]",
        "Options:",
        options,
        "\nExample:\n"
            + "  java -cp <classpath> edu.ucr.cs.riple.core.Main libgdx --mode basic --verbose\n"
            + "  java -cp <classpath> edu.ucr.cs.riple.core.Main zuul --continueRunAtError 5");
  }
}
