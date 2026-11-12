#!/usr/bin/env python3
import glob
import json
import os
import sys


def run_checks():
    qc_files = glob.glob("work/*/*/*_qc.json")
    if not qc_files:
        print("[FAIL] No QC JSON files found in work directory.")
        sys.exit(1)

    rejected_count = 0
    for f in qc_files:
        with open(f) as fp:
            data = json.load(fp)
            if data.get("status") == "REJECTED_HEMOLYSIS":
                rejected_count += 1

    assert rejected_count >= 1, "[FAIL] Hemolysis rejection logic failed to trigger!"

    metric_files = glob.glob("work/*/*/*_metrics.json")
    if not metric_files:
        print("[FAIL] No metrics JSON files found.")
        sys.exit(1)

    for f in metric_files:
        with open(f) as fp:
            data = json.load(fp)
            acc = data.get("accuracy", 0.0)
            assert acc >= 0.75, (
                f"[FAIL] Model accuracy degraded below clinical threshold: {acc}"
            )

    assert os.path.exists("results/clinical_summary_report.pdf"), (
        "[FAIL] Final PDF report was not published!"
    )

    print("[SUCCESS] All clinical and mathematical invariants passed.")


if __name__ == "__main__":
    run_checks()
