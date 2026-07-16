#!/usr/bin/env python3
"""
Validate that extracted API endpoints follow Huawei Cloud URL patterns.
"""
import re
import sys

def validate_endpoints():
    filepath = "scripts/endpoints.txt"
    try:
        with open(filepath, "r") as f:
            endpoints = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("ERROR: endpoints.txt not found. Run extract_endpoints.py first.")
        sys.exit(1)

    issues = []
    valid_services = ['vpc', 'ecs', 'elb', 'rds', 'obs', 'iam', 'cce', 'evs', 'vbs']
    
    for ep in endpoints:
        # Check basic URL structure
        m = re.match(r'https://\*\.(\{?\w+\}?)\.myhuaweicloud\.com(/[^\s]*)?', ep)
        if not m:
            issues.append(f"Invalid URL format: {ep}")
            continue
        
        region = m.group(1)
        path = m.group(2) or ""
        
        # Check API version in path
        if path and not re.search(r'/v[0-9]+(?:\.[0-9]+)?/', path):
            issues.append(f"Missing API version in path: {ep}")
    
    if issues:
        print(f"FAILED: {len(issues)} endpoint issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print(f"PASSED: All {len(endpoints)} endpoint patterns are valid.")
        sys.exit(0)

if __name__ == "__main__":
    validate_endpoints()
