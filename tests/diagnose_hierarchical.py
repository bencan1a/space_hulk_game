#!/usr/bin/env python3
"""
Diagnostic script to understand hierarchical mode failures.

This script attempts to identify the specific issue with hierarchical mode
by testing progressively more complex configurations.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from crewai import Agent, Crew, Task, Process, LLM
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_hierarchical():
    """Test absolute minimal hierarchical configuration."""
    print("\n" + "="*80)
    print("TEST 1: Basic Hierarchical (1 task, 1 worker)")
    print("="*80)
    
    try:
        # Create simple LLM config
        llm = LLM(
            model=os.environ.get("OPENAI_MODEL_NAME", "ollama/qwen2.5"),
            base_url="http://localhost:11434" if "ollama" in os.environ.get("OPENAI_MODEL_NAME", "") else None,
            api_key=os.environ.get("OPENROUTER_API_KEY") if os.environ.get("OPENROUTER_API_KEY") else None
        )
        
        # Create manager with explicit configuration
        manager = Agent(
            role="Manager",
            goal="Coordinate task execution",
            backstory="An experienced project manager.",
            llm=llm,
            allow_delegation=True,
            verbose=True
        )
        
        # Create single worker
        worker = Agent(
            role="Writer",
            goal="Write a simple story",
            backstory="A creative writer.",
            llm=llm,
            allow_delegation=False,
            verbose=True
        )
        
        # Create simple task
        task = Task(
            description="Write a one-sentence story about a space marine.",
            expected_output="A single sentence story.",
            agent=worker
        )
        
        # Create minimal hierarchical crew
        crew = Crew(
            agents=[worker],
            tasks=[task],
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True
        )
        
        print("\n🚀 Testing basic hierarchical execution...")
        result = crew.kickoff()
        print(f"\n✅ SUCCESS! Result: {result.raw[:100]}...")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_with_llm_params():
    """Test with adjusted LLM parameters for hierarchical mode."""
    print("\n" + "="*80)
    print("TEST 2: Hierarchical with Optimized LLM Parameters")
    print("="*80)
    
    try:
        from space_hulk_game.crew import SpaceHulkGame
        
        crew_instance = SpaceHulkGame()
        
        # Create manager with simplified configuration
        manager_llm = LLM(
            model=os.environ.get("OPENAI_MODEL_NAME", "ollama/qwen2.5"),
            base_url="http://localhost:11434" if "ollama" in os.environ.get("OPENAI_MODEL_NAME", "") else None,
            api_key=os.environ.get("OPENROUTER_API_KEY") if os.environ.get("OPENROUTER_API_KEY") else None,
            temperature=0.3,  # Lower temperature for manager decisions
            max_tokens=2000   # Limit token usage
        )
        
        manager = Agent(
            role="Narrative Director",
            goal="Coordinate narrative development efficiently",
            backstory="An experienced game narrative director.",
            llm=manager_llm,
            allow_delegation=True,
            verbose=True,
            max_iter=5  # Limit iterations
        )
        
        # Get single worker with task
        worker = crew_instance.PlotMasterAgent()
        task = crew_instance.GenerateOverarchingPlot()
        
        # Single task hierarchical crew
        crew = Crew(
            agents=[worker],
            tasks=[task],
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True
        )
        
        print("\n🚀 Testing with optimized parameters...")
        result = crew.kickoff(inputs={"prompt": "A short space marine story"})
        print(f"\n✅ SUCCESS!")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_sequential_baseline():
    """Test sequential mode as baseline."""
    print("\n" + "="*80)
    print("TEST 0: Sequential Baseline (for comparison)")
    print("="*80)
    
    try:
        from space_hulk_game.crew import SpaceHulkGame
        
        crew_instance = SpaceHulkGame()
        
        # Get single task
        worker = crew_instance.PlotMasterAgent()
        task = crew_instance.GenerateOverarchingPlot()
        
        # Sequential crew
        crew = Crew(
            agents=[worker],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        print("\n🚀 Testing sequential execution...")
        result = crew.kickoff(inputs={"prompt": "A short space marine story"})
        print(f"\n✅ SUCCESS!")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False


if __name__ == "__main__":
    print("\nHIERARCHICAL MODE DIAGNOSTIC")
    print("="*80)
    print("This script tests progressively more complex hierarchical configurations")
    print("to identify the specific failure point.")
    print("="*80)
    
    results = {}
    
    # Test 0: Sequential baseline
    results['sequential'] = test_sequential_baseline()
    
    # Test 1: Minimal hierarchical
    results['basic_hierarchical'] = test_basic_hierarchical()
    
    # Test 2: With LLM optimizations
    if results['basic_hierarchical']:
        results['optimized_hierarchical'] = test_with_llm_params()
    
    # Summary
    print("\n" + "="*80)
    print("DIAGNOSTIC SUMMARY")
    print("="*80)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:30s}: {status}")
    print("="*80)
