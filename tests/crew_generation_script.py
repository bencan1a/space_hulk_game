#!/usr/bin/env python3
"""
Crew Validation Test Script

This script tests the Space Hulk Game crew to identify and debug issues
with agent coordination and task execution.

Usage:
    python test_crew_generation.py [--mode sequential|hierarchical] [--timeout 600]
"""

import sys
import os
import argparse
import time
import signal
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from space_hulk_game.crew import SpaceHulkGame


class TimeoutError(Exception):
    """Raised when operation times out"""
    pass


def timeout_handler(signum, frame):
    """Handle timeout signal"""
    raise TimeoutError("Operation timed out")


def test_sequential_generation(timeout_seconds=600):
    """
    Test crew in sequential mode (simplest configuration)
    
    Args:
        timeout_seconds: Maximum time to wait for completion
        
    Returns:
        dict: Test results
    """
    print("=" * 80)
    print("TEST 1: SEQUENTIAL MODE")
    print("=" * 80)
    print(f"Timeout: {timeout_seconds} seconds ({timeout_seconds/60:.1f} minutes)")
    print()
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    results = {
        'mode': 'sequential',
        'success': False,
        'duration': None,
        'outputs_generated': [],
        'errors': [],
        'timeout': False
    }
    
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Initializing crew...")
        game = SpaceHulkGame()
        
        # Modify to use sequential (we'll need to change crew.py temporarily)
        print("[WARNING] This test requires crew.py to use Process.sequential")
        print("[WARNING] Please modify crew.py before running this test")
        print()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting generation...")
        print("Prompt: 'A simple space exploration scenario with limited scope'")
        print()
        
        start_time = time.time()
        
        result = game.crew().kickoff(
            inputs={"prompt": "A simple space exploration scenario with limited scope"}
        )
        
        duration = time.time() - start_time
        results['duration'] = duration
        
        print()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Generation completed!")
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print()
        
        # Check outputs
        output_files = [
            'plot_outline.yaml',
            'narrative_map.yaml',
            'puzzle_design.yaml',
            'scene_texts.yaml',
            'prd_document.yaml'
        ]
        
        print("Checking generated files:")
        for filename in output_files:
            exists = os.path.exists(filename)
            status = "✓" if exists else "✗"
            print(f"  {status} {filename}")
            if exists:
                results['outputs_generated'].append(filename)
                # Check file size
                size = os.path.getsize(filename)
                print(f"     Size: {size} bytes")
        
        print()
        
        if result:
            print("Result preview:")
            print("-" * 40)
            result_str = str(result)
            print(result_str[:500] + "..." if len(result_str) > 500 else result_str)
            print("-" * 40)
        
        results['success'] = True
        
    except TimeoutError:
        print()
        print(f"✗ TEST FAILED: Timed out after {timeout_seconds} seconds")
        results['timeout'] = True
        results['errors'].append(f"Timeout after {timeout_seconds}s")
        
    except Exception as e:
        print()
        print(f"✗ TEST FAILED: {str(e)}")
        results['errors'].append(str(e))
        import traceback
        traceback.print_exc()
        
    finally:
        # Cancel alarm
        signal.alarm(0)
    
    return results


def test_hierarchical_generation(timeout_seconds=600):
    """
    Test crew in hierarchical mode (current configuration)
    
    Args:
        timeout_seconds: Maximum time to wait for completion
        
    Returns:
        dict: Test results
    """
    print("=" * 80)
    print("TEST 2: HIERARCHICAL MODE")
    print("=" * 80)
    print(f"Timeout: {timeout_seconds} seconds ({timeout_seconds/60:.1f} minutes)")
    print()
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    results = {
        'mode': 'hierarchical',
        'success': False,
        'duration': None,
        'outputs_generated': [],
        'errors': [],
        'timeout': False
    }
    
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Initializing crew...")
        game = SpaceHulkGame()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting generation...")
        print("Prompt: 'A simple space exploration scenario with limited scope'")
        print()
        print("NOTE: Watch for where the process hangs...")
        print("      Press Ctrl+C if it becomes unresponsive")
        print()
        
        start_time = time.time()
        
        result = game.crew().kickoff(
            inputs={"prompt": "A simple space exploration scenario with limited scope"}
        )
        
        duration = time.time() - start_time
        results['duration'] = duration
        
        print()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Generation completed!")
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print()
        
        # Check outputs
        output_files = [
            'plot_outline.yaml',
            'narrative_map.yaml',
            'puzzle_design.yaml',
            'scene_texts.yaml',
            'prd_document.yaml'
        ]
        
        print("Checking generated files:")
        for filename in output_files:
            exists = os.path.exists(filename)
            status = "✓" if exists else "✗"
            print(f"  {status} {filename}")
            if exists:
                results['outputs_generated'].append(filename)
                # Check file size
                size = os.path.getsize(filename)
                print(f"     Size: {size} bytes")
        
        print()
        
        if result:
            print("Result preview:")
            print("-" * 40)
            result_str = str(result)
            print(result_str[:500] + "..." if len(result_str) > 500 else result_str)
            print("-" * 40)
        
        results['success'] = True
        
    except TimeoutError:
        print()
        print(f"✗ TEST FAILED: Timed out after {timeout_seconds} seconds")
        print()
        print("DIAGNOSIS: The crew appears to be hanging in hierarchical mode.")
        print("This confirms the reported issue with agent coordination.")
        results['timeout'] = True
        results['errors'].append(f"Timeout after {timeout_seconds}s")
        
    except KeyboardInterrupt:
        print()
        print("✗ TEST INTERRUPTED: User stopped test (Ctrl+C)")
        print()
        print("DIAGNOSIS: The crew was not making progress.")
        results['errors'].append("User interrupted - crew appeared stuck")
        
    except Exception as e:
        print()
        print(f"✗ TEST FAILED: {str(e)}")
        results['errors'].append(str(e))
        import traceback
        traceback.print_exc()
        
    finally:
        # Cancel alarm
        signal.alarm(0)
    
    return results


