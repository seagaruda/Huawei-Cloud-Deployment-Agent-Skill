#!/usr/bin/env python3
"""
Extract all API endpoints from module files for validation.
"""
import re
import sys
import glob

def extract_endpoints():
    endpoints = set()
    all_files = glob.glob("modules/*.md")
    
    for filepath in all_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find all Huawei Cloud API URLs
        urls = re.findall(r'https://[a-z]+\.(\{?\w+\}?)\.myhuaweicloud\.com(/[^\s\'"]+)?', content)
        for domain, path in urls:
            endpoint = f"https://*.{domain}.myhuaweicloud.com{path or ''}"
            endpoints.add(endpoint)
    
    print(f"Found {len(endpoints)} unique API endpoint patterns:")
    for ep in sorted(endpoints):
        print(f"  {ep}")
    
    # Write to file for further validation
    with open("scripts/endpoints.txt", "w") as f:
        for ep in sorted(endpoints):
            f.write(ep + "\n")

if __name__ == "__main__":
    extract_endpoints()
