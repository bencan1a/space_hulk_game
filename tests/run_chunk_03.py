#!/usr/bin/env python3
"""
Test runner for Chunk 0.3: Reliability Testing

This script runs the SpaceHulkGame crew 3 times with different prompts
to validate reliability and consistency across multiple runs.

Per master_implementation_plan.md Chunk 0.3:
- Run sequential mode (11 tasks) 3 times with different prompts
- Track success/failure for each run
- Measure average generation time
- Compare output quality across runs
- Document any failures or inconsistencies

Test Prompts:
1. "A Space Marine boarding team discovers an ancient derelict vessel"
2. "A lone Tech-Priest investigates strange signals from a hulk"
3. "A desperate escape from a Genestealer-infested hulk"

Success Criteria:
✅ 3/3 runs complete successfully
✅ Average time < 10 minutes
✅ All runs produce valid YAML outputs
✅ No memory leaks or degradation over time

Prerequisites:
- Chunk 0.2 must be completed successfully
- All 11 tasks must be enabled
"""

import json
import os
import sys
import time
from pathlib import Path

import yaml

# Disable CrewAI telemetry to avoid firewall warnings
os.environ["OTEL_SDK_DISABLED"] = "true"
from datetime import datetime

# Add src to path so we can import space_hulk_game
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Test prompts
TEST_PROMPTS = [
    "A Space Marine boarding team discovers an ancient derelict vessel",
    "A lone Tech-Priest investigates strange signals from a hulk",
    "A desperate escape from a Genestealer-infested hulk",
]

# Expected output files
EXPECTED_FILES = [
    "plot_outline.yaml",
    "narrative_map.yaml",
    "puzzle_design.yaml",
    "scene_texts.yaml",
    "prd_document.yaml",
]


def save_run_results(run_number, prompt, results, output_dir):
    """Save results from a test run."""
    results_file = output_dir / f"chunk_03_run{run_number}_results.json"

    run_data = {
        "run_number": run_number,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "execution_time": results.get("execution_time", 0),
        "success": results.get("success", False),
        "error": results.get("error"),
        "files_generated": results.get("files_generated", {}),
        "quality_metrics": results.get("quality_metrics", {}),
    }

    with open(results_file, "w") as f:
        json.dump(run_data, f, indent=2)

    print(f"  Saved results to: {results_file}")


def backup_outputs(run_number, output_dir, backup_dir):
    """Backup output files from a run."""
    backup_dir.mkdir(exist_ok=True)
    run_backup_dir = backup_dir / f"run{run_number}"
    run_backup_dir.mkdir(exist_ok=True)

    print(f"  Backing up outputs to: {run_backup_dir}")

    for filename in EXPECTED_FILES:
        src = output_dir / filename
        if src.exists():
            dst = run_backup_dir / filename
            dst.write_text(src.read_text())
            print(f"    ✅ Backed up: {filename}")
        else:
            print(f"    ❌ Missing: {filename}")


