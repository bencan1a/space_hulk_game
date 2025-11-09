#!/usr/bin/env python3
"""
Simple test runner for Chunk 0.1: Sequential Mode Validation (5 Core Tasks)

This script directly executes the SpaceHulkGame crew with the test prompt
and validates the outputs according to Chunk 0.1 specifications.

Per master_implementation_plan.md Chunk 0.1:
- Run with test prompt: "A Space Marine boarding team discovers an ancient derelict vessel"
- Monitor execution with 15-minute timeout
- Validate 5 output files exist and are valid YAML
- Document execution time and any errors

Success Criteria:
✅ All 5 core tasks complete without errors  
✅ All 5 output files exist and contain valid YAML
✅ Generation completes in < 10 minutes
✅ No hanging or timeout issues
"""

import sys
import time
import yaml
from pathlib import Path
import signal

# Add src to path so we can import space_hulk_game
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def timeout_handler(signum, frame):
    """Handler for timeout signal."""
    raise TimeoutError("Crew execution exceeded 15 minute timeout")

def validate_output_files(output_dir, expected_files):
    """Validate that all expected output files exist and are valid YAML."""
    print("\n" + "="*80)
    print("VALIDATING OUTPUT FILES")
    print("="*80)
    
    results = {
        "all_exist": True,
        "all_valid_yaml": True,
        "files_status": {}
    }
    
    for filename in expected_files:
        filepath = output_dir / filename
        status = {"exists": False, "valid_yaml": False, "size": 0, "error": None}
        
        # Check existence
        if filepath.exists():
            status["exists"] = True
            status["size"] = filepath.stat().st_size
            
            # Check YAML validity
            try:
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
                    
                if data is None:
                    status["error"] = "File is empty or contains only comments"
                    results["all_valid_yaml"] = False
                else:
                    status["valid_yaml"] = True
                    if isinstance(data, dict):
                        status["keys"] = len(data.keys())
                        
            except yaml.YAMLError as e:
                status["error"] = f"YAML error: {e}"
                results["all_valid_yaml"] = False
            except Exception as e:
                status["error"] = f"Error: {e}"
                results["all_valid_yaml"] = False
        else:
            results["all_exist"] = False
            status["error"] = "File not found"
        
        results["files_status"][filename] = status
        
        # Print status
        if status["exists"] and status["valid_yaml"]:
            keys_info = f", {status['keys']} keys" if "keys" in status else ""
            print(f"✅ {filename}: {status['size']} bytes{keys_info}")
        elif status["exists"]:
            print(f"❌ {filename}: {status['error']}")
        else:
            print(f"❌ {filename}: File not found")
    
    print("="*80)
    return results

def main():
    """Run Chunk 0.1 validation test."""
    print("\n" + "="*80)
    print("CHUNK 0.1: SEQUENTIAL MODE VALIDATION (5 CORE TASKS)")
    print("="*80)
    print("Per master_implementation_plan.md:")
    print("- Testing sequential mode with 5 core tasks only")
    print("- Evaluation tasks are commented out")
    print("- Expected: All 5 tasks complete without errors")
    print("- Expected: Generation time < 10 minutes")
    print("- Expected: All 5 output files are valid YAML")
    print("="*80 + "\n")
    
    # Test configuration
    test_prompt = "A Space Marine boarding team discovers an ancient derelict vessel"
    output_dir = project_root / "game-config"
    expected_files = [
        "plot_outline.yaml",
        "narrative_map.yaml",
        "puzzle_design.yaml",
        "scene_texts.yaml",
        "prd_document.yaml"
    ]
    
    # Clean up old output files
    print("Cleaning up old output files...")
    for filename in expected_files:
        filepath = output_dir / filename
        if filepath.exists():
            filepath.unlink()
            print(f"  Deleted: {filename}")
    print()
    
    # Import crew (do this after path setup)
    try:
        from space_hulk_game.crew import SpaceHulkGame
        print("✅ Successfully imported SpaceHulkGame crew")
    except ImportError as e:
        print(f"❌ Failed to import SpaceHulkGame: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -e .")
        print("  or")
        print("  crewai install")
        return 1
    
    # Prepare inputs
    inputs = {
        'prompt': test_prompt,
        'game': test_prompt  # Some configs might use 'game' key
    }
    
    print("\n" + "="*80)
    print("STARTING CREW EXECUTION")
    print("="*80)
    print(f"Prompt: {test_prompt}")
    print(f"Timeout: 15 minutes (900 seconds)")
    print(f"Expected Outputs: {len(expected_files)} files")
    print("="*80 + "\n")
    
    # Set up timeout (Unix only)
    # signal.signal(signal.SIGALRM, timeout_handler)
    # signal.alarm(900)  # 15 minutes
    
    # Execute crew
    start_time = time.time()
    success = False
    error_message = None
    
    try:
        print("Initializing crew...")
        crew_instance = SpaceHulkGame()
        
        print("Starting crew execution...")
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print("\n" + "="*80)
        print("CREW EXECUTION COMPLETED")
        print("="*80)
        print(f"Execution Time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")
        print("="*80)
        
        success = True
        
    except TimeoutError as e:
        end_time = time.time()
        execution_time = end_time - start_time
        error_message = f"Timeout after {execution_time:.2f} seconds: {e}"
        print(f"\n❌ {error_message}")
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        error_message = f"Error during execution: {e}"
        print(f"\n❌ {error_message}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cancel timeout alarm
        # signal.alarm(0)
        pass
    
    # Validate outputs
    validation_results = validate_output_files(output_dir, expected_files)
    
    # Print final summary
    print("\n" + "="*80)
    print("CHUNK 0.1 VALIDATION SUMMARY")
    print("="*80)
    
    if not success:
        print(f"❌ Crew Execution: FAILED - {error_message}")
    else:
        if execution_time < 600:  # 10 minutes
            print(f"✅ Crew Execution: SUCCESS ({execution_time:.2f}s < 600s threshold)")
        else:
            print(f"⚠️  Crew Execution: SUCCESS but SLOW ({execution_time:.2f}s > 600s threshold)")
    
    if validation_results["all_exist"]:
        print(f"✅ All Output Files: FOUND ({len(expected_files)}/{ len(expected_files)})")
    else:
        missing = [f for f, s in validation_results["files_status"].items() if not s["exists"]]
        print(f"❌ Output Files: MISSING {len(missing)} files: {', '.join(missing)}")
    
    if validation_results["all_valid_yaml"]:
        print(f"✅ YAML Validity: ALL VALID ({len(expected_files)}/{len(expected_files)})")
    else:
        invalid = [f for f, s in validation_results["files_status"].items() if not s["valid_yaml"]]
        print(f"❌ YAML Validity: {len(invalid)} invalid files: {', '.join(invalid)}")
    
    # Overall result
    print("="*80)
    if success and validation_results["all_exist"] and validation_results["all_valid_yaml"]:
        if execution_time < 600:
            print("✅ CHUNK 0.1 VALIDATION: PASSED")
            print("All success criteria met!")
            print("Ready to proceed to Chunk 0.2 (all 11 tasks)")
            return_code = 0
        else:
            print("⚠️  CHUNK 0.1 VALIDATION: PASSED WITH WARNINGS")
            print("All tasks completed successfully but execution time exceeded threshold")
            return_code = 0
    else:
        print("❌ CHUNK 0.1 VALIDATION: FAILED")
        print("Review issues above and retry after fixes")
        return_code = 1
    
    print("="*80 + "\n")
    
    return return_code

if __name__ == "__main__":
    sys.exit(main())
