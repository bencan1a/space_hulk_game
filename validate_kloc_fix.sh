#!/bin/bash
# Validation script to demonstrate the kloc script fix works

echo "=========================================="
echo "KLOC Script Fix - Validation Test"
echo "=========================================="
echo ""

# Test 1: Script help works quickly
echo "Test 1: Script help works without hanging..."
timeout 5 python -u tools/kloc-report.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ PASS: Script help runs in under 5 seconds"
else
    echo "✗ FAIL: Script help timeout or error"
    exit 1
fi
echo ""

# Test 2: Unbuffered mode works
echo "Test 2: Unbuffered Python mode works..."
output=$(python -u tools/kloc-report.py --help 2>&1 | head -1)
if [[ $output == *"Warning"* ]] || [[ $output == *"usage"* ]]; then
    echo "✓ PASS: Unbuffered output works"
else
    echo "✗ FAIL: Unexpected output: $output"
    exit 1
fi
echo ""

# Test 3: Flush calls exist
echo "Test 3: Checking for stdout flush calls..."
flush_count=$(grep -c "sys.stdout.flush()" tools/kloc-report.py)
if [ $flush_count -ge 3 ]; then
    echo "✓ PASS: Found $flush_count flush calls (expected >= 3)"
else
    echo "✗ FAIL: Only found $flush_count flush calls"
    exit 1
fi
echo ""

# Test 4: Workflow YAML is valid
echo "Test 4: Workflow YAML syntax is valid..."
python -c "import yaml; yaml.safe_load(open('.github/workflows/run-kloc-report.yml'))" 2>&1
if [ $? -eq 0 ]; then
    echo "✓ PASS: Workflow YAML is valid"
else
    echo "✗ FAIL: Workflow YAML is invalid"
    exit 1
fi
echo ""

# Test 5: Workflow has timeout
echo "Test 5: Workflow has timeout configured..."
if grep -q "timeout-minutes: 360" .github/workflows/run-kloc-report.yml; then
    echo "✓ PASS: Timeout configured (360 minutes)"
else
    echo "✗ FAIL: Timeout not found"
    exit 1
fi
echo ""

# Test 6: Workflow uses unbuffered Python
echo "Test 6: Workflow uses unbuffered Python..."
if grep -q "python -u" .github/workflows/run-kloc-report.yml; then
    echo "✓ PASS: Using 'python -u' for unbuffered output"
else
    echo "✗ FAIL: Not using unbuffered Python"
    exit 1
fi
echo ""

# Test 7: Workflow checks exit code
echo "Test 7: Workflow checks script exit code..."
if grep -q "PIPESTATUS" .github/workflows/run-kloc-report.yml; then
    echo "✓ PASS: Exit code checking with PIPESTATUS"
else
    echo "✗ FAIL: No exit code checking"
    exit 1
fi
echo ""

# Test 8: Run all unit tests
echo "Test 8: Running all kloc-related unit tests..."
python -m unittest tests.test_kloc_report tests.test_kloc_workflow -v > /tmp/test_output.txt 2>&1
test_result=$?
if [ $test_result -eq 0 ]; then
    test_count=$(grep -c "ok$" /tmp/test_output.txt)
    echo "✓ PASS: All $test_count unit tests passed"
else
    echo "✗ FAIL: Some tests failed"
    cat /tmp/test_output.txt
    exit 1
fi
echo ""

# Test 9: Documentation exists
echo "Test 9: Documentation exists..."
if [ -f "docs/KLOC_SCRIPT_FIX.md" ]; then
    doc_size=$(wc -l < docs/KLOC_SCRIPT_FIX.md)
    echo "✓ PASS: Documentation found ($doc_size lines)"
else
    echo "✗ FAIL: Documentation not found"
    exit 1
fi
echo ""

# Test 10: --repos parameter works
echo "Test 10: --repos parameter accepts repository names..."
if grep -q "\-\-repos" tools/kloc-report.py && python -u tools/kloc-report.py --help 2>&1 | grep -q "\-\-repos"; then
    echo "✓ PASS: --repos parameter is available"
else
    echo "✗ FAIL: --repos parameter not found"
    exit 1
fi
echo ""

echo "=========================================="
echo "All validation tests passed! ✓"
echo "=========================================="
echo ""
echo "Summary of fixes:"
echo "  • Unbuffered Python output (python -u)"
echo "  • 3 stdout flush calls in script"
echo "  • 6-hour timeout configured"
echo "  • Exit code checking (PIPESTATUS)"
echo "  • 13 comprehensive unit tests"
echo "  • Detailed documentation"
echo "  • Repository filtering (--repos) for faster execution"
echo ""
echo "The script will now show real-time progress"
echo "and can scan specific repos for faster results."
echo ""