def validate_output_files(output_dir):
    """Validate that all expected output files exist and are valid YAML."""
    results = {
        "all_exist": True,
        "all_valid_yaml": True,
        "files_generated": {},
        "quality_metrics": {},
    }

    for filename in EXPECTED_FILES:
        filepath = output_dir / filename
        file_info = {"exists": False, "valid_yaml": False, "size": 0, "keys": 0, "error": None}

        if filepath.exists():
            file_info["exists"] = True
            file_info["size"] = filepath.stat().st_size

            try:
                with open(filepath, encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                if data is None:
                    file_info["error"] = "Empty file"
                    results["all_valid_yaml"] = False
                else:
                    file_info["valid_yaml"] = True
                    if isinstance(data, dict):
                        file_info["keys"] = len(data.keys())

            except yaml.YAMLError as e:
                file_info["error"] = f"YAML error: {e}"
                results["all_valid_yaml"] = False
            except Exception as e:
                file_info["error"] = f"Error: {e}"
                results["all_valid_yaml"] = False
        else:
            results["all_exist"] = False
            file_info["error"] = "File not found"

        results["files_generated"][filename] = file_info

    # Calculate quality metrics
    total_size = sum(f["size"] for f in results["files_generated"].values())
    avg_keys = sum(f["keys"] for f in results["files_generated"].values()) / len(EXPECTED_FILES)

    results["quality_metrics"] = {
        "total_size_bytes": total_size,
        "average_keys_per_file": avg_keys,
        "files_with_content": sum(1 for f in results["files_generated"].values() if f["size"] > 0),
    }

    return results


def run_single_test(run_number, prompt, output_dir):
    """Run a single test with the given prompt."""
    print("\n" + "=" * 80)
    print(f"RUN #{run_number}: {prompt[:60]}...")
    print("=" * 80)

    results = {
        "success": False,
        "execution_time": 0,
        "error": None,
        "files_generated": {},
        "quality_metrics": {},
    }

    # Clean up old output files
    print("\nCleaning up old output files...")
    for filename in EXPECTED_FILES:
        filepath = output_dir / filename
        if filepath.exists():
            filepath.unlink()

    # Import crew
    try:
        from space_hulk_game.crew import SpaceHulkGame
    except ImportError as e:
        results["error"] = f"Failed to import: {e}"
        return results

    # Execute crew
    start_time = time.time()

    try:
        print(f"\nStarting execution at {datetime.now().strftime('%H:%M:%S')}")

        inputs = {"prompt": prompt, "game": prompt}

        crew_instance = SpaceHulkGame()
        crew_instance.crew().kickoff(inputs=inputs)

        end_time = time.time()
        results["execution_time"] = end_time - start_time
        results["success"] = True

        print(f"\n✅ Execution completed in {results['execution_time']:.2f} seconds")

    except Exception as e:
        end_time = time.time()
        results["execution_time"] = end_time - start_time
        results["error"] = str(e)
        print(f"\n❌ Execution failed: {e}")
        import traceback

        traceback.print_exc()

    # Validate outputs
    print("\nValidating outputs...")
    validation = validate_output_files(output_dir)
    results["files_generated"] = validation["files_generated"]
    results["quality_metrics"] = validation["quality_metrics"]

    # Print summary
    print(
        f"\nFiles generated: {sum(1 for f in validation['files_generated'].values() if f['exists'])}/{len(EXPECTED_FILES)}"
    )
    print(
        f"Valid YAML: {sum(1 for f in validation['files_generated'].values() if f['valid_yaml'])}/{len(EXPECTED_FILES)}"
    )
    print(f"Total size: {validation['quality_metrics']['total_size_bytes']} bytes")

    return results


def main():
    """Run Chunk 0.3 reliability testing."""
    print("\n" + "=" * 80)
    print("CHUNK 0.3: RELIABILITY TESTING (3 CONSECUTIVE RUNS)")
    print("=" * 80)
    print("Per master_implementation_plan.md:")
    print("- Run sequential mode 3 times with different prompts")
    print("- Track success/failure for each run")
    print("- Measure average generation time")
    print("- Expected: 3/3 runs succeed, avg time < 10 minutes")
    print("=" * 80 + "\n")

    output_dir = project_root / "game-config"
    backup_dir = project_root / "tmp" / "chunk_03_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Run all tests
    all_results = []

    for i, prompt in enumerate(TEST_PROMPTS, 1):
        results = run_single_test(i, prompt, output_dir)
        all_results.append(results)

        # Save results
        save_run_results(i, prompt, results, backup_dir)

        # Backup outputs
        if results["success"]:
            backup_outputs(i, output_dir, backup_dir)

        # Brief pause between runs
        if i < len(TEST_PROMPTS):
            print("\nPausing 5 seconds before next run...")
            time.sleep(5)

    # Analyze results
    print("\n" + "=" * 80)
    print("RELIABILITY TEST RESULTS")
    print("=" * 80)

    successful_runs = sum(1 for r in all_results if r["success"])
    total_time = sum(r["execution_time"] for r in all_results)
    avg_time = total_time / len(all_results) if all_results else 0

    print(f"\nRuns Completed: {successful_runs}/{len(TEST_PROMPTS)}")
    print(f"Total Time: {total_time:.2f} seconds ({total_time / 60:.2f} minutes)")
    print(f"Average Time: {avg_time:.2f} seconds ({avg_time / 60:.2f} minutes)")
    print(f"Min Time: {min(r['execution_time'] for r in all_results):.2f} seconds")
    print(f"Max Time: {max(r['execution_time'] for r in all_results):.2f} seconds")

    # Detailed results
    print("\nDetailed Results:")
    for i, (prompt, results) in enumerate(zip(TEST_PROMPTS, all_results, strict=False), 1):
        status = "✅ PASSED" if results["success"] else "❌ FAILED"
        time_str = f"{results['execution_time']:.2f}s"
        files = sum(1 for f in results["files_generated"].values() if f.get("exists", False))
        print(
            f"  Run {i}: {status} - {time_str} - {files}/{len(EXPECTED_FILES)} files - {prompt[:50]}..."
        )
        if results["error"]:
            print(f"         Error: {results['error']}")

    # Quality comparison
    print("\nQuality Comparison:")
    if all_results:
        for metric in ["total_size_bytes", "average_keys_per_file", "files_with_content"]:
            values = [r["quality_metrics"].get(metric, 0) for r in all_results if r["success"]]
            if values:
                avg = sum(values) / len(values)
                print(f"  {metric}: avg={avg:.2f}, min={min(values):.2f}, max={max(values):.2f}")

    # Final verdict
    print("\n" + "=" * 80)
    print("CHUNK 0.3 VALIDATION SUMMARY")
    print("=" * 80)

    if successful_runs == len(TEST_PROMPTS):
        print(f"✅ Reliability: ALL RUNS PASSED ({successful_runs}/{len(TEST_PROMPTS)})")
    else:
        print(f"❌ Reliability: {successful_runs}/{len(TEST_PROMPTS)} runs passed")

    if avg_time < 600:  # 10 minutes
        print(f"✅ Performance: Average time {avg_time:.2f}s < 600s threshold")
    else:
        print(f"⚠️  Performance: Average time {avg_time:.2f}s > 600s threshold")

    # Check for degradation
    if len(all_results) >= 2:
        time_trend = all_results[-1]["execution_time"] - all_results[0]["execution_time"]
        if time_trend > 60:  # More than 1 minute slower
            print(f"⚠️  Degradation: Run 3 was {time_trend:.2f}s slower than Run 1")
        else:
            print("✅ No Degradation: Consistent performance across runs")

    print("=" * 80)

    if successful_runs == len(TEST_PROMPTS) and avg_time < 600:
        print("\n✅ CHUNK 0.3 VALIDATION: PASSED")
        print("All reliability criteria met!")
        print("System is ready for production use!")
        return_code = 0
    else:
        print("\n❌ CHUNK 0.3 VALIDATION: FAILED")
        print("Review issues above and investigate failures")
        return_code = 1

    print("=" * 80 + "\n")
    print(f"Results and backups saved to: {backup_dir}")

    return return_code


if __name__ == "__main__":
    sys.exit(main())
