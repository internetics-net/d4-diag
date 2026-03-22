# d4-diag Test Suite Documentation

## Overview

This directory contains comprehensive test cases for the d4-diag Python code analysis tool. The test suite ensures reliability, correctness, and maintainability of all components.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared test fixtures and utilities
├── test_utils.py               # Tests for utility functions
├── test_generate_mermaid.py    # Tests for CodeMapAnalyzer class
├── test_viewer_mermaid.py      # Tests for diagram viewer functionality
├── test_cli_basic.py           # Basic CLI functionality tests
├── test_main.py                # Comprehensive CLI tests
├── test_integration.py         # End-to-end integration tests
└── run_tests.py                # Test suite runner script
```

## Test Categories

### 1. Unit Tests (`test_utils.py`)

**Coverage:**
- `sanitize_id()` - String sanitization for Mermaid IDs
- `qlabel()` - Safe label quoting for Mermaid rendering
- `get_base_name()` - AST node name extraction
- `find_python_files()` - Recursive Python file discovery

**Key Test Cases:**
- Edge cases (empty strings, special characters, Unicode)
- Error handling (invalid AST nodes, malformed paths)
- Directory exclusion logic (virtual environments, caches)
- File system boundary conditions

### 2. CodeMapAnalyzer Tests (`test_generate_mermaid.py`)

**Coverage:**
- `CodeMapAnalyzer.__init__()` - Analyzer initialization
- `build_module_map()` - Module name mapping
- `analyze_file()` - Single file analysis
- Import resolution and edge detection
- Class and function extraction
- Error handling for malformed files

**Key Test Cases:**
- Large file handling (size limits)
- Syntax error recovery
- Encoding error handling
- Complex inheritance hierarchies
- Async function detection
- Import resolution (local vs external)

### 3. Viewer Tests (`test_viewer_mermaid.py`)

**Coverage:**
- `find_diagram_files()` - Diagram file discovery
- `read_diagram_content()` - File content reading
- `extract_mermaid_code()` - Mermaid code extraction
- `generate_html_viewer()` - HTML viewer generation
- `view_diagrams()` - Complete viewer workflow

**Key Test Cases:**
- Multiple diagram blocks handling
- Browser integration
- File system error handling
- HTML generation validation
- Mermaid syntax extraction

### 4. CLI Tests (`test_main.py`, `test_cli_basic.py`)

**Coverage:**
- CLI command structure and help
- Argument parsing and validation
- Error handling and exit codes
- Backward compatibility
- Output directory validation
- Project root detection

**Key Test Cases:**
- All command-line options
- Error conditions and messages
- Backward compatibility scenarios
- Security validations (output directory safety)
- Edge cases (empty projects, invalid paths)

### 5. Integration Tests (`test_integration.py`)

**Coverage:**
- End-to-end workflow testing
- Multi-file project analysis
- Complex project structures
- Error recovery in real scenarios
- Diagram generation validation

**Key Test Cases:**
- Complete analysis workflow
- Complex inheritance and imports
- Error handling in realistic scenarios
- Performance with various project sizes
- Generated diagram content validation

## Test Fixtures (`conftest.py`)

### Available Fixtures

1. **`temp_project_dir`** - Creates a temporary project with sample Python files:
   - `main.py` - Main application with class and function
   - `utils.py` - Utility functions and classes
   - `models/user.py` - Data model with dataclass
   - `services/auth.py` - Service with import dependencies
   - `.venv/` and `__pycache__/` - Excluded directories

2. **`empty_project_dir`** - Empty temporary directory for edge case testing

3. **`complex_project_dir`** - Complex project with:
   - Abstract base classes and protocols
   - Complex inheritance hierarchies
   - Nested module structures
   - Various import patterns

4. **`sample_python_file`** - Single file with various Python constructs for focused testing

## Running Tests

### Quick Test Run
```bash
cd d4-diag
python -m pytest tests/ -v
```

### Specific Test Category
```bash
# Unit tests only
python -m pytest tests/test_utils.py tests/test_generate_mermaid.py -v

