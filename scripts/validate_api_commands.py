#!/usr/bin/env python3
"""
Validate that all curl commands in module files have valid JSON payloads.
This catches syntax errors before they reach production.
"""
import re
import json
import sys
import os
import glob

def normalize_bash_vars(payload):
    """Replace bash variables like ${VAR} or $VAR with placeholder values for JSON validation."""
    # Replace "${VAR}" (quoted bash var) with "placeholder"
    payload = re.sub(r'"\$[\{][A-Za-z_][A-Za-z0-9_]*[\}]"', '"PLACEHOLDER"', payload)
    payload = re.sub(r'"\$[A-Za-z_][A-Za-z0-9_]*"', '"PLACEHOLDER"', payload)
    # Replace ${VAR} (unquoted bash var, used as number) with 0
    payload = re.sub(r'\$\{[A-Za-z_][A-Za-z0-9_]*\}', '0', payload)
    # Replace $VAR (unquoted, no braces) with 0
    payload = re.sub(r'\$[A-Za-z_][A-Za-z0-9_]*', '0', payload)
    # Fix "app-${VAR}" patterns (concatenation)
    payload = re.sub(r'"app-\$[\{][A-Za-z_][A-Za-z0-9_]*[\}]"', '"app-PLACEHOLDER"', payload)
    return payload

def extract_curl_commands(directory):
    """Extract all curl -d payloads from markdown files."""
    modules_dir = os.path.join(directory, "modules")
    if not os.path.isdir(modules_dir):
        print(f"ERROR: modules/ directory not found")
        sys.exit(1)

    issues = []
    files_checked = 0
    payloads_found = 0

    for filepath in sorted(glob.glob(os.path.join(modules_dir, "*.md"))):
        files_checked += 1
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all -d '...' and -d "..." patterns
        # Pattern 1: -d '{...}'
        single_quoted = re.findall(r"-d\s+'((?:[^'\\]|\\.)*)'", content)
        # Pattern 2: -d "{...}"
        double_quoted = re.findall(r'-d\s+"((?:[^"\\]|\\.)*)"', content)

        for payload in single_quoted + double_quoted:
            payloads_found += 1
            # Unescape for JSON parsing
            cleaned = payload.replace('\\"', '"').replace('\\n', '\n').strip()
            if not cleaned:
                continue

            # Skip if it looks like a non-JSON payload (e.g., date command)
            if not cleaned.startswith('{'):
                continue

            # Normalize bash variables for validation
            normalized = normalize_bash_vars(cleaned)

            try:
                json.loads(normalized)
            except json.JSONDecodeError as e:
                issues.append(f"  {filename}: Invalid JSON in payload: {e}")

    print(f"Files checked: {files_checked}")
    print(f"JSON payloads found: {payloads_found}")

    if issues:
        print(f"\nFAILED: {len(issues)} invalid JSON payload(s):")
        for issue in issues:
            print(issue)
        sys.exit(1)
    else:
        print(f"\nPASSED: All {payloads_found} JSON payloads are valid.")
        sys.exit(0)

if __name__ == "__main__":
    extract_curl_commands(".")