def print_summary(results_list):
    """Print summary of all tests"""
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    for results in results_list:
        mode = results['mode'].upper()
        success = "✓ PASSED" if results['success'] else "✗ FAILED"
        
        print(f"{mode} Mode: {success}")
        
        if results['duration']:
            print(f"  Duration: {results['duration']:.1f}s ({results['duration']/60:.1f}m)")
        
        if results['outputs_generated']:
            print(f"  Outputs: {len(results['outputs_generated'])}/5 files")
        
        if results['timeout']:
            print(f"  Issue: Timed out (crew likely hanging)")
        
        if results['errors']:
            print(f"  Errors: {', '.join(results['errors'])}")
        
        print()
    
    # Recommendations
    print("RECOMMENDATIONS:")
    print()
    
    all_failed = all(not r['success'] for r in results_list)
    sequential_passed = any(r['mode'] == 'sequential' and r['success'] for r in results_list)
    hierarchical_failed = any(r['mode'] == 'hierarchical' and not r['success'] for r in results_list)
    
    if all_failed:
        print("❌ Both modes failed. Issues to investigate:")
        print("   1. Check Ollama is running: ollama list")
        print("   2. Check model is available: ollama pull qwen2.5")
        print("   3. Check .env configuration")
        print("   4. Check for Python errors in logs")
        print("   5. Try with a cloud LLM to rule out Ollama issues")
        
    elif sequential_passed and hierarchical_failed:
        print("⚠️  Sequential works but Hierarchical hangs. Root cause likely:")
        print("   1. Manager agent (NarrativeDirector) delegation issues")
        print("   2. Task dependency deadlocks in hierarchical mode")
        print("   3. Evaluation tasks creating circular waits")
        print()
        print("   SOLUTION OPTIONS:")
        print("   A. Use sequential mode for now (proven to work)")
        print("   B. Simplify hierarchical: remove evaluation tasks")
        print("   C. Debug manager agent with detailed logging")
        print("   D. Try different manager LLM configuration")
        
    else:
        print("✅ Crew is working! Ready to proceed with:")
        print("   1. Add output validation")
        print("   2. Add quality metrics")
        print("   3. Build game engine")
    
    print()


def main():
    parser = argparse.ArgumentParser(description='Test Space Hulk Game crew generation')
    parser.add_argument(
        '--mode',
        choices=['sequential', 'hierarchical', 'both'],
        default='both',
        help='Which mode to test'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=600,
        help='Timeout in seconds (default: 600 = 10 minutes)'
    )
    
    args = parser.parse_args()
    
    print()
    print("SPACE HULK GAME - CREW VALIDATION TEST")
    print("=" * 80)
    print()
    print("This script tests whether the multi-agent crew can successfully")
    print("generate game content without hanging or timing out.")
    print()
    
    results = []
    
    if args.mode in ['sequential', 'both']:
        print("NOTE: Sequential test requires modifying crew.py to use Process.sequential")
        print("      Skip this test if you haven't made that change yet.")
        response = input("Run sequential test? (y/n): ")
        if response.lower() == 'y':
            results.append(test_sequential_generation(args.timeout))
        print()
    
    if args.mode in ['hierarchical', 'both']:
        response = input("Run hierarchical test? (y/n): ")
        if response.lower() == 'y':
            results.append(test_hierarchical_generation(args.timeout))
        print()
    
    if results:
        print_summary(results)
    else:
        print("No tests were run.")
    
    # Exit with error code if any tests failed
    if any(not r['success'] for r in results):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
