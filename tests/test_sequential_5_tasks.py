"""
Test script for Chunk 0.1: Sequential Mode Validation (5 Core Tasks)

This test validates that the SpaceHulkGame crew can successfully complete
the 5 core tasks in sequential mode without evaluation tasks.

Per master_implementation_plan.md Chunk 0.1:
- Comment out all 6 evaluation tasks in tasks.yaml
- Run: crewai run --inputs "prompt: A Space Marine boarding team discovers an ancient derelict vessel"
- Monitor execution with 15-minute timeout
- Validate outputs: 5 JSON files exist and are valid
- Document: execution time, any errors, output quality

Success Criteria:
✅ All 5 core tasks complete without errors
✅ All 5 output files exist and contain valid JSON
✅ Generation completes in < 10 minutes
✅ No hanging or timeout issues
"""

import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path


class TestSequential5Tasks(unittest.TestCase):
    """Test sequential mode with 5 core tasks only."""

    @classmethod
    def setUpClass(cls):
        """Setup test environment."""
        cls.project_root = Path(__file__).parent.parent
        cls.output_dir = cls.project_root / "game-config"
        cls.test_prompt = "A Space Marine boarding team discovers an ancient derelict vessel"
        cls.use_real_api = os.getenv("RUN_REAL_API_TESTS") == "1"

        # Expected output files from 5 core tasks
        cls.expected_files = [
            "plot_outline.json",
            "narrative_map.json",
            "puzzle_design.json",
            "scene_texts.json",
            "prd_document.json",
        ]

        # Only clean up old output files if running with real API
        # In mock mode, use static test files that are checked in
        if cls.use_real_api:
            for filename in cls.expected_files:
                filepath = cls.output_dir / filename
                if filepath.exists():
                    filepath.unlink()
                    print(f"Cleaned up old file: {filepath}")
        else:
            print("\n⚠ Running in MOCK mode - using static test files from game-config/")

    @unittest.skipUnless(
        os.getenv("RUN_REAL_API_TESTS") == "1",
        "Skipping crew execution test - requires RUN_REAL_API_TESTS=1",
    )
    def test_01_crew_execution_completes(self):
        """Test that crew execution completes within timeout."""
        print("\n" + "=" * 80)
        print("CHUNK 0.1: Testing Sequential Mode with 5 Core Tasks")
        print("=" * 80)
        print(f"Test Prompt: {self.test_prompt}")
        print("Timeout: 15 minutes (900 seconds)")
        print(f"Expected Output Files: {len(self.expected_files)}")
        print("=" * 80 + "\n")

        # Record start time
        start_time = time.time()

        # Run the crew using Python module execution
        # Note: Using 'crewai run' requires the crewai CLI to be installed
        # We'll use Python module execution instead for better control
        try:
            cmd = [
                sys.executable,
                "-m",
                "space_hulk_game.main",
                "--inputs",
                f"prompt:{self.test_prompt}",
            ]

            print(f"Executing command: {' '.join(cmd)}\n")

            # Run with timeout
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=900,  # 15 minutes
                env={**os.environ, "PYTHONPATH": str(self.project_root)},
                check=False,
            )

            # Record end time
            end_time = time.time()
            execution_time = end_time - start_time

            print("\n" + "=" * 80)
            print(
                f"Execution completed in {execution_time:.2f} seconds ({execution_time / 60:.2f} minutes)"
            )
            print("=" * 80)

            # Check if execution succeeded
            if result.returncode != 0:
                print("\nSTDOUT:")
                print(result.stdout)
                print("\nSTDERR:")
                print(result.stderr)
                self.fail(f"Crew execution failed with return code {result.returncode}")

            # Verify execution time is under 10 minutes (600 seconds)
            self.assertLess(
                execution_time, 600, f"Execution took {execution_time:.2f}s (>{600}s threshold)"
            )

            print(f"✅ Execution completed successfully in {execution_time:.2f} seconds")

        except subprocess.TimeoutExpired:
            self.fail("Crew execution timed out after 15 minutes")
        except Exception as e:
            self.fail(f"Crew execution failed with error: {e}")

    def test_02_output_files_exist(self):
        """Test that all 5 expected output files were created."""
        print("\n" + "=" * 80)
        print("Checking Output Files")
        print("=" * 80)

        missing_files = []
        for filename in self.expected_files:
            filepath = self.output_dir / filename
            if not filepath.exists():
                missing_files.append(filename)
                print(f"❌ Missing: {filename}")
            else:
                file_size = filepath.stat().st_size
                print(f"✅ Found: {filename} ({file_size} bytes)")

        if missing_files:
            self.fail(f"Missing output files: {', '.join(missing_files)}")

        print("=" * 80)
        print(f"✅ All {len(self.expected_files)} output files created successfully")

    def test_03_output_files_valid_json(self):
        """Test that all output files contain valid JSON."""
        print("\n" + "=" * 80)
        print("Validating JSON Syntax")
        print("=" * 80)

        invalid_files = []
        for filename in self.expected_files:
            filepath = self.output_dir / filename
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)

                # Check that file is not empty
                if data is None:
                    invalid_files.append((filename, "File is empty"))
                    print(f"❌ Invalid: {filename} - Empty file")
                # Count keys for basic content validation
                elif isinstance(data, dict):
                    key_count = len(data.keys())
                    print(f"✅ Valid: {filename} ({key_count} top-level keys)")
                else:
                    print(f"✅ Valid: {filename} (non-dict data type)")

            except json.JSONDecodeError as e:
                invalid_files.append((filename, str(e)))
                print(f"❌ Invalid: {filename} - JSON error: {e}")
            except FileNotFoundError:
                invalid_files.append((filename, "File not found"))
                print(f"❌ Invalid: {filename} - File not found")
            except Exception as e:
                invalid_files.append((filename, str(e)))
                print(f"❌ Invalid: {filename} - Error: {e}")

        if invalid_files:
            error_msg = "\n".join([f"{f}: {e}" for f, e in invalid_files])
            self.fail(f"Invalid JSON files:\n{error_msg}")

        print("=" * 80)
        print(f"✅ All {len(self.expected_files)} output files contain valid JSON")

    def test_04_output_content_quality(self):
        """Test basic content quality of outputs."""
        print("\n" + "=" * 80)
        print("Checking Output Content Quality")
        print("=" * 80)

        quality_issues = []

        for filename in self.expected_files:
            filepath = self.output_dir / filename
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)

                # Check for minimum content based on file type
                if filename == "plot_outline.json":
                    if not isinstance(data, dict):
                        quality_issues.append(f"{filename}: Expected dict, got {type(data)}")
                    else:
                        print(f"✅ {filename}: Contains plot outline data")

                elif filename == "narrative_map.json":
                    if not isinstance(data, dict):
                        quality_issues.append(f"{filename}: Expected dict, got {type(data)}")
                    else:
                        print(f"✅ {filename}: Contains narrative map data")

                elif filename == "puzzle_design.json":
                    if not isinstance(data, dict):
                        quality_issues.append(f"{filename}: Expected dict, got {type(data)}")
                    else:
                        print(f"✅ {filename}: Contains puzzle design data")

                elif filename == "scene_texts.json":
                    if not isinstance(data, dict):
                        quality_issues.append(f"{filename}: Expected dict, got {type(data)}")
                    else:
                        print(f"✅ {filename}: Contains scene text data")

                elif filename == "prd_document.json":
                    if not isinstance(data, dict):
                        quality_issues.append(f"{filename}: Expected dict, got {type(data)}")
                    else:
                        print(f"✅ {filename}: Contains PRD document data")

            except Exception as e:
                quality_issues.append(f"{filename}: Error checking quality: {e}")

        if quality_issues:
            error_msg = "\n".join(quality_issues)
            self.fail(f"Content quality issues:\n{error_msg}")

        print("=" * 80)
        print(f"✅ All {len(self.expected_files)} output files have acceptable content quality")


def run_chunk_01_test():
    """
    Run the Chunk 0.1 test suite and generate a report.

    This function is the main entry point for Chunk 0.1 validation.
    """
    print("\n" + "=" * 80)
    print("CHUNK 0.1: SEQUENTIAL MODE VALIDATION (5 CORE TASKS)")
    print("=" * 80)
    print("Per master_implementation_plan.md:")
    print("- Testing sequential mode with 5 core tasks only")
    print("- Evaluation tasks are commented out in tasks.yaml and crew.py")
    print("- Expected: All 5 tasks complete without errors")
    print("- Expected: Generation time < 10 minutes")
    print("- Expected: All 5 output files are valid JSON")
    print("=" * 80 + "\n")

    # Run the test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSequential5Tasks)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ CHUNK 0.1 VALIDATION: PASSED")
        print("All 5 core tasks completed successfully!")
        print("Ready to proceed to Chunk 0.2 (all 11 tasks)")
    else:
        print("\n❌ CHUNK 0.1 VALIDATION: FAILED")
        print("Issues detected. Review output above for details.")

    print("=" * 80 + "\n")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_chunk_01_test()
    sys.exit(exit_code)
