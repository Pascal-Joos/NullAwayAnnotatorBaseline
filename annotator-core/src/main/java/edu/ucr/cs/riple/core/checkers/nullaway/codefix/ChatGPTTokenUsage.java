package edu.ucr.cs.riple.core.checkers.nullaway.codefix;

public class ChatGPTTokenUsage {
  private long uncachedPromptTokens;
  private long cachedPromptTokens;
  private long completionTokens;
  private long totalTokens;

  public ChatGPTTokenUsage(
      long uncachedPromptTokens, long cachedPromptTokens, long completionTokens) {
    this.uncachedPromptTokens = uncachedPromptTokens;
    this.cachedPromptTokens = cachedPromptTokens;
    this.completionTokens = completionTokens;
    this.totalTokens = uncachedPromptTokens + cachedPromptTokens + completionTokens;
  }

  public void reset() {
    this.uncachedPromptTokens = 0L;
    this.cachedPromptTokens = 0L;
    this.completionTokens = 0L;
    this.totalTokens = 0L;
  }

  public void add(ChatGPTTokenUsage other) {
    this.uncachedPromptTokens += other.uncachedPromptTokens;
    this.cachedPromptTokens += other.cachedPromptTokens;
    this.completionTokens += other.completionTokens;
    this.totalTokens += other.totalTokens;
  }

  public long getUncachedPromptTokens() {
    return uncachedPromptTokens;
  }

  public long getCachedPromptTokens() {
    return cachedPromptTokens;
  }

  public long getCompletionTokens() {
    return completionTokens;
  }

  public long getTotalTokens() {
    return totalTokens;
  }

  public String toString() {
    return String.format(
        "Token usage - Uncached Prompt: %d, Cached Prompt: %d, Completion: %d, Total: %d",
        uncachedPromptTokens, cachedPromptTokens, completionTokens, totalTokens);
  }
}
