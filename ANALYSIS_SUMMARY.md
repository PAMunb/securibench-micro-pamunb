# Securibench Micro - Complete Source Code Analysis Summary

## Project Overview

**Securibench Micro** is a security benchmark suite developed at Stanford University as part of the Griffin Security Project. It consists of small, focused test cases designed to evaluate the capabilities of static security analyzers and dynamic security testing tools.

**Version:** 1.08 (based on README, though some files reference 1.06)

**License:** Apache License 2.0

**Purpose:** Test security vulnerability detection tools through a comprehensive set of intentionally vulnerable Java servlet applications.

---

## Architecture & Structure

### Core Components

1. **MicroTestCase Interface** (`MicroTestCase.java`)
   - Defines the contract all test cases must implement
   - Requires `getDescription()` and `getVulnerabilityCount()` methods
   - Contains a constant `CONNECTION_STRING` for database connections
   - Uses XDoclet annotations (`@servlet`) for metadata

2. **BasicTestCase Abstract Class** (`BasicTestCase.java`)
   - Extends `HttpServlet` from J2EE
   - Provides base implementation for HTTP servlet methods (doTrace, doHead, doPost, doDelete, doPut)
   - All test cases extend this class

3. **Build System** (`build.xml`)
   - Apache Ant-based build system
   - Uses XDoclet for generating `web.xml` and `index.html`
   - Supports deployment to Tomcat application server
   - Includes Java2HTML for code colorization

---

## Test Case Categories

The suite is organized into **10 categories** with **96+ test cases** total:

### 1. **Basic** (42 test cases)
Tests fundamental security vulnerabilities:
- **XSS (Cross-Site Scripting)**: Direct output of user input (Basic1, Basic2)
- **String transformations**: Vulnerabilities through string operations like `toLowerCase()` (Basic3)
- **Conditional flows**: Vulnerabilities in conditional branches (Basic2)
- **Assignment chains**: Tracking taint through multiple assignments (Basic10)
- **SQL Injection**: Direct SQL query construction with user input (Basic19, Basic20, Basic21)
- **Complex data flows**: Various patterns of taint propagation

**Key Patterns:**
- Direct parameter → output (Basic1)
- Parameter → transformation → output (Basic3)
- Parameter → multiple assignments → output (Basic10)
- Parameter → SQL query construction (Basic20, Basic21)

### 2. **Arrays** (10 test cases)
Tests taint tracking through array operations:
- Array element assignment and retrieval (Arrays1)
- Multi-dimensional arrays
- Array indexing with tainted values
- Complex array access patterns

**Example:** `Arrays1` stores user input in an array and outputs it, testing if analyzers track taint through array operations.

### 3. **Collections** (15 test cases)
Tests taint propagation through Java Collections:
- **LinkedList**: Deposit/retrieve operations (Collections1)
- **ArrayList, HashMap, Vector**: Various collection types
- Nested collections
- Collection iteration patterns

**Example:** `Collections1` adds user input to a LinkedList and retrieves it, testing collection-aware taint analysis.

### 4. **Interprocedural (Inter)** (14 test cases)
Tests interprocedural analysis capabilities:
- **Method calls**: Simple identity methods (Inter1)
- **Multiple vulnerabilities**: Same tainted data used in multiple sinks (Inter2)
- **Call chains**: Deep call stacks
- **Method parameters**: Taint through method arguments
- **Return values**: Taint in return values

**Example:** `Inter1` calls an `id()` method that returns its parameter, testing if analyzers track taint across method boundaries.

### 5. **Aliasing** (6 test cases)
Tests pointer/alias analysis:
- **Simple aliasing**: Assignment creates alias (Aliasing1)
- **Field aliasing**: Object field assignments
- **Complex aliasing**: Multiple aliases to same object

**Example:** `Aliasing1` assigns user input to a variable and outputs it, testing alias-aware taint tracking.

