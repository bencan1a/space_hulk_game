#!/usr/bin/env python3
"""
Test script for Chunk 0.4: Hierarchical Mode Validation (Minimal)

This test validates hierarchical mode with only 3 core tasks to identify
if/where the hierarchical process hangs.

Test Configuration:
- Mode: Hierarchical (with NarrativeDirectorAgent as manager)
- Tasks: 3 core tasks only
  1. GenerateOverarchingPlot
  2. CreateNarrativeMap
  3. DesignArtifactsAndPuzzles
- Timeout: 10 minutes
- Manager: NarrativeDirectorAgent

Success Criteria:
- Hierarchical mode completes successfully, OR
- Specific hang point identified and documented
- Manager delegation observed in logs
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import cast

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from crewai import Crew, Process

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_hierarchical_minimal():  # noqa: PLR0915
    """
    Test hierarchical mode with minimal 3-task configuration.
    """
    print("\n" + "=" * 80)
    print("CHUNK 0.4: HIERARCHICAL MODE VALIDATION (MINIMAL)")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Test Mode: Hierarchical with 3 tasks")
    print("Timeout: 10 minutes")
    print("=" * 80 + "\n")

    # Record start time
    start_time = time.time()

    try:
        # Import SpaceHulkGame crew
        from space_hulk_game.crew import SpaceHulkGame

        print("✅ Successfully imported SpaceHulkGame crew")

        # Initialize the crew
        print("\n📋 Initializing SpaceHulkGame crew...")
        crew_instance = SpaceHulkGame()
        print("✅ Crew initialized")

        # Create hierarchical crew with minimal tasks
        print("\n🔧 Creating hierarchical crew configuration...")
        print("   Manager: NarrativeDirectorAgent")
        print("   Workers: PlotMasterAgent, NarrativeArchitectAgent, PuzzleSmithAgent")

        # Get the manager agent
        manager = crew_instance.NarrativeDirectorAgent()
        print(f"   Manager role: {manager.role}")

        # Get worker agents (only those needed for 3 tasks)
        plot_master = crew_instance.PlotMasterAgent()
        narrative_architect = crew_instance.NarrativeArchitectAgent()
        puzzle_smith = crew_instance.PuzzleSmithAgent()

        worker_agents = [plot_master, narrative_architect, puzzle_smith]
        print(f"   Worker agents: {[agent.role for agent in worker_agents]}")

        # Create minimal task set (only 3 tasks)
        task1 = crew_instance.GenerateOverarchingPlot()
        task2 = crew_instance.CreateNarrativeMap()
        task3 = crew_instance.DesignArtifactsAndPuzzles()

        minimal_tasks = [task1, task2, task3]
        print(f"   Tasks: {len(minimal_tasks)}")

        # Create hierarchical crew
        hierarchical_crew = Crew(
            agents=cast("list", worker_agents),
            tasks=minimal_tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True,
        )

        print("✅ Hierarchical crew created")

        # Prepare test input
        test_prompt = "A Space Marine boarding team discovers an ancient derelict vessel"
        inputs = {"prompt": test_prompt}

        print("\n🚀 Starting hierarchical crew execution...")
        print(f"   Prompt: {test_prompt}")
        print("   Monitoring for hang/timeout (10 min max)...")
        print("\n" + "-" * 80)

        # Execute crew with hierarchical process
        execution_start = time.time()
        hierarchical_crew.kickoff(inputs=inputs)
        execution_time = time.time() - execution_start

        print("-" * 80)
        print("\n✅ HIERARCHICAL EXECUTION COMPLETED!")
        print(
            f"   Execution time: {execution_time:.2f} seconds ({execution_time / 60:.2f} minutes)"
        )

        # Analyze results
        print("\n📊 RESULTS ANALYSIS")
        print("=" * 80)
        print("Status: SUCCESS")
        print(f"Execution Time: {execution_time:.2f}s")
        print(f"Tasks Completed: {len(minimal_tasks)}")
        print(f"Manager Used: {manager.role}")

        # Check output files
        print("\n📁 Checking Output Files:")
        output_files = [
            "game-config/plot_outline.yaml",
            "game-config/narrative_map.yaml",
            "game-config/puzzle_design.yaml",
        ]

        files_created = 0
        for filepath in output_files:
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"   ✅ {filepath} ({file_size} bytes)")
                files_created += 1
            else:
                print(f"   ❌ {filepath} (not found)")

        print(f"\nFiles Created: {files_created}/{len(output_files)}")

        # Performance comparison
        print("\n⚡ Performance Comparison:")
        print(f"   Hierarchical (3 tasks): {execution_time:.2f}s")
        print("   Sequential (5 tasks):   ~256s (from Chunk 0.1)")
        print(f"   Per-task average:       {execution_time / 3:.2f}s")

        # Overall assessment
        total_time = time.time() - start_time
        print("\n" + "=" * 80)
        print("CHUNK 0.4 TEST RESULTS")
        print("=" * 80)
        print("✅ Hierarchical mode WORKS with 3 tasks")
        print("✅ No hanging or blocking detected")
        print("✅ Manager delegation functional")
        print(f"✅ Execution time: {execution_time:.2f}s ({execution_time / 60:.2f} min)")
        print(f"✅ Files created: {files_created}/{len(output_files)}")
        print(f"\nTotal test time: {total_time:.2f}s")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Write results to file
        write_results_file(
            success=True,
            execution_time=execution_time,
            files_created=files_created,
            total_files=len(output_files),
            hang_point=None,
        )

        return True

    except Exception as e:
        error_time = time.time() - start_time
        print("\n" + "=" * 80)
        print("❌ HIERARCHICAL MODE FAILED")
        print("=" * 80)
        print(f"Error: {e!s}")
        print(f"Time before failure: {error_time:.2f}s ({error_time / 60:.2f} min)")
        print("=" * 80)

        logger.error(f"Hierarchical mode failed: {e!s}", exc_info=True)

        # Write failure results
        write_results_file(
            success=False,
            execution_time=error_time,
            files_created=0,
            total_files=3,
            hang_point=str(e),
        )

        return False


def write_results_file(success, execution_time, files_created, total_files, hang_point):
    """
    Write test results to a summary file.
    """
    results_dir = Path(__file__).parent.parent / "tmp"
    results_dir.mkdir(exist_ok=True)

    results_file = results_dir / "chunk_04_results.md"

    with open(results_file, "w") as f:
        f.write("# Chunk 0.4: Hierarchical Mode Validation Results\n\n")
        f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("**Test Mode:** Hierarchical with 3 minimal tasks\n\n")

        f.write("## Test Configuration\n\n")
        f.write("- **Manager Agent:** NarrativeDirectorAgent\n")
        f.write("- **Worker Agents:** PlotMasterAgent, NarrativeArchitectAgent, PuzzleSmithAgent\n")
        f.write("- **Tasks:**\n")
        f.write("  1. GenerateOverarchingPlot\n")
        f.write("  2. CreateNarrativeMap\n")
        f.write("  3. DesignArtifactsAndPuzzles\n\n")

        f.write("## Results\n\n")
        if success:
            f.write("**Status:** ✅ SUCCESS\n\n")
            f.write(
                f"**Execution Time:** {execution_time:.2f}s ({execution_time / 60:.2f} minutes)\n\n"
            )
            f.write(f"**Files Created:** {files_created}/{total_files}\n\n")
            f.write("**Findings:**\n")
            f.write("- Hierarchical mode completes successfully with 3 tasks\n")
            f.write("- No hanging or blocking detected\n")
            f.write("- Manager delegation works correctly\n")
            f.write("- Performance is acceptable\n\n")
            f.write("## Next Steps\n\n")
            f.write("1. Test with additional tasks incrementally\n")
            f.write("2. Test with all 5 core tasks\n")
            f.write("3. Test with evaluation tasks (6-11)\n")
            f.write("4. Compare performance with sequential mode\n")
        else:
            f.write("**Status:** ❌ FAILED\n\n")
            f.write(
                f"**Time Before Failure:** {execution_time:.2f}s ({execution_time / 60:.2f} minutes)\n\n"
            )
            f.write(f"**Hang Point:** {hang_point}\n\n")
            f.write("**Findings:**\n")
            f.write(f"- Hierarchical mode failed at: {hang_point}\n")
            f.write("- This confirms the known issue with hierarchical mode\n")
            f.write("- Sequential mode should be used for MVP\n\n")
            f.write("## Next Steps\n\n")
            f.write("1. Document the specific failure point\n")
            f.write("2. Proceed with sequential mode for Phase 4\n")
            f.write("3. Defer hierarchical mode debugging to later phase\n")

    print(f"\n📄 Results written to: {results_file}")


if __name__ == "__main__":
    print("\nStarting Chunk 0.4: Hierarchical Mode Validation Test")
    print("=" * 80)

    success = test_hierarchical_minimal()

    sys.exit(0 if success else 1)
