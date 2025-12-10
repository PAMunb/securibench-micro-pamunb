#!/bin/bash
#
# Vulnerability Count Validation Script (Shell version)
#
# This script validates that for each test case, three values match:
# 1. The @servlet vuln_count annotation value
# 2. The return value in getVulnerabilityCount() method
# 3. The count of "/* BAD */" comments in the code
#
# Usage:
#     ./validate_vuln_counts.sh [directory]
#
# If no directory is specified, defaults to src/securibench/micro/

set -e

# Determine source directory
if [ $# -ge 1 ]; then
    SOURCE_DIR="$1"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SOURCE_DIR="${SCRIPT_DIR}/src/securibench/micro"
fi

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Directory not found: $SOURCE_DIR" >&2
    exit 1
fi

echo "Validating test cases in: $SOURCE_DIR"
echo "=================================================================================="

# Find all Java test files (excluding base classes)
JAVA_FILES=$(find "$SOURCE_DIR" -name "*.java" \
    ! -name "BasicTestCase.java" \
    ! -name "MicroTestCase.java" \
    | sort)

if [ -z "$JAVA_FILES" ]; then
    echo "No Java test files found in $SOURCE_DIR"
    exit 1
fi

FILE_COUNT=$(echo "$JAVA_FILES" | wc -l)
echo "Found $FILE_COUNT test case files"
echo ""

VALID_COUNT=0
INVALID_COUNT=0

# Process each file
while IFS= read -r file; do
    # Extract relative path for display
    REL_PATH="${file#$SOURCE_DIR/../..}"
    REL_PATH="${REL_PATH#/}"
    
    # Extract annotation count
    ANNOTATION_COUNT=$(grep -oP '@servlet\s+vuln_count\s*=\s*"\K\d+' "$file" | head -1 || echo "")
    
    # Extract method return value
    METHOD_COUNT=$(grep -A 5 'public int getVulnerabilityCount()' "$file" | \
        grep -oP 'return\s+\K\d+' | head -1 || echo "")
    
    # Count BAD comments
    BAD_COMMENT_COUNT=$(grep -o '/\*\s*BAD\s*\*/' "$file" | wc -l)
    
    # Validate
    ERRORS=()
    
    if [ -z "$ANNOTATION_COUNT" ]; then
        ERRORS+=("Missing @servlet vuln_count annotation")
    fi
    
    if [ -z "$METHOD_COUNT" ]; then
        ERRORS+=("Missing or invalid getVulnerabilityCount() method")
    fi
    
    if [ -n "$ANNOTATION_COUNT" ] && [ -n "$METHOD_COUNT" ]; then
        if [ "$ANNOTATION_COUNT" != "$METHOD_COUNT" ]; then
            ERRORS+=("Annotation count ($ANNOTATION_COUNT) != method count ($METHOD_COUNT)")
        fi
        if [ "$ANNOTATION_COUNT" != "$BAD_COMMENT_COUNT" ]; then
            ERRORS+=("Annotation count ($ANNOTATION_COUNT) != BAD comment count ($BAD_COMMENT_COUNT)")
        fi
        if [ "$METHOD_COUNT" != "$BAD_COMMENT_COUNT" ]; then
            ERRORS+=("Method count ($METHOD_COUNT) != BAD comment count ($BAD_COMMENT_COUNT)")
        fi
    fi
    
    # Print result
    if [ ${#ERRORS[@]} -eq 0 ]; then
        echo "✓ $REL_PATH"
        echo "  Annotation: $ANNOTATION_COUNT, Method: $METHOD_COUNT, BAD comments: $BAD_COMMENT_COUNT"
        ((VALID_COUNT++))
    else
        echo "✗ $REL_PATH"
        if [ -n "$ANNOTATION_COUNT" ]; then
            echo "  Annotation: $ANNOTATION_COUNT"
        else
            echo "  Annotation: MISSING"
        fi
        if [ -n "$METHOD_COUNT" ]; then
            echo "  Method: $METHOD_COUNT"
        else
            echo "  Method: MISSING"
        fi
        echo "  BAD comments: $BAD_COMMENT_COUNT"
        for error in "${ERRORS[@]}"; do
            echo "  ERROR: $error"
        done
        ((INVALID_COUNT++))
    fi
    echo ""
    
done <<< "$JAVA_FILES"

# Summary
echo "=================================================================================="
echo "Summary: $VALID_COUNT valid, $INVALID_COUNT invalid out of $FILE_COUNT files"

if [ $INVALID_COUNT -gt 0 ]; then
    exit 1
else
    echo "All test cases validated successfully!"
    exit 0
fi

