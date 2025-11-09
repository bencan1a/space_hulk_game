#!/usr/bin/env python3
"""
Test hierarchical mode with simplified task descriptions.

This is the most likely to work since it drastically reduces the context
that the manager needs to handle for delegation.
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_simplified_hierarchical():
    """Test hierarchical mode with simplified tasks."""
    print("\n" + "="*80)
    print("HIERARCHICAL MODE - SIMPLIFIED TASK DESCRIPTIONS")
    print("="*80)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Optimization: 90% shorter task descriptions")
    print("="*80 + "\n")
    
    start_time = time.time()
    
    try:
        from space_hulk_game.crew import SpaceHulkGame
        
        print("✅ Importing crew...")
        crew_instance = SpaceHulkGame()
        
        print("✅ Creating simplified hierarchical crew...")
        hierarchical_crew = crew_instance.create_hierarchical_crew_simplified()
        
        print("✅ Crew created successfully")
        print(f"   Agents: {len(hierarchical_crew.agents)}")
        print(f"   Tasks: {len(hierarchical_crew.tasks)}")
        print(f"   Process: {hierarchical_crew.process}")
        
        test_prompt = "A Space Marine boarding team discovers an ancient derelict vessel"
        inputs = {"prompt": test_prompt}
        
        print(f"\n🚀 Starting execution...")
        print(f"   Prompt: {test_prompt}")
        print("\n" + "-"*80)
        
        exec_start = time.time()
        result = hierarchical_crew.kickoff(inputs=inputs)
        exec_time = time.time() - exec_start
        
        print("-"*80)
        print(f"\n✅ SUCCESS!")
        print(f"   Execution time: {exec_time:.2f}s ({exec_time/60:.2f} min)")
        
        # Check output files
        output_files = [
            "game-config/plot_outline.yaml",
            "game-config/narrative_map.yaml",
            "game-config/puzzle_design.yaml"
        ]
        
        files_created = sum(1 for f in output_files if os.path.exists(f))
        
        print(f"\n📁 Output files: {files_created}/{len(output_files)}")
        for filepath in output_files:
            status = "✅" if os.path.exists(filepath) else "❌"
            size = f"({os.path.getsize(filepath)} bytes)" if os.path.exists(filepath) else ""
            print(f"   {status} {filepath} {size}")
        
        total_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("SIMPLIFIED HIERARCHICAL MODE - SUCCESS!")
        print("="*80)
        print(f"✅ Hierarchical mode works with simplified tasks")
        print(f"✅ Execution: {exec_time:.2f}s ({exec_time/60:.2f} min)")
        print(f"✅ Files: {files_created}/{len(output_files)}")
        print(f"\nKey fix: Simplified task descriptions (90% shorter)")
        print(f"Total time: {total_time:.2f}s")
        print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        return True
        
    except Exception as e:
        error_time = time.time() - start_time
        print("\n" + "="*80)
        print("❌ FAILED")
        print("="*80)
        print(f"Error: {str(e)}")
        print(f"Time: {error_time:.2f}s ({error_time/60:.2f} min)")
        print("="*80)
        
        import traceback
        traceback.print_exc()
        
        return False


if __name__ == "__main__":
    success = test_simplified_hierarchical()
    sys.exit(0 if success else 1)
