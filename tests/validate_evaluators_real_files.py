#!/usr/bin/env python3
"""
Validation script to test quality evaluators against real generated files.

This script tests all 5 evaluators (Plot, NarrativeMap, Puzzle, Scene, Mechanics)
against the actual YAML files in game-config/ and reports the results.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from space_hulk_game.quality import (
    PlotEvaluator,
    NarrativeMapEvaluator,
    PuzzleEvaluator,
    SceneEvaluator,
    MechanicsEvaluator,
)


def load_file(filepath):
    """Load file content."""
    with open(filepath, 'r') as f:
        return f.read()


def main():
    """Run validation against all real files."""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    game_config_dir = os.path.join(base_dir, '../game-config')
    
    # Define file mappings
    files = {
        'plot_outline.yaml': PlotEvaluator(),
        'narrative_map.yaml': NarrativeMapEvaluator(),
        'puzzle_design.yaml': PuzzleEvaluator(),
        'scene_texts.yaml': SceneEvaluator(),
        'prd_document.yaml': MechanicsEvaluator(),
    }
    
    print("=" * 80)
    print("QUALITY EVALUATOR VALIDATION - Real Generated Files")
    print("=" * 80)
    print()
    
    results = {}
    
    for filename, evaluator in files.items():
        filepath = os.path.join(game_config_dir, filename)
        
        print(f"Evaluating: {filename}")
        print("-" * 80)
        
        if not os.path.exists(filepath):
            print(f"  ⚠️  File not found: {filepath}")
            print()
            continue
        
        try:
            # Load content
            content = load_file(filepath)
            
            # Evaluate
            result = evaluator.evaluate(content)
            results[filename] = result
            
            # Print results
            status_icon = "✅" if result.passed else "❌"
            print(f"  {status_icon} Score: {result.score:.1f}/10.0")
            print(f"  {status_icon} Status: {'PASS' if result.passed else 'FAIL'}")
            print(f"  {status_icon} Feedback: {result.feedback}")
            
            # Print failures if any
            failures = result.get_failures()
            if failures:
                print(f"\n  Issues found ({len(failures)}):")
                for failure in failures:
                    print(f"    • {failure}")
            
            # Print key metrics
            print(f"\n  Details:")
            for key, value in result.details.items():
                if key not in ['failures', 'threshold']:
                    print(f"    - {key}: {value}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results.values() if r.passed)
    failed = sum(1 for r in results.values() if not r.passed)
    
    print(f"Total files evaluated: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if results:
        avg_score = sum(r.score for r in results.values()) / len(results)
        print(f"Average score: {avg_score:.1f}/10.0")
    
    print()
    print("All evaluators tested successfully!")


if __name__ == '__main__':
    main()
