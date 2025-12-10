# Vulnerability Count Validation Rules

## Rule Definition

For each test case file in `src/securibench/micro/`, **three values must match**:

1. **`@servlet vuln_count` annotation value**
2. **`getVulnerabilityCount()` method return value**  
3. **Count of `/* BAD */` comments in the code**

## Rule Details

### 1. Annotation Value

**Location**: In the class-level Javadoc comment

**Format**:
```java
/** 
 *  @servlet description="..." 
 *  @servlet vuln_count = "N" 
 *  */
```

**Extraction Pattern**: `@servlet\s+vuln_count\s*=\s*"(\d+)"`

**Example**:
```java
@servlet vuln_count = "1"   // Value: 1
@servlet vuln_count = "0"   // Value: 0
@servlet vuln_count = "3"   // Value: 3
```

### 2. Method Return Value

**Location**: In the `getVulnerabilityCount()` method

**Format**:
```java
public int getVulnerabilityCount() {
    return N;
}
```

**Extraction Pattern**: `public\s+int\s+getVulnerabilityCount\s*\(\s*\)\s*\{[^}]*return\s+(\d+)\s*;`

**Example**:
```java
public int getVulnerabilityCount() {
    return 1;   // Value: 1
}
```

### 3. BAD Comment Count

**Location**: Throughout the code, marking actual vulnerability locations

**Format**: `/* BAD */`

**Extraction Pattern**: `/\*\s*BAD\s*\*/`

**Example**:
```java
writer.println(str);    /* BAD */           // Count: 1
stmt.execute(query);    /* BAD */            // Count: 2
new FileWriter(path);   /* BAD */            // Count: 3
```

**Note**: 
- Only `/* BAD */` comments are counted
- `/* OK */` comments are **not** counted
- Comments are case-sensitive: `/* bad */` is **not** counted
- Format must be exact: `/* BAD */` (spaces matter)

## Validation Logic

### Step 1: Extract All Three Values

For each test case file:
1. Extract annotation value using regex pattern
2. Extract method return value using regex pattern  
3. Count `/* BAD */` comments using regex pattern

### Step 2: Validate Presence

- Annotation must exist (not null)
- Method must exist (not null)
- BAD comments count is always present (0 or more)

### Step 3: Validate Consistency

All three values must be equal:
```
annotation_count == method_count == bad_comment_count
```

## Validation Examples

### ✅ Valid Example

```java
/** 
 *  @servlet description="simple XSS" 
 *  @servlet vuln_count = "1"           ← 1
 *  */
public class Basic1 extends BasicTestCase implements MicroTestCase {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String str = req.getParameter("name");
        PrintWriter writer = resp.getWriter();
        writer.println(str);    /* BAD */    ← Count: 1
    }
    
    public int getVulnerabilityCount() {
        return 1;    ← 1
    }
}
```

**Result**: ✅ Valid (1 == 1 == 1)

### ✅ Valid Example (Zero Vulnerabilities)

```java
/** 
 *  @servlet description="unreachable code" 
 *  @servlet vuln_count = "0"           ← 0
 *  */
public class Pred1 extends BasicTestCase implements MicroTestCase {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("name");
        if(false) {
            PrintWriter writer = resp.getWriter();
            writer.println(name);    /* OK */    ← Count: 0 (OK not counted)
        }
    }
    
    public int getVulnerabilityCount() {
        return 0;    ← 0
    }
}
```

**Result**: ✅ Valid (0 == 0 == 0)

### ❌ Invalid Example (Count Mismatch)

```java
/** 
 *  @servlet description="..." 
 *  @servlet vuln_count = "1"           ← 1
 *  */
public class TestCase extends BasicTestCase implements MicroTestCase {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String str = req.getParameter("name");
        PrintWriter writer = resp.getWriter();
        writer.println(str);    /* BAD */    ← Count: 1
        writer.println(str);    /* BAD */    ← Count: 2
    }
    
    public int getVulnerabilityCount() {
        return 1;    ← 1
    }
}
```

**Result**: ❌ Invalid
- Annotation: 1
- Method: 1  
- BAD comments: 2
- **Error**: Annotation count (1) != BAD comment count (2)

### ❌ Invalid Example (Missing Annotation)

```java
/** 
 *  @servlet description="..." 
 *  // Missing vuln_count annotation
 *  */
public class TestCase extends BasicTestCase implements MicroTestCase {
    // ...
    public int getVulnerabilityCount() {
        return 1;
    }
}
```

**Result**: ❌ Invalid
- **Error**: Missing @servlet vuln_count annotation

### ❌ Invalid Example (Missing Method)

```java
/** 
 *  @servlet description="..." 
 *  @servlet vuln_count = "1"
 *  */
public class TestCase extends BasicTestCase implements MicroTestCase {
    // Missing getVulnerabilityCount() method
}
```

**Result**: ❌ Invalid
- **Error**: Missing or invalid getVulnerabilityCount() method

## Edge Cases

### Multiple Vulnerabilities

```java
@servlet vuln_count = "3"
// ...
new FileWriter(name);        /* BAD */    // 1
new FileWriter(name);        /* BAD */    // 2
new FileInputStream(name);   /* BAD */    // 3
// ...
return 3;
```

**Result**: ✅ Valid (3 == 3 == 3)

### Zero Vulnerabilities

```java
@servlet vuln_count = "0"
// ... no /* BAD */ comments ...
return 0;
```

**Result**: ✅ Valid (0 == 0 == 0)

### False Positive Tests

Some test cases are designed to test false positive detection. These should have:
- `vuln_count = "0"` (or appropriate count)
- `/* OK */` comments (not counted)
- No `/* BAD */` comments (or count matches annotation)

## Exclusions

The following files are **excluded** from validation:
- `BasicTestCase.java` (base class, not a test case)
- `MicroTestCase.java` (interface, not a test case)

## Implementation

### Python Script

See `validate_vuln_counts.py` for the reference implementation.

### Shell Script

See `validate_vuln_counts.sh` for a shell-based implementation.

### YAML Definition

See `validate_vuln_counts.yaml` for a machine-readable rule definition.

## Usage

```bash
# Validate all test cases
python3 validate_vuln_counts.py

# Validate specific directory
python3 validate_vuln_counts.py src/securibench/micro/basic/
```

## Output

### Valid File
```
✓ aliasing/Aliasing1.java
  Annotation: 1, Method: 1, BAD comments: 1
```

### Invalid File
```
✗ aliasing/Aliasing2.java
  Annotation: 1
  Method: 1
  BAD comments: 0
  ERROR: Annotation count (1) != BAD comment count (0)
  ERROR: Method count (1) != BAD comment count (0)
```

## Fixing Issues

1. **Count Mismatch**: Update annotation and method to match actual `/* BAD */` count
2. **Missing Annotation**: Add `@servlet vuln_count = "N"` to class Javadoc
3. **Missing Method**: Add `getVulnerabilityCount()` method returning the correct value
4. **Wrong Comment Count**: Add or remove `/* BAD */` comments to match declared count

