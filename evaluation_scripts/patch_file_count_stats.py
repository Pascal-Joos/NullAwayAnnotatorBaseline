"""
Analyse how many files each patch touches, split by approach and outcome.

Outcomes tracked:
  - all          : every patch for which a commit hash exists
  - resolved     : TARGET_ERROR_RESOLVED_WITHOUT_NEW_ERRORS == true
  - resolved_no_fail : resolved + FAILING_TESTS == false
"""

import argparse
import csv
import os
import subprocess
from collections import Counter, defaultdict

# ── Config ─────────────────────────────────────────────────────────────────
LOG_ROOT        = "/home/vscode/NullRepairBaseline/evaluation_data/logs"
BENCHMARK_ROOT  = "/home/vscode/NullRepairBaseline/benchmarks"

APPROACHES = {
    "advanced":       "advanced-evaluation-run-gpt5.1",
    "basic":          "basic-evaluation-run-gpt5.1",
    "agent_baseline": "agent_baseline-evaluation-run-gpt5.1",
}
APPROACH_LABELS = {
    "advanced":       "Advanced",
    "basic":          "Basic",
    "agent_baseline": "Agent Baseline (per-patch)",
}

BENCHMARKS = sorted(
    b for b in os.listdir(LOG_ROOT)
    if os.path.isdir(os.path.join(LOG_ROOT, b)) and b != "total"
)


# ── Helpers ────────────────────────────────────────────────────────────────
def load_metrics(path: str) -> dict:
    """Return dict: row_id -> {col: value, ...}"""
    result = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            result[row["ID"]] = row
    return result


def count_changed_files(repo_path: str, commit_hash: str) -> int | None:
    """Number of files touched by commit_hash in repo_path, or None on error."""
    if not commit_hash or commit_hash.strip() == "":
        return None
    try:
        out = subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", commit_hash.strip()],
            cwd=repo_path,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        files = [l for l in out.splitlines() if l.strip().endswith(".java")]
        return len(files) if files else None
    except subprocess.CalledProcessError:
        return None


# ── Main collection ────────────────────────────────────────────────────────
# Structure: stats[approach_key][outcome] = Counter({num_files: count})
stats: dict[str, dict[str, Counter]] = {
    key: {"all": Counter(), "resolved": Counter(), "resolved_no_fail": Counter()}
    for key in APPROACHES
}

missing_repo = set()

for benchmark in BENCHMARKS:
    repo_path = os.path.join(BENCHMARK_ROOT, benchmark)
    if not os.path.isdir(repo_path):
        missing_repo.add(benchmark)
        continue

    for key, subdir in APPROACHES.items():
        base = os.path.join(LOG_ROOT, benchmark, subdir)
        commits_path = os.path.join(base, "commits.tsv")
        metrics_path = os.path.join(base, "metrics.tsv")
        if not os.path.exists(commits_path) or not os.path.exists(metrics_path):
            continue

        metrics = load_metrics(metrics_path)

        with open(commits_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                row_id   = row["ID"]
                commit   = row.get("HASH", "").strip()
                n_files  = count_changed_files(repo_path, commit)
                if n_files is None:
                    continue

                m = metrics.get(row_id, {})
                resolved      = m.get("TARGET_ERROR_RESOLVED_WITHOUT_NEW_ERRORS", "false").lower() == "true"
                no_fail       = m.get("FAILING_TESTS", "false").lower() == "false"

                stats[key]["all"][n_files] += 1
                if resolved:
                    stats[key]["resolved"][n_files] += 1
                    if no_fail:
                        stats[key]["resolved_no_fail"][n_files] += 1

if missing_repo:
    print(f"Warning: repos not found in {BENCHMARK_ROOT}: {sorted(missing_repo)}\n")


# ── Pretty-print ───────────────────────────────────────────────────────────
OUTCOMES = [
    ("all",              "All patches"),
    ("resolved",         "Resolved without new errors"),
    ("resolved_no_fail", "Resolved without new errors & no test failures"),
]

MAX_SHOW = 10   # show individual counts up to this many files; bucket the rest

def format_table(counter: Counter, label: str) -> None:
    total = sum(counter.values())
    if total == 0:
        print(f"  {label}: (no data)")
        return
    multi = sum(v for k, v in counter.items() if k > 1)
    print(f"  {label} — total patches: {total}  |  multi-file: {multi} ({100*multi/total:.1f}%)")
    max_files = max(counter.keys(), default=0)
    for n in range(1, min(max_files, MAX_SHOW) + 1):
        c = counter[n]
        bar = "#" * c
        print(f"    {n:2d} file(s): {c:4d}  {bar}")
    if max_files > MAX_SHOW:
        bucket = sum(v for k, v in counter.items() if k > MAX_SHOW)
        print(f"    >{MAX_SHOW} file(s): {bucket:4d}")


print("=" * 70)
print("PATCH FILE-COUNT STATISTICS")
print("=" * 70)

for key, label in [
    ("advanced", APPROACH_LABELS["advanced"]),
    ("basic", APPROACH_LABELS["basic"]),
    ("agent_baseline", APPROACH_LABELS["agent_baseline"]),
]:
    print(f"\n{'─' * 70}")
    print(f"Approach: {label}")
    print(f"{'─' * 70}")
    for outcome_key, outcome_label in OUTCOMES:
        format_table(stats[key][outcome_key], outcome_label)


# ── CSV export ─────────────────────────────────────────────────────────────
_default_csv = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../evaluation_data/evaluation_results/per_patch/patch_file_count_stats.csv"
)
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument("--output", default=_default_csv)
out_csv = _parser.parse_known_args()[0].output

all_file_counts = sorted(
    set(
        k
        for key in APPROACHES
        for outcome_key, _ in OUTCOMES
        for k in stats[key][outcome_key]
    )
)

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    header = ["approach", "outcome", "n_files", "count"]
    writer.writerow(header)
    for key in APPROACHES:
        for outcome_key, _ in OUTCOMES:
            for n in all_file_counts:
                writer.writerow([APPROACH_LABELS[key], outcome_key, n, stats[key][outcome_key][n]])

print(f"\nCSV saved to: {out_csv}")
