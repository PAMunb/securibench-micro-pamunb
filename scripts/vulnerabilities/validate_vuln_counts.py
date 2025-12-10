#!/usr/bin/env python3
"""
Vulnerability Count Validation Script

This script validates that for each test case, three values match:
1. The @servlet vuln_count annotation value
2. The return value in getVulnerabilityCount() method
3. The count of "/* BAD */" comments in the code

Usage:
    python3 validate_vuln_counts.py [directory]
    
    If no directory is specified, defaults to src/securibench/micro/
"""

import re
import sys
import os
from pathlib import Path
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validation for a single file"""
    file_path: str
    annotation_count: Optional[int]
    method_count: Optional[int]
    bad_comment_count: int
    is_valid: bool
    errors: List[str]


def extract_vuln_count_annotation(content: str) -> Optional[int]:
    """
    Extract the vuln_count value from @servlet annotation.
    
    Looks for: @servlet vuln_count = "N"
    """
    pattern = r'@servlet\s+vuln_count\s*=\s*"(\d+)"'
    match = re.search(pattern, content)
    if match:
        return int(match.group(1))
    return None


def extract_get_vulnerability_count(content: str) -> Optional[int]:
    """
    Extract the return value from getVulnerabilityCount() method.
    
    Looks for: public int getVulnerabilityCount() { return N; }
    """
    # Pattern to match the method and extract return value
    pattern = r'public\s+int\s+getVulnerabilityCount\s*\(\s*\)\s*\{[^}]*return\s+(\d+)\s*;'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return int(match.group(1))
    return None


def count_bad_comments(content: str) -> int:
    """
    Count the number of "/* BAD */" comments in the code.
    """
    # Pattern to match /* BAD */ comments
    # This handles various whitespace patterns
    pattern = r'/\*\s*BAD\s*\*/'
    matches = re.findall(pattern, content)
    return len(matches)


def validate_file(file_path: Path) -> ValidationResult:
    """
    Validate a single Java test case file.
    
    Returns a ValidationResult with all three counts and validation status.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return ValidationResult(
            file_path=str(file_path),
            annotation_count=None,
            method_count=None,
            bad_comment_count=0,
            is_valid=False,
            errors=[f"Error reading file: {e}"]
        )
    
    annotation_count = extract_vuln_count_annotation(content)
    method_count = extract_get_vulnerability_count(content)
    bad_comment_count = count_bad_comments(content)
    
    errors = []
    
    # Check if annotation exists
    if annotation_count is None:
        errors.append("Missing @servlet vuln_count annotation")
    
    # Check if method exists
    if method_count is None:
        errors.append("Missing or invalid getVulnerabilityCount() method")
    
    # Validate all three match
    if annotation_count is not None and method_count is not None:
        if annotation_count != method_count:
            errors.append(
                f"Annotation count ({annotation_count}) != method count ({method_count})"
            )
        if annotation_count != bad_comment_count:
            errors.append(
                f"Annotation count ({annotation_count}) != BAD comment count ({bad_comment_count})"
            )
        if method_count != bad_comment_count:
            errors.append(
                f"Method count ({method_count}) != BAD comment count ({bad_comment_count})"
            )
    
    is_valid = len(errors) == 0
    
    return ValidationResult(
        file_path=str(file_path),
        annotation_count=annotation_count,
        method_count=method_count,
        bad_comment_count=bad_comment_count,
        is_valid=is_valid,
        errors=errors
    )


def find_java_test_files(directory: Path) -> List[Path]:
    """
    Find all Java test case files in the directory.
    
    Excludes BasicTestCase.java and MicroTestCase.java (base classes).
    """
    java_files = []
    for java_file in directory.rglob("*.java"):
        # Skip base test case files
        if java_file.name in ["BasicTestCase.java", "MicroTestCase.java"]:
            continue
        java_files.append(java_file)
    return sorted(java_files)


def main():
    """Main validation function"""
    # Determine source directory
    if len(sys.argv) > 1:
        source_dir = Path(sys.argv[1])
    else:
        # Default to src/securibench/micro/
        script_dir = Path(__file__).parent
        source_dir = script_dir / "src" / "securibench" / "micro"
    
    if not source_dir.exists():
        print(f"Error: Directory not found: {source_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Validating test cases in: {source_dir}")
    print("=" * 80)
    
    # Find all Java test files
    java_files = find_java_test_files(source_dir)
    
    if not java_files:
        print(f"No Java test files found in {source_dir}")
        sys.exit(1)
    
    print(f"Found {len(java_files)} test case files\n")
    
    # Validate each file
    results = []
    for java_file in java_files:
        result = validate_file(java_file)
        results.append(result)
    
    # Report results
    valid_count = sum(1 for r in results if r.is_valid)
    invalid_count = len(results) - valid_count
    
    # Print detailed results
    for result in results:
        relative_path = Path(result.file_path).relative_to(source_dir.parent.parent)
        
        if result.is_valid:
            print(f"✓ {relative_path}")
            print(f"  Annotation: {result.annotation_count}, "
                  f"Method: {result.method_count}, "
                  f"BAD comments: {result.bad_comment_count}")
        else:
            print(f"✗ {relative_path}")
            if result.annotation_count is not None:
                print(f"  Annotation: {result.annotation_count}")
            else:
                print(f"  Annotation: MISSING")
            
            if result.method_count is not None:
                print(f"  Method: {result.method_count}")
            else:
                print(f"  Method: MISSING")
            
            print(f"  BAD comments: {result.bad_comment_count}")
            
            for error in result.errors:
                print(f"  ERROR: {error}")
        print()
    
    # Summary
    print("=" * 80)
    print(f"Summary: {valid_count} valid, {invalid_count} invalid out of {len(results)} files")
    
    # Exit with error code if any files are invalid
    if invalid_count > 0:
        sys.exit(1)
    else:
        print("All test cases validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()

