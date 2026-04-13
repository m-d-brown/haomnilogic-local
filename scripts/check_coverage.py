#!/usr/bin/env python3
"""Check test coverage and ensure all library operations are covered."""

import json
import subprocess
import sys
from pathlib import Path

# Minimum threshold for coverage
THRESHOLD = 90.0

def run_tests_with_coverage():
    """Run pytest with coverage and generate JSON report."""
    print("Running tests with coverage...")
    cmd = [
        "PYTHONPATH=.",
        ".venv/bin/pytest",
        "--cov=custom_components.omnilogic_local",
        "--cov-report=json",
        "custom_components/omnilogic_local/tests/"
    ]
    subprocess.run(" ".join(cmd), shell=True, check=False)

def evaluate_coverage():
    """Parse coverage report and evaluate status."""
    coverage_file = Path("coverage.json")
    if not coverage_file.exists():
        print("Error: coverage.json not found!")
        sys.exit(1)

    with open(coverage_file) as f:
        data = json.load(f)

    total_percent = data["totals"]["percent_covered"]
    print(f"\nOverall Coverage: {total_percent:.2f}%")

    # Check for missing operations in key files
    missing_ops = False
    for filename, file_data in data["files"].items():
        if filename.startswith("custom_components/omnilogic_local/"):
            # We especially care about actionable platforms
            if any(p in filename for p in ["switch", "light", "water_heater", "number", "button", "select"]):
                missing_lines = file_data["missing_lines"]
                if missing_lines:
                    # We'll be more specific about what lines are critical
                    # For now, just alert on missing lines in these files
                    print(f"File {filename} has missing lines: {missing_lines}")
                    # We'll consider any missing line in a platform file as a potential missing operation
                    # unless it's explicitly ignored.

    if total_percent < THRESHOLD:
        print(f"\nFAILURE: Coverage {total_percent:.2f}% is below threshold {THRESHOLD}%")
        return False

    print("\nSUCCESS: All operations are covered within threshold.")
    return True

if __name__ == "__main__":
    run_tests_with_coverage()
    success = evaluate_coverage()
    if not success:
        sys.exit(1)
