#!/usr/bin/env python3
"""
Check for hardcoded secrets in all markdown files.
"""
import re
import sys
import os
import glob

def check_secrets():
    issues = []
    patterns = [
        (r'password["\']?\s*[:=]\s*["\'][^$\{]["\']', "Hardcoded password detected"),
        (r'adminPass["\']?\s*[:=]\s*["\'][^$\{]["\']', "Hardcoded adminPass detected"),
        (r'AK["\']?\s*[:=]\s*["\'][^$\{]["\']', "Hardcoded AK detected"),
        (r'SK["\']?\s*[:=]\s*["\'][^$\{]["\']', "Hardcoded SK detected"),
        (r'ghp_[A-Za-z0-9]{36}', "GitHub token detected"),
        (r'X-Auth-Token:\s*[A-Za-z0-9]{20,}', "Hardcoded auth token detected"),
    ]

    all_files = glob.glob("modules/*.md") + glob.glob("*.md") + glob.glob("references/*.md")

    for filepath in all_files:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                for pattern, msg in patterns:
                    if re.search(pattern, line):
                        # Skip if it's a placeholder like {PASSWORD} or ${PASSWORD}
                        if '{' in line or '$' in line:
                            continue
                        issues.append(f"  {filepath}:{line_num}: {msg}")

    if issues:
        print(f"FAILED: {len(issues)} potential secret(s) found:")
        for issue in issues:
            print(issue)
        sys.exit(1)
    else:
        print("PASSED: No hardcoded secrets detected.")
        sys.exit(0)

if __name__ == "__main__":
    check_secrets()