# Integration tests only
python -m pytest tests/test_integration.py -v

# CLI tests only
python -m pytest tests/test_main.py -v
```

### Using Test Runner
```bash
# Basic test run
python tests/run_tests.py

# With coverage report
python tests/run_tests.py --coverage

# Quick run (minimal tests)
python tests/run_tests.py --quick
```

### With Coverage
```bash
python -m pytest tests/ --cov=d4_diag --cov-report=term-missing
```

## Test Coverage Areas

### Code Coverage Goals
- **Overall Coverage:** >80%
- **Core Functions:** >90%
- **Error Handling:** >85%
- **Edge Cases:** >75%

### Coverage Reports
- Terminal output with missing lines
- HTML report in `htmlcov/index.html`
- Coverage badge integration

## Test Quality Standards

### Test Naming Conventions
- Class names: `Test<ModuleName>`
- Method names: `test_<functionality>_<scenario>`
- Descriptive names that explain what is being tested

### Test Structure
```python
def test_functionality_scenario(self, fixture):
    """Brief description of what the test validates."""
    # Arrange
    # (setup test data and conditions)

    # Act
    # (execute the function being tested)

    # Assert
    # (verify expected outcomes)
```

### Error Handling Tests
- Every error path should have a corresponding test
- Test error messages and exit codes
- Verify graceful degradation

### Edge Cases
- Empty inputs
- Null/None values
- Maximum/minimum values
- Invalid data types
- File system boundaries

## Mocking Strategy

### When to Mock
- External dependencies (file system, network)
- Heavy operations (large file processing)
- User interaction (browser opening)
- Time-sensitive operations

### Mocking Examples
```python
# Mock file system operations
with patch('os.path.getsize', return_value=15 * 1024 * 1024):
    # Test large file handling

# Mock external services
with patch('webbrowser.open') as mock_browser:
    # Test browser integration

# Mock heavy operations
with patch('d4_diag.main.CodeMapAnalyzer') as mock_analyzer:
    # Test CLI without actual analysis
```

## Continuous Integration

### CI Pipeline Integration
- Tests run on every PR
- Coverage requirements enforced
- Performance regression detection
- Cross-platform compatibility

### Test Metrics
- Test execution time
- Coverage percentage
- Failure rate analysis
- Flaky test detection

## Adding New Tests

### When to Add Tests
- New functionality implementation
- Bug fixes (regression tests)
- Performance optimizations
- Edge case discoveries

### Test Checklist
- [ ] Test follows naming conventions
- [ ] Test has clear documentation
- [ ] Test covers both success and failure cases
- [ ] Test uses appropriate fixtures
- [ ] Test is deterministic (no random failures)
- [ ] Test has meaningful assertions

### Review Process
1. Code review for test quality
2. Coverage impact analysis
3. Performance impact assessment
4. Documentation updates

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure `PYTHONPATH` includes `src/` directory
- Check package installation: `pip install -e .`
- Verify virtual environment activation

**Fixture Issues:**
- Check fixture scope and dependencies
- Verify temporary directory permissions
- Ensure proper cleanup in fixtures

**Mock Issues:**
- Verify mock patch targets
- Check mock return values
- Ensure mock restoration

**Performance Issues:**
- Use test timeouts for long-running tests
- Optimize fixture setup/teardown
- Consider test categorization

### Debugging Tips
```bash
# Run with detailed output
python -m pytest tests/ -v -s

# Run specific test with debugging
python -m pytest tests/test_utils.py::TestSanitizeId::test_empty_string -v -s --pdb

# Stop on first failure
python -m pytest tests/ -x

# Run with local debugging
python -m pytest tests/ --tb=local
```

## Future Improvements

### Planned Enhancements
- Performance benchmarking tests
- Memory usage validation
- Concurrent execution testing
- Large-scale project testing
- Cross-platform compatibility matrix

### Test Automation
- Automated test generation
- Property-based testing
- Fuzzing for input validation
- Contract testing

This comprehensive test suite ensures that d4-diag remains reliable, maintainable, and bug-free as it evolves.
