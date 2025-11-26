package edu.ucr.cs.riple.core.checkers.nullaway.codefix;

public class ChatGPTTokenUsage {
  private long promptTokens;
  private long completionTokens;
  private long totalTokens;

  public ChatGPTTokenUsage(long promptTokens, long completionTokens) {
    this.promptTokens = promptTokens;
    this.completionTokens = completionTokens;
    this.totalTokens = promptTokens + completionTokens;
  }

  public void reset() {
    this.promptTokens = 0L;
    this.completionTokens = 0L;
    this.totalTokens = 0L;
  }

  public void add(ChatGPTTokenUsage other) {
    this.promptTokens += other.promptTokens;
    this.completionTokens += other.completionTokens;
    this.totalTokens += other.totalTokens;
  }

  public long getPromptTokens() {
    return promptTokens;
  }

  public long getCompletionTokens() {
    return completionTokens;
  }

  public long getTotalTokens() {
    return totalTokens;
  }

  public String toString() {
    return String.format(
        "Token usage - Prompt: %d, Completion: %d, Total: %d",
        promptTokens, completionTokens, totalTokens);
  }
}
