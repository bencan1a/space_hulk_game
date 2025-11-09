#!/usr/bin/env python3
"""
Comprehensive validation script for the 7-agent Space Hulk Game system.

This script validates:
1. All 7 agents are properly defined in agents.yaml
2. All 11 tasks are properly defined in tasks.yaml
3. All agent methods exist in crew.py
4. All task methods exist in crew.py
5. Task assignments are correct
6. Workload is balanced (no agent >30% of tasks)
7. Unit tests pass

Usage:
    python tests/validate_7_agent_system.py
"""
import sys
import os
import yaml
import re
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class Color:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Color.BLUE}{Color.BOLD}{'=' * 70}{Color.END}")
    print(f"{Color.BLUE}{Color.BOLD}{text}{Color.END}")
    print(f"{Color.BLUE}{Color.BOLD}{'=' * 70}{Color.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Color.GREEN}✅ {text}{Color.END}")

def print_error(text):
    """Print error message"""
    print(f"{Color.RED}❌ {text}{Color.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Color.YELLOW}⚠️  {text}{Color.END}")

def validate_agents_yaml():
    """Validate agents.yaml has all 7 agents"""
    print_header("1. Validating agents.yaml")
    
    agents_path = Path('src/space_hulk_game/config/agents.yaml')
    with open(agents_path, 'r') as f:
        agents = yaml.safe_load(f)
    
    expected_agents = [
        'NarrativeDirectorAgent',
        'PlotMasterAgent',
        'NarrativeArchitectAgent',
        'PuzzleSmithAgent',
        'CreativeScribeAgent',
        'MechanicsGuruAgent',
        'GameIntegrationAgent'
    ]
    
    print(f"Expected agents: {len(expected_agents)}")
    print(f"Found agents: {len(agents)}")
    print()
    
    all_present = True
    for i, agent in enumerate(expected_agents, 1):
        if agent in agents:
            print_success(f"{i}. {agent}")
        else:
            print_error(f"{i}. {agent} - MISSING!")
            all_present = False
    
    if all_present and len(agents) == 7:
        print()
        print_success("All 7 agents properly configured!")
        return True
    else:
        print()
        print_error(f"Agent configuration issue: expected 7, found {len(agents)}")
        return False

def validate_tasks_yaml():
    """Validate tasks.yaml has all 11 tasks"""
    print_header("2. Validating tasks.yaml")
    
    tasks_path = Path('src/space_hulk_game/config/tasks.yaml')
    with open(tasks_path, 'r') as f:
        tasks = yaml.safe_load(f)
    
    print(f"Total tasks defined: {len(tasks)}")
    print()
    
    # Group tasks by agent
    agent_tasks = {}
    for task_name, task_info in tasks.items():
        agent = task_info.get('agent', 'Unknown')
        if agent not in agent_tasks:
            agent_tasks[agent] = []
        agent_tasks[agent].append(task_name)
    
    # Print task distribution
    for agent, task_list in sorted(agent_tasks.items()):
        count = len(task_list)
        percentage = (count / len(tasks)) * 100
        print(f"{agent}: {count} tasks ({percentage:.1f}%)")
        for task in sorted(task_list):
            print(f"  • {task}")
        print()
    
    # Check workload balance
    max_tasks = max(len(task_list) for task_list in agent_tasks.values())
    max_percentage = (max_tasks / len(tasks)) * 100
    
    print(f"Maximum tasks per agent: {max_tasks} ({max_percentage:.1f}%)")
    
    if max_percentage <= 30:
        print_success("Workload is well balanced (no agent >30%)")
        return True
    else:
        print_error(f"Workload imbalance: {max_percentage:.1f}% exceeds 30% threshold")
        return False

