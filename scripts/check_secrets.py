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
        (r'password["\']?\s*[:=]\s*["\']([^"\'\n]{2,})["\']', "Hardcoded password detected"),
        (r'adminPass["\']?\s*[:=]\s*["\']([^"\'\n]{2,})["\']', "Hardcoded adminPass detected"),
        (r'AK["\']?\s*[:=]\s*["\']([^"\'\n]{2,})["\']', "Hardcoded AK detected"),
        (r'SK["\']?\s*[:=]\s*["\']([^"\'\n]{2,})["\']', "Hardcoded SK detected"),
        (r'ghp_[A-Za-z0-9]{36}', "GitHub token detected"),
        (r'X-Auth-Token:\s*[A-Za-z0-9]{20,}', "Hardcoded auth token detected"),
    ]

    all_files = glob.glob("modules/*.md") + glob.glob("*.md") + glob.glob("references/*.md")

    for filepath in all_files:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                for pattern, msg in patterns:
                    m = re.search(pattern, line)
                    if m:
                        # Skip if the matched value is a placeholder like
                        # {PASSWORD} or ${PASSWORD}. We inspect the matched
                        # string rather than the whole line, because a line
                        # may legitimately contain both a JSON object literal
                        # (with '{') and a hardcoded secret.
                        # Use group(1) if available (patterns with capture group), else fall back
                        try:
                            val = m.group(1)
                        except IndexError:
                            matched = m.group(0)
                            val_match = re.search(r'[:=]\s*["\']([^"\']*)["\']', matched)
                            val = val_match.group(1) if val_match else ""
                        if re.match(r'^\$\{[^}]+\}$', val) or re.match(r'^\{[^}]+\}$', val):
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
