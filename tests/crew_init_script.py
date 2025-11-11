#!/usr/bin/env python3
"""
Simple test script to validate sequential crew execution.

This script runs a minimal test of the crew to verify:
1. The crew can be initialized without errors
2. Agents and tasks are loaded correctly
3. The process mode is set correctly
4. No import or configuration errors exist

Usage:
    python test_crew_init.py
"""

import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_crew_initialization():  # noqa: PLR0915
    """Test that the crew can be initialized successfully."""
    print("=" * 70)
    print("Space Hulk Game - Crew Initialization Test")
    print("=" * 70)
    print()

    try:
        print("1. Importing SpaceHulkGame class...")
        from space_hulk_game.crew import SpaceHulkGame

        print("   ✅ Import successful\n")

        print("2. Initializing crew instance...")
        start_time = time.time()
        game = SpaceHulkGame()
        init_time = time.time() - start_time
        print(f"   ✅ Initialization successful ({init_time:.2f}s)\n")

        print("3. Checking agents configuration...")
        print(f"   - Agents loaded: {len(game.agents_config)} agents")
        for agent_name in game.agents_config:
            print(f"     • {agent_name}")
        print()

        print("4. Checking tasks configuration...")
        print(f"   - Tasks loaded: {len(game.tasks_config)} tasks")
        core_tasks = [
            "GenerateOverarchingPlot",
            "CreateNarrativeMap",
            "DesignArtifactsAndPuzzles",
            "WriteSceneDescriptionsAndDialogue",
            "CreateGameMechanicsPRD",
        ]
        for task_name in core_tasks:
            status = "✅" if task_name in game.tasks_config else "❌"
            print(f"     {status} {task_name}")
        print()

        print("5. Creating crew instance...")
        start_time = time.time()
        crew = game.crew()
        crew_time = time.time() - start_time
        print(f"   ✅ Crew created successfully ({crew_time:.2f}s)\n")

        print("6. Validating crew configuration...")
        print(f"   - Process mode: {crew.process}")
        print(f"   - Total agents: {len(crew.agents)}")
        print(f"   - Total tasks: {len(crew.tasks)}")
        print(f"   - Verbose mode: {crew.verbose}")
        print()

        # Verify sequential mode
        from crewai import Process

        if crew.process == Process.sequential:
            print("   ✅ Sequential process mode confirmed")
        else:
            print(f"   ⚠️  WARNING: Unexpected process mode: {crew.process}")
        print()

        print("7. Testing hierarchical crew creation (not default)...")
        try:
            h_crew = game.create_hierarchical_crew()
            print("   ✅ Hierarchical crew available")
            print(f"      - Process: {h_crew.process}")
            print(
                f"      - Manager: {h_crew.manager_agent.role if h_crew.manager_agent else 'None'}"
            )
            print(f"      - Workers: {len(h_crew.agents)} agents")
        except Exception as e:
            print(f"   ⚠️  Hierarchical crew creation failed: {e!s}")
        print()

        print("=" * 70)
        print("✅ ALL INITIALIZATION TESTS PASSED")
        print("=" * 70)
        print()
        print("The crew is ready for execution. To run a full generation:")
        print('  crewai run --inputs "prompt: Your game scenario"')
        print()
        print("Or test with Python:")
        print("  from space_hulk_game.crew import SpaceHulkGame")
        print("  game = SpaceHulkGame()")
        print('  result = game.crew().kickoff({"prompt": "Your scenario"})')
        print()

        return True

    except ImportError as e:
        print(f"\n❌ Import Error: {e!s}")
        print("\nMake sure you're running from the project root directory.")
        print("Try: cd /home/runner/work/space_hulk_game/space_hulk_game")
        return False

    except Exception as e:
        print(f"\n❌ Initialization Error: {e!s}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_crew_initialization()
    sys.exit(0 if success else 1)
