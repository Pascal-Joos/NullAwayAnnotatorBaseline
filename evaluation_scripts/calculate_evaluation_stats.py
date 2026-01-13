import argparse
import csv
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class BenchmarkStats:
    project: str
    total_target_errors: int = 0
    generated_patches: int = 0
    error_introducing_patches: int = 0
    resolving_patches: int = 0
    resolving_patches_and_no_new_errors: int = 0
    trigger_new_error_patches: int = 0
    total_execution_time_sec: float = 0.0
    full_scaffold_execution_time_in_sec: float = 0.0
    total_agent_cycles: int = 0
    total_tokens: int = 0
    uncached_input_tokens: int = 0
    cached_input_tokens: int = 0
    completion_tokens: int = 0
    total_monetary_cost: float = 0.0

    def aggregate_from_patch(self, patch: Dict) -> None:
        self.total_target_errors += 1
        
        if patch.get("generated_patch"):
            self.generated_patches += 1

        if patch.get("introduces_error"):
            self.error_introducing_patches += 1

        if patch.get("resolves_error"):
            self.resolving_patches += 1

        if patch.get("resolves_error_and_no_new_errors"):
            self.resolving_patches_and_no_new_errors += 1

        if patch.get("triggers_new_error"):
            self.trigger_new_error_patches += 1


        self.total_execution_time_sec += float(patch.get("execution_time_sec", 0.0))
        self.total_agent_cycles += int(patch.get("agent_cycles", 0))
        self.total_tokens += int(patch.get("total_tokens", 0))
        self.uncached_input_tokens += int(patch.get("uncached_input_tokens", 0))
        self.cached_input_tokens += int(patch.get("cached_input_tokens", 0))
        self.completion_tokens += int(patch.get("completion_tokens", 0))
        self.total_monetary_cost += float(patch.get("monetary_cost", 0.0))

    def finalize(self, config_dir: str) -> Dict:
        data = asdict(self)

        if self.total_target_errors > 0:
            data["avg_execution_time_sec"] = self.total_execution_time_sec / self.total_target_errors
            data["avg_agent_cycles"] = self.total_agent_cycles / self.total_target_errors
            data["avg_tokens"] = self.total_tokens / self.total_target_errors
            data["avg_uncached_input_tokens"] = self.uncached_input_tokens / self.total_target_errors
            data["avg_cached_input_tokens"] = self.cached_input_tokens / self.total_target_errors
            data["avg_completion_tokens"] = self.completion_tokens / self.total_target_errors
            data["avg_monetary_cost"] = self.total_monetary_cost / self.total_target_errors
        else:
            data["avg_execution_time_sec"] = 0.0
            data["avg_agent_cycles"] = 0.0
            data["avg_tokens"] = 0.0
            data["avg_completion_tokens"] = 0.0
            data["avg_monetary_cost"] = 0.0

        return data

@dataclass
class BenchmarkStatsNonCombined(BenchmarkStats):
    failing_test_patches: int = 0
    resolving_patches_no_new_errors_no_failing_tests: int = 0
    percentage_resolving_patches_and_no_new_errors: float = 0.0
    percentage_failing_test_patches: float = 0.0

    def aggregate_from_patch(self, patch) -> None:
        super().aggregate_from_patch(patch)
        if patch.get("has_failing_tests"):
            self.failing_test_patches += 1

        if patch.get("resolves_error_and_no_new_errors") and not patch.get("has_failing_tests"):
            self.resolving_patches_no_new_errors_no_failing_tests += 1

    def finalize(self, config_dir: str) -> Dict:
        finalized_stats = super().finalize(config_dir)
        if self.total_target_errors > 0:
            finalized_stats["percentage_resolving_patches_and_no_new_errors"] = (self.resolving_patches_and_no_new_errors / self.total_target_errors) * 100.0
            finalized_stats["percentage_failing_test_patches"] = (self.failing_test_patches / self.total_target_errors) * 100.0
        else:
            finalized_stats["percentage_resolving_patches_and_no_new_errors"] = 0.0
            finalized_stats["percentage_failing_test_patches"] = 0.0

        return finalized_stats