### 6. **Predicates (Pred)** (9 test cases)
Tests path-sensitive analysis:
- **Unreachable code**: `if(false)` blocks (Pred1 - 0 vulnerabilities expected)
- **Conditional taint**: Taint only flows in certain branches
- **Path pruning**: Eliminating infeasible paths

**Example:** `Pred1` has user input output inside an `if(false)` block, testing if analyzers correctly identify this as safe.

### 7. **Reflection (Refl)** (4 test cases)
Tests reflection-aware analysis:
- **Method invocation**: Reflective method calls (Refl1)
- **Class loading**: Dynamic class loading
- **Method discovery**: Finding methods via reflection

**Example:** `Refl1` uses reflection to find and invoke a method with tainted parameters, testing reflection-aware taint tracking.

### 8. **Sanitizers** (6 test cases)
Tests sanitization recognition:
- **Sanitization functions**: Methods marked with `@sanitizer` annotation (Sanitizers1)
- **Partial sanitization**: Some paths sanitized, others not
- **Sanitization effectiveness**: Testing if sanitizers are correctly identified

**Example:** `Sanitizers1` has a `clean()` method that sanitizes HTML, but outputs both sanitized and unsanitized versions.

### 9. **Session** (3 test cases)
Tests session-aware analysis:
- **Session storage**: Storing tainted data in HTTP session (Session1)
- **Session retrieval**: Retrieving and using session data
- **Session lifecycle**: Taint across session boundaries

**Example:** `Session1` stores user input in session and outputs it, testing session-aware taint tracking.

### 10. **Strong Updates** (5 test cases)
Tests strong update analysis:
- **Overwriting taint**: Assigning safe value after tainted assignment (StrongUpdates1 - 0 vulnerabilities)
- **Kill analysis**: Determining when taint is eliminated
- **Flow sensitivity**: Order-dependent taint analysis

**Example:** `StrongUpdates1` assigns user input then overwrites it with a constant, testing if analyzers recognize the overwrite.

### 11. **Factories** (3 test cases)
Tests factory method analysis:
- **String factories**: Methods like `toLowerCase()` that create new strings (Factories1)
- **Object factories**: Methods that create new objects
- **Factory identification**: Distinguishing factories from identity functions

**Example:** `Factories1` calls `toLowerCase()` on user input, testing if analyzers recognize this as creating a new tainted string.

### 12. **Datastructures** (6 test cases)
Tests object-oriented taint tracking:
- **Field assignments**: Taint through object fields (Datastructures1)
- **Getter/setter methods**: Taint through accessor methods
- **Object encapsulation**: Taint in encapsulated data

**Example:** `Datastructures1` stores user input in an object field and retrieves it, testing OO-aware taint analysis.

---

## Vulnerability Types Tested

### 1. **Cross-Site Scripting (XSS)**
- Direct output of user input to HTTP response
- Output through various transformations
- Output in different contexts (HTML, JavaScript, attributes)

### 2. **SQL Injection**
- Direct SQL query construction with user input
- Prepared statement misuse
- Various SQL execution methods

### 3. **HTTP Response Splitting**
- User input in HTTP headers
- CRLF injection vulnerabilities

### 4. **Path Traversal**
- User input in file paths
- Directory traversal attacks

### 5. **General Taint Analysis**
- Tracking untrusted data from sources (HTTP parameters) to sinks (output, SQL queries)
- Various data flow patterns

---

## Technical Implementation Details

### Servlet Architecture
- All test cases are HTTP servlets extending `BasicTestCase`
- Implement `doGet()` method to handle HTTP GET requests
- Use `HttpServletRequest.getParameter()` as taint source
- Use `PrintWriter.println()` or SQL execution as taint sinks

### Taint Sources
- `HttpServletRequest.getParameter(String name)`
- `HttpServletRequest.getHeader(String name)`
- `HttpSession.getAttribute(String name)`