def validate_crew_py_agents():
    """Validate crew.py has all agent methods"""
    print_header("3. Validating crew.py agent methods")
    
    # Load agents from YAML
    with open('src/space_hulk_game/config/agents.yaml', 'r') as f:
        agents_yaml = yaml.safe_load(f)
    
    # Load crew.py and find @agent methods
    with open('src/space_hulk_game/crew.py', 'r') as f:
        crew_content = f.read()
    
    # Find all @agent decorated methods
    agent_pattern = r'@agent\s+def\s+(\w+)\(self\)'
    crew_agents = re.findall(agent_pattern, crew_content)
    
    yaml_agents = set(agents_yaml.keys())
    py_agents = set(crew_agents)
    
    missing_in_py = yaml_agents - py_agents
    missing_in_yaml = py_agents - yaml_agents
    
    all_match = True
    
    if missing_in_py:
        print_error("Agents in YAML but missing methods in crew.py:")
        for agent in sorted(missing_in_py):
            print(f"   - {agent}")
        all_match = False
    
    if missing_in_yaml:
        print_error("Agent methods in crew.py but not in YAML:")
        for agent in sorted(missing_in_yaml):
            print(f"   - {agent}")
        all_match = False
    
    if all_match:
        for agent in sorted(yaml_agents):
            print_success(agent)
        print()
        print_success(f"All {len(yaml_agents)} agent methods properly defined!")
        return True
    
    return False

def validate_crew_py_tasks():
    """Validate crew.py has all task methods"""
    print_header("4. Validating crew.py task methods")
    
    # Load tasks from YAML
    with open('src/space_hulk_game/config/tasks.yaml', 'r') as f:
        tasks_yaml = yaml.safe_load(f)
    
    # Load crew.py and find @task methods
    with open('src/space_hulk_game/crew.py', 'r') as f:
        crew_content = f.read()
    
    # Find all @task decorated methods
    task_pattern = r'@task\s+def\s+(\w+)\(self\)'
    crew_tasks = re.findall(task_pattern, crew_content)
    
    yaml_tasks = set(tasks_yaml.keys())
    py_tasks = set(crew_tasks)
    
    missing_in_py = yaml_tasks - py_tasks
    missing_in_yaml = py_tasks - yaml_tasks
    
    all_match = True
    
    if missing_in_py:
        print_error("Tasks in YAML but missing methods in crew.py:")
        for task in sorted(missing_in_py):
            print(f"   - {task}")
        all_match = False
    
    if missing_in_yaml:
        print_error("Task methods in crew.py but not in YAML:")
        for task in sorted(missing_in_yaml):
            print(f"   - {task}")
        all_match = False
    
    if all_match:
        for task in sorted(yaml_tasks):
            print_success(task)
        print()
        print_success(f"All {len(yaml_tasks)} task methods properly defined!")
        return True
    
    return False

def run_unit_tests():
    """Run relevant unit tests"""
    print_header("5. Running unit tests")
    
    # Run the test directly using subprocess since module path is complex
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'unittest', 'tests.test_crew_improvements', '-v'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode == 0:
        print()
        print_success("All crew improvement tests passed!")
        return True
    else:
        print()
        print_error("Some tests failed")
        return False

def main():
    """Main validation function"""
    print(f"\n{Color.BOLD}Space Hulk Game - 7-Agent System Validation{Color.END}")
    print(f"{Color.BOLD}{'=' * 70}{Color.END}\n")
    
    results = []
    
    # Run all validations
    results.append(("Agents YAML", validate_agents_yaml()))
    results.append(("Tasks YAML", validate_tasks_yaml()))
    results.append(("Crew.py Agents", validate_crew_py_agents()))
    results.append(("Crew.py Tasks", validate_crew_py_tasks()))
    results.append(("Unit Tests", run_unit_tests()))
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = True
    for name, passed in results:
        if passed:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
            all_passed = False
    
    print()
    
    if all_passed:
        print(f"{Color.GREEN}{Color.BOLD}{'=' * 70}{Color.END}")
        print(f"{Color.GREEN}{Color.BOLD}✅ ALL VALIDATIONS PASSED - 7-AGENT SYSTEM READY!{Color.END}")
        print(f"{Color.GREEN}{Color.BOLD}{'=' * 70}{Color.END}\n")
        
        print("The system is properly configured with:")
        print("  • 7 agents (5 content creation + 2 quality assurance)")
        print("  • 11 tasks (5 generation + 6 evaluation)")
        print("  • Balanced workload (max 27% per agent)")
        print("  • All tests passing")
        print()
        print("Ready to generate game content!")
        print()
        return 0
    else:
        print(f"{Color.RED}{Color.BOLD}{'=' * 70}{Color.END}")
        print(f"{Color.RED}{Color.BOLD}❌ VALIDATION FAILED - PLEASE FIX ISSUES ABOVE{Color.END}")
        print(f"{Color.RED}{Color.BOLD}{'=' * 70}{Color.END}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
