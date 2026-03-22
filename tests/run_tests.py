#!/usr/bin/env python3
"""Test runner script for d4-diag test suite."""

import sys
from pathlib import Path


def main():
    """Run the test suite using pytest."""
    project_root = Path(__file__).parent.parent

    print("🧪 Running d4-diag Test Suite")
    print("=" * 50)

    # Run pytest with the tests directory
    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"], cwd=project_root, check=False
        )

        if result.returncode == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {result.returncode})")

        return result.returncode

    except Exception as e:
        print(f"💥 Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