@dataclass
class BenchmarkStatsCombined(BenchmarkStats):
    total_test_failures: int = -1
    remaining_errors: int = 1_000_000
    percentage_error_reduction: float = 0.0
    percentage_failed_tests_from_total_tests: float = 0.0

    def aggregate_from_patch(self, patch) -> None:
        super().aggregate_from_patch(patch)
        self.remaining_errors = min(self.remaining_errors, patch.get("remaining_errors", self.remaining_errors))

    def finalize(self, config_dir: str) -> Dict:
        finalized_stats = super().finalize(config_dir)
        remaining_errors_after_reverting_late_breaking_fixes = parse_remaining_errors_after_reverting_late_breaking_fixes_tsv(os.path.join(config_dir, "remaining_errors_after_reverting_late_breaking_fixes.tsv"))

        if remaining_errors_after_reverting_late_breaking_fixes != -1:
            finalized_stats["remaining_errors"] = remaining_errors_after_reverting_late_breaking_fixes

        if self.total_target_errors > 0:
            finalized_stats["percentage_error_reduction"] = ((self.total_target_errors - finalized_stats["remaining_errors"]) / self.total_target_errors) * 100.0
        else:
            finalized_stats["percentage_error_reduction"] = 0.0

        path_before_exp_folder = os.path.dirname(config_dir)
        total_tests = parse_total_tests_tsv(os.path.join(path_before_exp_folder, "total_tests.tsv"))
        if total_tests > 0:
            finalized_stats["percentage_failed_tests_from_total_tests"] = (self.total_test_failures / total_tests) * 100.0
        else:
            finalized_stats["percentage_failed_tests_from_total_tests"] = 0.0

        return finalized_stats
    
def parse_remaining_errors_after_reverting_late_breaking_fixes_tsv(path: str) -> int:
    
    if not os.path.exists(path):
        return -1

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                return int(row.get("REMAINING_ERRORS", -1))
            except (TypeError, ValueError):
                return -1

def parse_metrics_tsv(path: str) -> List[Dict]:
    patches: List[Dict] = []
    if not os.path.exists(path):
        return patches

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            patches.append(row)
    return patches


def parse_timers_tsv(path: str) -> float:
    if not os.path.exists(path):
        return 0.0

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                return float(row.get("TIME_IN_MILLIS", 0.0))
            except (TypeError, ValueError):
                return 0.0
            
def parse_total_test_failures_tsv(path: str) -> int:
    if not os.path.exists(path):
        return -1

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                return int(row.get("TOTAL_TEST_FAILURES", -1))
            except (TypeError, ValueError):
                return -1
            
def parse_total_tests_tsv(path: str) -> int:
    if not os.path.exists(path):
        return 0

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                return int(row.get("TOTAL_TESTS", 0))
            except (TypeError, ValueError):
                return 0

# Only applies to agent_baseline mode    
def parse_agent_logs_agent_baseline(log_dir: str) -> Dict[str, Dict]:
    agent_info: Dict[str, Dict] = {}

    if not os.path.isdir(log_dir):
        return agent_info

    for filename in os.listdir(log_dir):
        if not filename.startswith("agent-log-") or not filename.endswith(".traj.json"):
            continue
        patch_id_str = filename[len("agent-log-") : -len(".traj.json")]
        try:
            int(patch_id_str)
        except ValueError:
            continue

        path = os.path.join(log_dir, filename)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue

        info = data.get("info", {}).get("model_stats", {})
        messages = data.get("messages", [])
        agent_info.setdefault(patch_id_str, {})
        agent_info[patch_id_str]["agent_cycles"] = info.get("api_calls", 0)
        agent_info[patch_id_str]["total_tokens"] = info.get("total_tokens", 0)
        agent_info[patch_id_str]["uncached_input_tokens"] = retrieve_uncached_input_tokens(messages)
        agent_info[patch_id_str]["cached_input_tokens"] = retrieve_cached_input_tokens(messages)
        agent_info[patch_id_str]["completion_tokens"] = info.get("completion_tokens", 0)
        agent_info[patch_id_str]["monetary_cost"] = info.get("instance_cost", 0.0)

    return agent_info

def retrieve_uncached_input_tokens(messages: Dict) -> int:
    # Aggregate all "prompt_tokens" fields in messages dict.
    total_uncached = 0
    for message in messages:
        extra_info = message.get("extra", {})
        if not extra_info:
            continue
        response = extra_info.get("response", {})
        usage = response.get("usage", {})

        prompt_tokens = usage.get("prompt_tokens", 0)
        cached_tokens = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
        uncached_tokens = prompt_tokens - cached_tokens
        total_uncached += uncached_tokens

    return total_uncached

def retrieve_cached_input_tokens(messages: Dict) -> int:
    # Aggregate all "cached_tokens" fields in messages dict.
    total_cached = 0
    for message in messages:
        extra_info = message.get("extra", {})
        if not extra_info:
            continue
        response = extra_info.get("response", {})
        usage = response.get("usage", {})

        cached_tokens = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
        total_cached += cached_tokens

    return total_cached

