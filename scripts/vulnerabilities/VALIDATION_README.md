# Vulnerability Count Validation

This directory contains validation tools to ensure consistency of vulnerability counts across all test cases.

## Validation Rule

For each test case, **three values must match**:

1. **`@servlet vuln_count` annotation value** - The declared count in the servlet annotation
2. **`getVulnerabilityCount()` method return value** - The value returned by the method
3. **Count of `/* BAD */` comments** - The number of vulnerability markers in the code

### Example

```java
/** 
 *  @servlet description="simple XSS" 
 *  @servlet vuln_count = "1"    ← Must match
 *  */
public class Basic1 extends BasicTestCase implements MicroTestCase {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String str = req.getParameter("name");
        PrintWriter writer = resp.getWriter();
        writer.println(str);    /* BAD */    ← Count: 1 (must match)
    }
    
    public int getVulnerabilityCount() {
        return 1;    ← Must match
    }
}
```

## Validation Tools

### 1. Python Script (Recommended)

**File**: `validate_vuln_counts.py`

**Usage**:
```bash
# Validate all test cases (default: src/securibench/micro/)
python3 scripts/vulnerabilities/validate_vuln_counts.py src/securibench/micro
```

**Features**:
- Cross-platform (Windows, Linux, macOS)
- Detailed error reporting
- Color-coded output (✓ for valid, ✗ for invalid)
- Summary statistics

**Output Example**:
```
Validating test cases in: src/securibench/micro
================================================================================
Found 96 test case files

✓ aliasing/Aliasing1.java
  Annotation: 1, Method: 1, BAD comments: 1

✗ basic/Basic1.java
  Annotation: 1
  Method: 1
  BAD comments: 2
  ERROR: Annotation count (1) != BAD comment count (2)

================================================================================
Summary: 95 valid, 1 invalid out of 96 files
```

### 2. Shell Script

**File**: `validate_vuln_counts.sh`

**Usage**:
```bash
# Make executable (first time only)
chmod +x validate_vuln_counts.sh

# Validate all test cases
./validate_vuln_counts.sh

# Validate specific directory
./validate_vuln_counts.sh src/securibench/micro/basic/
```

**Features**:
- Works on Unix-like systems (Linux, macOS)
- No external dependencies (uses standard shell tools)
- Same output format as Python script


## Known Issues in Test Suite

The validator has identified some inconsistencies in the existing test suite:

1. **Aliasing2.java**: `vuln_count = "1"` but has 0 `/* BAD */` comments (has `/* OK */` instead)
   - This is a false positive test case, so it should likely be `vuln_count = "0"`

2. **Aliasing4.java**: `vuln_count = "1"` but has 2 `/* BAD */` comments
   - Should likely be `vuln_count = "2"` to match the actual vulnerabilities

These are actual inconsistencies in the test suite that the validator correctly identifies.

## Common Issues

### Issue 1: Missing Annotation

**Error**: `Missing @servlet vuln_count annotation`

**Fix**: Add the annotation to the class Javadoc:
```java
/** 
 *  @servlet description="..." 
 *  @servlet vuln_count = "1" 
 *  */
```

### Issue 2: Missing Method

**Error**: `Missing or invalid getVulnerabilityCount() method`

**Fix**: Add the method:
```java
public int getVulnerabilityCount() {
    return 1;  // Match the annotation value
}
```

### Issue 3: Count Mismatch

**Error**: `Annotation count (1) != BAD comment count (2)`

**Fix**: Either:
- Add missing `/* BAD */` comments where vulnerabilities exist
- Remove extra `/* BAD */` comments if they're false positives
- Update the annotation and method to match the actual count

### Issue 4: Wrong Comment Format

**Error**: BAD comments not counted

**Fix**: Use exact format: `/* BAD */` (case-sensitive, with spaces)

**Valid formats**:
- `/* BAD */`
- `/*BAD*/` (may work, but not recommended)

**Invalid formats**:
- `// BAD` (single-line comment)
- `/* bad */` (lowercase)
- `/*BAD` (missing closing)

## Testing the Validator

Test the validator on a known-good file:

```bash
# Test on a single file
python3 validate_vuln_counts.py src/securibench/micro/aliasing/

# Should show all files as valid (✓)
```

## Troubleshooting

### Python Script Not Found

**Error**: `python3: command not found`

**Solution**: 
- Install Python 3.6 or higher
- Or use `python` instead of `python3`
- Or use the shell script version

### Permission Denied (Shell Script)

**Error**: `Permission denied: ./validate_vuln_counts.sh`

**Solution**:
```bash
chmod +x validate_vuln_counts.sh
```

### No Files Found

**Error**: `No Java test files found`

**Solution**: 
- Check that you're in the correct directory
- Verify the path: `src/securibench/micro/`
- Ensure Java files exist in subdirectories

## Contributing

When adding new test cases:

1. **Add the annotation**:
   ```java
   @servlet vuln_count = "N"
   ```

2. **Add the method**:
   ```java
   public int getVulnerabilityCount() {
       return N;  // Must match annotation
   }
   ```

3. **Mark vulnerabilities**:
   ```java
   writer.println(tainted);  /* BAD */
   ```

4. **Run validation**:
   ```bash
   python3 validate_vuln_counts.py
   ```

5. **Fix any errors** before committing

## Advanced Usage

### JSON Output (Python script modification)

Modify the script to output JSON for programmatic processing:

```python
import json
# ... in main()
results_dict = {
    "valid": valid_count,
    "invalid": invalid_count,
    "total": len(results),
    "files": [
        {
            "file": r.file_path,
            "valid": r.is_valid,
            "annotation": r.annotation_count,
            "method": r.method_count,
            "bad_comments": r.bad_comment_count,
            "errors": r.errors
        }
        for r in results
    ]
}
print(json.dumps(results_dict, indent=2))
```

### Filtering Results

Show only invalid files:

```bash
python3 validate_vuln_counts.py | grep -A 10 "✗"
```

Show summary only:

```bash
python3 validate_vuln_counts.py | tail -5
```

## License

Same as the main project (Apache License 2.0)

