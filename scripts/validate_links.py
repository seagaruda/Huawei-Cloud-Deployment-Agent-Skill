#!/usr/bin/env python3
"""
Validate internal cross-references between SKILL.md and module files.
"""
import os
import sys
import glob

def validate_links():
    issues = []
    modules_dir = "modules"
    
    # Check all module files exist
    expected_modules = [
        "01-security-groups.md",
        "02-ecs.md",
        "03-eip.md",
        "04-bandwidth.md",
        "05-obs.md",
        "06-ecs-rds.md",
        "07-elb.md",
        "08-rds.md",
        "09-end-to-end.md",
    ]
    
    for module in expected_modules:
        path = os.path.join(modules_dir, module)
        if not os.path.exists(path):
            issues.append(f"Missing module file: {path}")
        else:
            # Check file is not empty
            if os.path.getsize(path) < 50:
                issues.append(f"Module file too small (may be empty): {path}")
    
    # Check references directory
    refs = glob.glob("references/*.md")
    for ref in refs:
        if not os.path.exists(ref):
            issues.append(f"Missing reference file: {ref}")
    
    # Check SKILL.md references modules
    skill_path = "SKILL.md"
    if os.path.exists(skill_path):
        with open(skill_path, "r") as f:
            content = f.read()
        for module in expected_modules:
            if module not in content:
                issues.append(f"SKILL.md does not reference {module}")
    
    if issues:
        print(f"FAILED: {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("PASSED: All internal references are valid.")
        sys.exit(0)

if __name__ == "__main__":
    validate_links()
