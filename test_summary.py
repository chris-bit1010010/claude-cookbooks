#!/usr/bin/env python3
"""Generate test summary report for notebook tests."""

import subprocess
import sys
from collections import defaultdict


def run_tests_and_parse():
    """Run pytest and parse the output."""
    cmd = [
        "uv",
        "run",
        "pytest",
        "tests/notebook_tests/test_notebooks.py",
        "-v",
        "--tb=no",
        "-m",
        "not slow",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    failures_by_type = defaultdict(list)
    failures_by_notebook = defaultdict(list)

    for line in result.stdout.split("\n"):
        if "FAILED" in line:
            # Parse: tests/...::TestClass::test_name[notebook.ipynb] FAILED
            if "::" in line and "[" in line:
                parts = line.split("::")
                if len(parts) >= 3:
                    test_class = parts[1]
                    rest = parts[2]
                    test_name = rest.split("[")[0]
                    notebook = rest.split("[")[1].split("]")[0]

                    test_type = f"{test_class}::{test_name}"
                    failures_by_type[test_type].append(notebook)
                    failures_by_notebook[notebook].append(test_type)

    return failures_by_type, failures_by_notebook, result.stdout


def main():
    print("🔍 Analyzing notebook test results...\n")

    failures_by_type, failures_by_notebook, full_output = run_tests_and_parse()

    # Summary statistics
    total_notebooks_with_failures = len(failures_by_notebook)
    total_failure_instances = sum(len(v) for v in failures_by_type.values())

    print("=" * 80)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 80)
    print(f"\n📝 Total notebooks with failures: {total_notebooks_with_failures}")
    print(f"❌ Total test failures: {total_failure_instances}\n")

    # Failures by type
    print("=" * 80)
    print("🔎 FAILURES BY TEST TYPE")
    print("=" * 80)

    for test_type, notebooks in sorted(
        failures_by_type.items(), key=lambda x: len(x[1]), reverse=True
    ):
        print(f"\n{test_type}")
        print(f"  Affected notebooks: {len(notebooks)}")
        if len(notebooks) <= 5:
            for nb in notebooks:
                print(f"    - {nb}")
        else:
            print(f"    (showing first 5 of {len(notebooks)})")
            for nb in notebooks[:5]:
                print(f"    - {nb}")

    # Most problematic notebooks
    print("\n" + "=" * 80)
    print("⚠️  TOP 10 MOST PROBLEMATIC NOTEBOOKS")
    print("=" * 80)

    sorted_notebooks = sorted(
        failures_by_notebook.items(), key=lambda x: len(x[1]), reverse=True
    )

    for notebook, failures in sorted_notebooks[:10]:
        print(f"\n📓 {notebook}")
        print(f"   Failures: {len(failures)}")
        for failure in failures:
            test_name = failure.split("::")[-1]
            print(f"     - {test_name}")

    # Extract summary line
    summary_line = [line for line in full_output.split("\n") if "failed" in line and "passed" in line]
    if summary_line:
        print("\n" + "=" * 80)
        print("OVERALL RESULTS")
        print("=" * 80)
        print(summary_line[-1])

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
