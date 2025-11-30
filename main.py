#!/usr/bin/env python3
"""
Legacy entry point - redirects to the new CLI.
This file is kept for backward compatibility.

Use: toki --help
Or: python -m photolibnamer.main --help
"""

import sys

print("=" * 60)
print("NOTICE: This script has been replaced by the new CLI tool.")
print("=" * 60)
print("\nPlease use one of the following commands instead:\n")
print("  toki --help")
print("  python -m photolibnamer.main --help")
print("\nNew features:")
print("  - 'toki rename' - Rename files with metadata")
print("  - 'toki organize' - Organize into YYYY/MM/DD structure")
print("\nFor more information, see README.md")
print("=" * 60)

sys.exit(1)