### Taint Sinks
- `PrintWriter.println(String)` - XSS vulnerability
- `Statement.execute(String)` - SQL injection
- `Statement.executeQuery(String)` - SQL injection
- `PreparedStatement` construction with tainted strings
- HTTP header setting methods

### Annotations & Metadata
- `@servlet description="..."` - Human-readable description
- `@servlet vuln_count="N"` - Expected number of vulnerabilities
- `@sanitizer` - Marks sanitization methods
- Comments like `/* BAD */` and `/* OK */` indicate expected vulnerability locations

### Build & Deployment
- **XDoclet**: Generates `web.xml` servlet mappings and `index.html` test case index
- **Java2HTML**: Colorizes source code for web viewing
- **Ant**: Compiles, deploys to Tomcat, generates documentation
- Test cases can be deployed as a web application for dynamic testing

---

## Analysis Challenges

The test suite is designed to challenge static analyzers in several ways:

1. **Interprocedural Analysis**: Tracking taint across method boundaries
2. **Alias Analysis**: Handling multiple references to the same data
3. **Path Sensitivity**: Distinguishing feasible from infeasible paths
4. **Reflection**: Handling dynamic method invocation
5. **Collections**: Tracking taint through generic data structures
6. **Object-Oriented**: Field-sensitive and context-sensitive analysis
7. **Sanitization**: Recognizing and modeling sanitization functions
8. **Strong Updates**: Detecting when taint is overwritten
9. **Factory Methods**: Distinguishing identity from factory methods

---

## Statistics

Based on the source code structure:
- **Total test cases**: 96+ (exact count varies by version)
- **Categories**: 10-12 (depending on classification)
- **Lines of code**: ~5,000-10,000 (estimated)
- **Vulnerability types**: Primarily XSS and SQL injection, with support for others

---

## Usage

### For Static Analysis Tools
1. Point analyzer at `src/securibench/micro/` directory
2. Run analysis
3. Compare detected vulnerabilities against expected counts in `@servlet vuln_count` annotations
4. Verify false positives/negatives

### For Dynamic Analysis Tools
1. Configure `build.properties` with Tomcat path
2. Run `ant cleandist` to build and deploy
3. Access test cases via web interface
4. Run penetration testing or dynamic analysis tools

### For Research
- Benchmark different analysis techniques
- Compare precision and recall of various tools
- Study specific analysis challenges (interprocedural, alias, etc.)

---

## Key Design Principles

1. **Micro-benchmarks**: Small, focused test cases (unlike full applications)
2. **Known answers**: Each test case specifies expected vulnerability count
3. **Executable**: Can be deployed and run as web application
4. **Comprehensive**: Covers many analysis challenges
5. **Incremental complexity**: From simple (Basic1) to complex (multi-file, deep call stacks)

---

## Notable Features

- **Self-documenting**: Each test case includes description and expected vulnerability count
- **Web interface**: Auto-generated index.html provides navigation to all test cases
- **Colorized source**: HTML versions of source code for easy browsing
- **Extensible**: Easy to add new test cases following the pattern

---

## Limitations & Notes

- **Intentional vulnerabilities**: All test cases contain known security flaws - **DO NOT deploy to production**
- **Java/J2EE specific**: Tests are Java servlet-based
- **Version differences**: Some discrepancies between documented version (1.08) and file metadata (1.06)
- **Count variations**: Actual file count may differ from documented statistics

---

## Conclusion

Securibench Micro is a well-structured, comprehensive benchmark suite for evaluating security analysis tools. It systematically tests various aspects of static and dynamic analysis, from simple direct flows to complex interprocedural, alias-aware, and reflection-based scenarios. The suite is particularly valuable for:

- **Tool developers**: Testing and improving analysis capabilities
- **Researchers**: Benchmarking new analysis techniques
- **Security practitioners**: Understanding analysis tool limitations
- **Educators**: Teaching security analysis concepts

The codebase demonstrates careful design to challenge analyzers while maintaining clarity and executability.