# Only applies to non-agent_baseline modes
def parse_token_usage_log(path: str) -> Dict[str, Dict]:
    agent_info: Dict[str, Dict] = {}

    if not os.path.exists(path):
        return agent_info
    
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            agent_info.setdefault(row["ID"], {})
            agent_info[row["ID"]]["agent_cycles"] = int(row.get("PROMPTS_COUNT", 0))
            agent_info[row["ID"]]["total_tokens"] = int(row.get("TOTAL_TOKENS", 0))
            agent_info[row["ID"]]["uncached_input_tokens"] = int(row.get("UNCACHED_PROMPTS_TOKENS", 0))
            agent_info[row["ID"]]["cached_input_tokens"] = int(row.get("CACHED_PROMPTS_TOKENS", 0))
            agent_info[row["ID"]]["completion_tokens"] = int(row.get("RESPONSES_TOKENS", 0))
            agent_info[row["ID"]]["monetary_cost"] = float(row.get("COST_IN_DOLLARS", 0.0))

    return agent_info



def collect_stats_for_benchmark(log_root: str, benchmark: str, config_subdir: str, code_fix_mode: str, combined: bool) -> BenchmarkStats:
    benchmark_dir = os.path.join(log_root, benchmark)
    config_dir = os.path.join(benchmark_dir, config_subdir)

    if combined:
        stats = BenchmarkStatsCombined(project=benchmark)
    else:
        stats = BenchmarkStatsNonCombined(project=benchmark)

    metrics_path = os.path.join(config_dir, "metrics.tsv")
    timers_path = os.path.join(config_dir, "timers.tsv")

    metrics_rows = parse_metrics_tsv(metrics_path)
    full_scaffold_execution_time_in_millis = parse_timers_tsv(timers_path)
    stats.full_scaffold_execution_time_in_sec = full_scaffold_execution_time_in_millis / 1000.0

    if combined:
        total_test_failures = parse_total_test_failures_tsv(os.path.join(config_dir, "total-test-failures.tsv"))
        stats.total_test_failures = total_test_failures

    if code_fix_mode == "agent_baseline":
        agent_info = parse_agent_logs_agent_baseline(config_dir)
    else:
        token_usage_dir = os.path.join(config_dir, "token-usages.tsv")
        agent_info = parse_token_usage_log(token_usage_dir)

    for row in metrics_rows:
        patch_id = row.get("ID")
        agent_info_for_patch = agent_info.get(patch_id, {})

        patch_record: Dict = {}
        patch_record["generated_patch"] = row.get("PATCH_GENERATED", "false").lower() == "true"
        patch_record["introduces_error"] = row.get("COMPILATION_ERROR_INTRODUCED", "false").lower() == "true"
        patch_record["resolves_error"] = row.get("TARGET_ERROR_RESOLVED", "false").lower() == "true"
        patch_record["resolves_error_and_no_new_errors"] = (row.get("TARGET_ERROR_RESOLVED_WITHOUT_NEW_ERRORS", "false").lower() == "true")
        patch_record["triggers_new_error"] = row.get("TRIGGERED_NEW_ERRORS", "false").lower() == "true"
        
        patch_record["has_failing_tests"] = row.get("FAILING_TESTS", "false").lower() == "true"
        patch_record["remaining_errors"] = int(row.get("REMAINING_ERRORS", 1_000_000))

        patch_record["execution_time_sec"] = float(row.get("EXECUTION_TIME_IN_MILLIS")) / 1000.0 if row.get("EXECUTION_TIME_IN_MILLIS") is not None else 0.0
        
        patch_record["agent_cycles"] = agent_info_for_patch.get("agent_cycles", 0)
        patch_record["total_tokens"] = agent_info_for_patch.get("total_tokens", 0)
        patch_record["uncached_input_tokens"] = agent_info_for_patch.get("uncached_input_tokens", 0)
        patch_record["cached_input_tokens"] = agent_info_for_patch.get("cached_input_tokens", 0)
        patch_record["completion_tokens"] = agent_info_for_patch.get("completion_tokens", 0)
        patch_record["monetary_cost"] = agent_info_for_patch.get("monetary_cost", 0.0)

        stats.aggregate_from_patch(patch_record)

    return stats


