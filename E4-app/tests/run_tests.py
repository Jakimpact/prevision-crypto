"""Simple test runner script for CI or local usage.

Usage: python run_tests.py
"""
from __future__ import annotations
import subprocess
import sys


def main() -> int:
    cmd = [sys.executable, '-m', 'pytest', '-q']
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
