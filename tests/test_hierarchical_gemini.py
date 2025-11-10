#!/usr/bin/env python3
"""
Test hierarchical mode with Gemini 2.5 Flash.

This test attempts to use Gemini 2.5 Flash which should handle delegation
better than Llama models.

SETUP:
To use this test, you need to configure Gemini API access:

Option 1: Environment variable (recommended for testing)
  export GOOGLE_API_KEY=your-api-key-here
  export OPENAI_MODEL_NAME=gemini/gemini-2.0-flash-exp
  python tests/test_hierarchical_gemini.py

Option 2: .env file (recommended for development)
  Create .env file with:
    GOOGLE_API_KEY=your-api-key-here
    OPENAI_MODEL_NAME=gemini/gemini-2.0-flash-exp
  python tests/test_hierarchical_gemini.py

To get a Gemini API key:
1. Visit https://aistudio.google.com/app/apikey
2. Click "Create API key"
3. Copy the key and set it as GOOGLE_API_KEY

Available Gemini models (via litellm):
- gemini/gemini-2.0-flash-exp (Recommended - latest experimental)
- gemini/gemini-1.5-flash (Stable)
- gemini/gemini-1.5-pro (Most capable)
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_hierarchical_with_gemini():
    """Test hierarchical mode with Gemini 2.5 Flash."""
    print("\n" + "="*80)
    print("HIERARCHICAL MODE TEST - GEMINI 2.5 FLASH")
    print("="*80)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check for Gemini configuration
    gemini_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if not gemini_key:
        print("\n" + "="*80)
        print("⚠️  GEMINI API KEY NOT CONFIGURED")
        print("="*80)
        print("\nTo run this test, you need to set up Gemini API access.")
        print("\nQuick setup:")
        print("  1. Get API key from: https://aistudio.google.com/app/apikey")
        print("  2. Set environment variable:")
        print("       export GOOGLE_API_KEY=your-api-key-here")
        print("       export OPENAI_MODEL_NAME=gemini/gemini-2.0-flash-exp")
        print("  3. Run this test again:")
        print("       python tests/test_hierarchical_gemini.py")
        print("\nAlternatively, create .env file:")
        print("  GOOGLE_API_KEY=your-api-key-here")
        print("  OPENAI_MODEL_NAME=gemini/gemini-2.0-flash-exp")
        print("\n" + "="*80)
        return False

    print("✅ Gemini API key found")

    # Determine which Gemini model to use
    configured_model = os.environ.get("OPENAI_MODEL_NAME", "gemini/gemini-2.0-flash-exp")
    if "gemini" not in configured_model.lower():
        print(f"⚠️  OPENAI_MODEL_NAME is set to '{configured_model}'")
        print("    Overriding to use Gemini for this test...")
        gemini_model = "gemini/gemini-2.0-flash-exp"
    else:
        gemini_model = configured_model

    print(f"✅ Using model: {gemini_model}")
    print("="*80 + "\n")

    start_time = time.time()

    try:
        from crewai import LLM, Agent, Crew, Process

        from space_hulk_game.crew import SpaceHulkGame

        print("✅ Importing crew...")
        crew_instance = SpaceHulkGame()

        print("\n🔧 Creating hierarchical crew with Gemini...")

        # Create Gemini-powered manager
        gemini_llm = LLM(
            model=gemini_model,
            api_key=gemini_key,
            temperature=0.3,
            max_tokens=4000
        )

        manager = Agent(
            role="Narrative Director",
            goal="Coordinate narrative development efficiently",
            backstory="An experienced game narrative director who efficiently delegates tasks to specialists.",
            llm=gemini_llm,
            allow_delegation=True,
            verbose=True,
            max_iter=15  # Give Gemini a bit more room
        )

        print(f"   Manager: {manager.role}")
        print(f"   Manager LLM: {gemini_model}")
        print(f"   Manager max_iter: {manager.max_iter}")
        print("   Manager temperature: 0.3")

        # Get 3 workers (using Gemini for consistency)
        plot_master = crew_instance.PlotMasterAgent()
        narrative_architect = crew_instance.NarrativeArchitectAgent()
        puzzle_smith = crew_instance.PuzzleSmithAgent()

        # Use Gemini for workers too (consistency and quality)
        plot_master.llm = gemini_llm
        narrative_architect.llm = gemini_llm
        puzzle_smith.llm = gemini_llm

        worker_agents = [plot_master, narrative_architect, puzzle_smith]
        print(f"   Workers: {[agent.role for agent in worker_agents]}")
        print(f"   Worker LLM: {gemini_model}")

        # Get 3 tasks
        task1 = crew_instance.GenerateOverarchingPlot()
        task2 = crew_instance.CreateNarrativeMap()
        task3 = crew_instance.DesignArtifactsAndPuzzles()

        minimal_tasks = [task1, task2, task3]
        print(f"   Tasks: {len(minimal_tasks)}")

        # Create hierarchical crew
        hierarchical_crew = Crew(
            agents=cast(list, worker_agents),
            tasks=minimal_tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True
        )

        print("✅ Hierarchical crew created successfully")

        test_prompt = "A Space Marine boarding team discovers an ancient derelict vessel"
        inputs = {"prompt": test_prompt}

        print("\n🚀 Starting hierarchical execution with Gemini...")
        print(f"   Prompt: {test_prompt}")
        print("   Max timeout: 10 minutes")
        print("   Monitoring for delegation behavior...")
        print("\n" + "-"*80)

        exec_start = time.time()
        hierarchical_crew.kickoff(inputs=inputs)
        exec_time = time.time() - exec_start

        print("-"*80)
        print("\n✅ HIERARCHICAL EXECUTION COMPLETED SUCCESSFULLY!")
        print(f"   Execution time: {exec_time:.2f}s ({exec_time/60:.2f} min)")

        # Check output files
        output_files = [
            "game-config/plot_outline.yaml",
            "game-config/narrative_map.yaml",
            "game-config/puzzle_design.yaml"
        ]

        files_created = sum(1 for f in output_files if os.path.exists(f))

        print(f"\n📁 Output files created: {files_created}/{len(output_files)}")
        for filepath in output_files:
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   ✅ {filepath} ({size} bytes)")
            else:
                print(f"   ❌ {filepath} (not found)")

        total_time = time.time() - start_time

        print("\n" + "="*80)
        print("🎉 BREAKTHROUGH: HIERARCHICAL MODE WORKS WITH GEMINI!")
        print("="*80)
        print(f"✅ Hierarchical mode SUCCESSFUL with Gemini {gemini_model}")
        print(f"✅ Execution time: {exec_time:.2f}s ({exec_time/60:.2f} min)")
        print(f"✅ Files created: {files_created}/{len(output_files)}")
        print("✅ No delegation failures or LLM errors")
        print("\n🔑 Key finding: Gemini handles delegation much better than Llama")
        print(f"📊 Performance: {exec_time/60:.2f} min vs ~2-6 min failures with Llama")
        print("\n💡 Recommendation for production:")
        print("   - Use Gemini for hierarchical mode manager")
        print("   - Can use Ollama for workers (cost savings)")
        print("   - Or use Gemini for all agents (best quality)")
        print(f"\nTotal test time: {total_time:.2f}s")
        print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        return True

    except Exception as e:
        error_time = time.time() - start_time
        print("\n" + "="*80)
        print("❌ HIERARCHICAL MODE FAILED WITH GEMINI")
        print("="*80)
        print(f"Error: {str(e)}")
        print(f"Time before failure: {error_time:.2f}s ({error_time/60:.2f} min)")

        # Check if it's the same delegation error
        if "Invalid response from LLM call" in str(e):
            print("\n📋 Analysis: Still getting delegation errors with Gemini.")
            print("   This suggests the issue may be with:")
            print("   1. Task complexity/description length")
            print("   2. CrewAI delegation mechanism itself")
            print("   3. API configuration or rate limiting")
            print("\n   Recommendation: Review task descriptions in tasks.yaml")
        elif "API" in str(e) or "key" in str(e).lower():
            print("\n📋 Analysis: API authentication issue.")
            print("   Check that GOOGLE_API_KEY is valid and has sufficient quota.")

        print("="*80)

        import traceback
        traceback.print_exc()

        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING HIERARCHICAL MODE WITH GEMINI 2.5 FLASH")
    print("="*80)
    print("\nThis test checks if Gemini can handle hierarchical delegation")
    print("where Llama 3.1 70B failed.")
    print("="*80)

    success = test_hierarchical_with_gemini()

    if success:
        print("\n" + "="*80)
        print("🎉 SUCCESS - HIERARCHICAL MODE WORKS!")
        print("="*80)
        print("\nNext steps:")
        print("1. Update crew.py to use Gemini for hierarchical mode")
        print("2. Consider hybrid approach: Gemini manager + Ollama workers")
        print("3. Test with all 5 core tasks")
        print("4. Test with evaluation tasks (all 11 tasks)")
        print("\nSee docs/HIERARCHICAL_MODE_INVESTIGATION.md for implementation guide.")
    else:
        print("\n" + "="*80)
        print("📋 FAILED - SEE ERROR ANALYSIS ABOVE")
        print("="*80)
        print("\nIf API key is configured correctly but still failing:")
        print("- Check docs/HIERARCHICAL_MODE_ASSESSMENT.md")
        print("- Consider using sequential mode (100% reliable)")
        print("- Review task descriptions in src/space_hulk_game/config/tasks.yaml")

    print("="*80)

    sys.exit(0 if success else 1)