def write_stats_tsv(output_path: str, stats_per_benchmark: List[BenchmarkStats], combined: bool, log_root: str, config_subdir: str) -> None:
    if not stats_per_benchmark:
        return

    rows = [s.finalize(os.path.join(log_root, s.project, config_subdir)) for s in stats_per_benchmark]

    # Aggregate totals for the 'total' row
    if combined:
        total_stats = BenchmarkStatsCombined(project="total")
    else:
        total_stats = BenchmarkStatsNonCombined(project="total")


    if combined:
        total_stats.remaining_errors = 0
        total_stats.total_test_failures = 0

    for s in stats_per_benchmark:
        # Aggregate all fields except project and averages
        total_stats.total_target_errors += s.total_target_errors
        total_stats.generated_patches += s.generated_patches
        total_stats.error_introducing_patches += s.error_introducing_patches
        total_stats.resolving_patches += s.resolving_patches
        total_stats.resolving_patches_and_no_new_errors += s.resolving_patches_and_no_new_errors
        total_stats.trigger_new_error_patches += s.trigger_new_error_patches

        if combined:
            
            total_stats.remaining_errors += s.remaining_errors
            total_stats.total_test_failures += s.total_test_failures
        else:
            total_stats.failing_test_patches += s.failing_test_patches
            total_stats.resolving_patches_no_new_errors_no_failing_tests += s.resolving_patches_no_new_errors_no_failing_tests

        total_stats.total_execution_time_sec += s.total_execution_time_sec
        total_stats.full_scaffold_execution_time_in_sec += s.full_scaffold_execution_time_in_sec
        total_stats.total_agent_cycles += s.total_agent_cycles
        total_stats.total_tokens += s.total_tokens
        total_stats.uncached_input_tokens += s.uncached_input_tokens
        total_stats.cached_input_tokens += s.cached_input_tokens
        total_stats.completion_tokens += s.completion_tokens
        total_stats.total_monetary_cost += s.total_monetary_cost

    total_row = total_stats.finalize(os.path.join(log_root, "total", config_subdir))

    if not combined:
        fieldnames = [
            "project",
            "total_target_errors",
            "generated_patches",
            "error_introducing_patches",
            "resolving_patches",
            "resolving_patches_and_no_new_errors",
            "percentage_resolving_patches_and_no_new_errors",
            "trigger_new_error_patches",
            "failing_test_patches",
            "resolving_patches_no_new_errors_no_failing_tests",
            "percentage_failing_test_patches",
            "total_execution_time_sec",
            "avg_execution_time_sec",
            "full_scaffold_execution_time_in_sec",
            "total_agent_cycles",
            "avg_agent_cycles",
            "total_tokens",
            "uncached_input_tokens",
            "cached_input_tokens",
            "completion_tokens",
            "avg_tokens",
            "avg_uncached_input_tokens",
            "avg_cached_input_tokens",
            "avg_completion_tokens",
            "total_monetary_cost",
            "avg_monetary_cost",
        ]
    else:
        fieldnames = [
            "project",
            "total_target_errors",
            "generated_patches",
            "error_introducing_patches",
            "resolving_patches",
            "resolving_patches_and_no_new_errors",
            "trigger_new_error_patches",
            "remaining_errors",
            "percentage_error_reduction",
            "total_test_failures",
            "percentage_failed_tests_from_total_tests",
            "total_execution_time_sec",
            "avg_execution_time_sec",
            "full_scaffold_execution_time_in_sec",
            "total_agent_cycles",
            "avg_agent_cycles",
            "total_tokens",
            "uncached_input_tokens",
            "cached_input_tokens",
            "completion_tokens",
            "avg_tokens",
            "avg_uncached_input_tokens",
            "avg_cached_input_tokens",
            "avg_completion_tokens",
            "total_monetary_cost",
            "avg_monetary_cost",
        ]


    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        writer.writerow(total_row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate evaluation statistics from experiment logs.")
    parser.add_argument(
        "--log-root",
        type=str,
        default="/home/vscode/Desktop/logs",
        help="Root directory containing benchmark subfolders (default: %(default)s)",
    )
    parser.add_argument(
        "--config-subdir",
        type=str,
        default="agentic-agent_baseline-2",
        help="Subdirectory name for the specific configuration to analyze (default: %(default)s)",
    )
    parser.add_argument(
        "--code-fix-mode",
        choices=["advanced", "basic", "agent_baseline"],
        default="agent_baseline",
        help="Code fix mode used in the experiment (default: %(default)s)",
    )
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Combined mode flag",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation_stats.tsv",
        help="Output TSV file path (default: %(default)s)",
    )

    args = parser.parse_args()

    benchmarks: List[str] = []
    if os.path.isdir(args.log_root):
        for name in os.listdir(args.log_root):
            path = os.path.join(args.log_root, name)
            if not os.path.isdir(path):
                continue
            if not os.path.exists(os.path.join(path, args.config_subdir)):
                continue
            benchmarks.append(name)

    stats_list: List[BenchmarkStats] = []
    for benchmark in sorted(benchmarks):
        stats = collect_stats_for_benchmark(args.log_root, benchmark, args.config_subdir, args.code_fix_mode, args.combined)
        stats_list.append(stats)

    write_stats_tsv(args.output, stats_list, args.combined, args.log_root, args.config_subdir)


if __name__ == "__main__":
    main()
