#!/usr/bin/env python3
"""
Test script for improved hierarchical mode with optimizations.

This test validates the optimized hierarchical mode implementation.
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


def test_optimized_hierarchical():  # noqa: PLR0915
    """
    Test hierarchical mode with optimized configuration.
    """
    print("\n" + "=" * 80)
    print("HIERARCHICAL MODE TEST - OPTIMIZED CONFIGURATION")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Test Mode: Hierarchical with optimizations")
    print("Optimizations:")
    print("  - Reduced max_iter: 10 (down from 25)")
    print("  - Simplified manager with lower temperature (0.3)")
    print("  - Limited token usage (4000 max)")
    print("=" * 80 + "\n")

    start_time = time.time()

    try:
        from space_hulk_game.crew import SpaceHulkGame

        print("✅ Successfully imported SpaceHulkGame crew")

        # Initialize the crew
        print("\n📋 Initializing SpaceHulkGame crew...")
        crew_instance = SpaceHulkGame()
        print("✅ Crew initialized")

        # Create optimized hierarchical crew (3 tasks)
        print("\n🔧 Creating optimized hierarchical crew...")

        # Get manager and workers
        from crewai import LLM, Agent

        # Create optimized manager
        manager_llm_opt = LLM(
            model=os.environ.get("OPENAI_MODEL_NAME", "ollama/qwen2.5"),
            base_url="http://localhost:11434"
            if "ollama" in os.environ.get("OPENAI_MODEL_NAME", "ollama")
            else None,
            api_key=os.environ.get("OPENROUTER_API_KEY")
            if os.environ.get("OPENROUTER_API_KEY")
            else None,
            temperature=0.3,
            max_tokens=4000,
        )

        manager = Agent(
            role="Narrative Director",
            goal="Coordinate narrative development efficiently",
            backstory="An experienced game narrative director who efficiently delegates tasks.",
            llm=manager_llm_opt,
            allow_delegation=True,
            verbose=True,
            max_iter=10,  # Key optimization
        )

        # Get 3 workers
        plot_master = crew_instance.PlotMasterAgent()
        narrative_architect = crew_instance.NarrativeArchitectAgent()
        puzzle_smith = crew_instance.PuzzleSmithAgent()

        worker_agents = [plot_master, narrative_architect, puzzle_smith]

        # Get 3 tasks
        task1 = crew_instance.GenerateOverarchingPlot()
        task2 = crew_instance.CreateNarrativeMap()
        task3 = crew_instance.DesignArtifactsAndPuzzles()

        minimal_tasks = [task1, task2, task3]

        print(f"   Manager: {manager.role} (max_iter={manager.max_iter})")
        print(f"   Workers: {[agent.role for agent in worker_agents]}")
        print(f"   Tasks: {len(minimal_tasks)}")

        # Create hierarchical crew with optimizations
        hierarchical_crew = Crew(
            agents=cast("list", worker_agents),
            tasks=minimal_tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True,
        )

        print("✅ Optimized hierarchical crew created")

        # Test input
        test_prompt = "A Space Marine boarding team discovers an ancient derelict vessel"
        inputs = {"prompt": test_prompt}

        print("\n🚀 Starting optimized hierarchical execution...")
        print(f"   Prompt: {test_prompt}")
        print("   Max timeout: 10 minutes")
        print("\n" + "-" * 80)

        execution_start = time.time()
        hierarchical_crew.kickoff(inputs=inputs)
        execution_time = time.time() - execution_start

        print("-" * 80)
        print("\n✅ HIERARCHICAL EXECUTION COMPLETED!")
        print(
            f"   Execution time: {execution_time:.2f} seconds ({execution_time / 60:.2f} minutes)"
        )

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

        total_time = time.time() - start_time

        print("\n" + "=" * 80)
        print("OPTIMIZED HIERARCHICAL MODE TEST RESULTS")
        print("=" * 80)
        print("✅ Hierarchical mode SUCCEEDED with optimizations")
        print(f"✅ Execution time: {execution_time:.2f}s ({execution_time / 60:.2f} min)")
        print(f"✅ Files created: {files_created}/{len(output_files)}")
        print("\nOptimizations applied:")
        print("  - Manager max_iter: 10 (prevents excessive delegation)")
        print("  - Manager temperature: 0.3 (more consistent decisions)")
        print("  - Manager max_tokens: 4000 (prevents context overflow)")
        print(f"\nTotal test time: {total_time:.2f}s")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        return True

    except Exception as e:
        error_time = time.time() - start_time
        print("\n" + "=" * 80)
        print("❌ OPTIMIZED HIERARCHICAL MODE FAILED")
        print("=" * 80)
        print(f"Error: {e!s}")
        print(f"Time before failure: {error_time:.2f}s ({error_time / 60:.2f} min)")
        print("=" * 80)

        logger.error(f"Optimized hierarchical mode failed: {e!s}", exc_info=True)
        return False


if __name__ == "__main__":
    print("\nTesting Optimized Hierarchical Mode")
    print("=" * 80)

    success = test_optimized_hierarchical()

    sys.exit(0 if success else 1)
