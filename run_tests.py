#!/usr/bin/env python3
"""
Quick test runner and debug tool for frontend application
Run with: python run_tests.py
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a shell command and report results"""
    print(f"\n{'='*60}")
    print(f">>> {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")
    
    # If cmd starts with pytest, use python -m pytest instead
    if cmd.startswith("pytest"):
        cmd = "python -m " + cmd
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("  FRONTEND TEST SUITE")
    print("="*60)
    
    # Change to frontend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Run all tests
    tests_total += 1
    if run_command(
        "pytest tests/test_app.py -v --tb=short",
        "Running all tests"
    ):
        tests_passed += 1
        print("All tests passed!")
    else:
        print(" Some tests failed")
    
    # Test 2: Run tests with coverage
    tests_total += 1
    if run_command(
        "pytest tests/test_app.py --cov=api_client --cov=config -v",
        "Running tests with coverage"
    ):
        tests_passed += 1
        print(" Coverage report generated!")
    else:
        print(" Coverage report not available")
    
    # Test 3: Run API client tests only
    tests_total += 1
    if run_command(
        "pytest tests/test_app.py::TestAPIClient -v",
        "Running API client tests"
    ):
        tests_passed += 1
        print(" API client tests passed!")
    else:
        print(" API client tests failed")
    
    # Test 4: Run config tests
    tests_total += 1
    if run_command(
        "pytest tests/test_app.py::TestConfig -v",
        "Running configuration tests"
    ):
        tests_passed += 1
        print(" Configuration tests passed!")
    else:
        print(" Configuration tests failed")
    
    # Test 5: Run integration tests
    tests_total += 1
    if run_command(
        "pytest tests/test_app.py::TestIntegration -v",
        "Running integration tests"
    ):
        tests_passed += 1
        print(" Integration tests passed!")
    else:
        print(" Integration tests failed")
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"  TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total test groups: {tests_total}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_total - tests_passed}")
    success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    print(f"{'='*60}\n")
    
    return 0 if tests_passed == tests_total else 1


if __name__ == "__main__":
    sys.exit(main())
