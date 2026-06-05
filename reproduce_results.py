#!/usr/bin/env python3
"""
Reproduce all evaluation statistics, tables, and figures from the paper.

Run from the repository root:
    python3 reproduce_results.py

Outputs are written to evaluation_data/evaluation_results/.
Jupyter notebooks (Venn diagrams, manual inspection plots) must be run manually.
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
EVAL_SCRIPTS = os.path.join(ROOT, "evaluation_scripts")
LOG_ROOT = os.path.join(ROOT, "evaluation_data", "logs")
RESULTS_ROOT = os.path.join(ROOT, "evaluation_data", "evaluation_results")

PER_PATCH_DIR = os.path.join(RESULTS_ROOT, "per_patch")
COMBINED_DIR = os.path.join(RESULTS_ROOT, "combined")
SCORING_STATS_DIR = os.path.join(RESULTS_ROOT, "manual_inspection", "scoring_stats")

RUNS = [
    # (mode, config_subdir, combined, output_filename)
    ("advanced",       "advanced-evaluation-run-gpt5.1",                False, "evaluation_stats_advanced_per_patch.tsv"),
    ("basic",          "basic-evaluation-run-gpt5.1",                   False, "evaluation_stats_basic_per_patch.tsv"),
    ("agent_baseline", "agent_baseline-evaluation-run-gpt5.1",          False, "evaluation_stats_agent_baseline_per_patch.tsv"),
    ("advanced",       "advanced-combined-evaluation-run-gpt5.1",       True,  "evaluation_stats_advanced_combined.tsv"),
    ("basic",          "basic-combined-evaluation-run-gpt5.1",          True,  "evaluation_stats_basic_combined.tsv"),
    ("agent_baseline", "agent_baseline-combined-evaluation-run-gpt5.1", True,  "evaluation_stats_agent_baseline_combined.tsv"),
]


def run(cmd, cwd=None):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT)
    if result.returncode != 0:
        print(f"  [WARNING] Command exited with code {result.returncode}")


def step(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def main():
    os.makedirs(PER_PATCH_DIR, exist_ok=True)
    os.makedirs(COMBINED_DIR, exist_ok=True)
    os.makedirs(SCORING_STATS_DIR, exist_ok=True)

    # ── 1. Per-patch and combined evaluation statistics ────────────────────
    step("1/4  Aggregating evaluation statistics (Table 1 / Table 2)")
    calc_script = os.path.join(EVAL_SCRIPTS, "calculate_evaluation_stats.py")
    for mode, subdir, combined, out_file in RUNS:
        out_dir = COMBINED_DIR if combined else PER_PATCH_DIR
        output_path = os.path.join(out_dir, out_file)
        cmd = [
            sys.executable, calc_script,
            "--log-root", LOG_ROOT,
            "--config-subdir", subdir,
            "--code-fix-mode", mode,
            "--output", output_path,
        ]
        if combined:
            cmd.append("--combined")
        print(f"\n  Mode={mode}, combined={combined}")
        run(cmd)

    # ── 2. Patch file-count statistics ─────────────────────────────────────
    step("2/4  Computing patch file-count statistics")
    patch_script = os.path.join(EVAL_SCRIPTS, "patch_file_count_stats.py")
    run([sys.executable, patch_script])

    # ── 3. Manual inspection score analysis ───────────────────────────────
    step("3/4  Analyzing manual inspection scores")
    consolidated_file = os.path.join(
        RESULTS_ROOT, "manual_inspection",
        "manual_inspection_scoring_with_classification.tsv"
    )
    stats_output = os.path.join(SCORING_STATS_DIR, "manual_inspection_statistics.tsv")
    analyze_script = os.path.join(EVAL_SCRIPTS, "manual_inspection", "analyze_manual_inspection_scores.py")
    run([sys.executable, analyze_script, consolidated_file, stats_output])

    # ── 4. Inter-rater agreement ───────────────────────────────────────────
    step("4/4  Calculating inter-rater agreement (Cohen's Kappa)")
    kappa_script = os.path.join(EVAL_SCRIPTS, "manual_inspection", "calculate_inter_rater_agreement.py")
    run([sys.executable, kappa_script], cwd=ROOT)

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("  Done. Outputs written to evaluation_data/evaluation_results/")
    print()
    print("  Remaining steps requiring Jupyter:")
    print("    - Venn diagrams:          evaluation_scripts/create_venn_diagrams.ipynb")
    print("    - Manual inspection plot: evaluation_scripts/manual_inspection/manual_inspection_plot.ipynb")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
