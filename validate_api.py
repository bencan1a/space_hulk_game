#!/usr/bin/env python3
"""
OpenRouter API Validation Script

This script validates that the OpenRouter API is properly configured
and can be accessed. It performs a simple API call to verify connectivity.

Usage:
    # With environment variables set:
    export OPENROUTER_API_KEY=sk-or-v1-your-key-here
    export OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
    python validate_api.py
    
    # Or with inline parameters:
    OPENROUTER_API_KEY=sk-or-v1-your-key python validate_api.py
"""
import os
import sys

def validate_api_connection():
    """Validate OpenRouter API connection."""
    print("="*70)
    print("OpenRouter API Validation")
    print("="*70)
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    model_name = os.getenv('OPENAI_MODEL_NAME', 'openrouter/anthropic/claude-3.5-sonnet')
    
    if not api_key:
        print("\n❌ ERROR: OPENROUTER_API_KEY environment variable not set")
        print("\nTo fix this:")
        print("  1. Get an API key from: https://openrouter.ai/keys")
        print("  2. Set the environment variable:")
        print("     export OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        print("  3. Optionally set the model:")
        print("     export OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet")
        return False
    
    print(f"\n✓ Found OPENROUTER_API_KEY (length: {len(api_key)})")
    print(f"✓ Using model: {model_name}")
    
    # Try to import CrewAI
    print("\nChecking dependencies...")
    try:
        from crewai import LLM
        print("✓ CrewAI installed")
    except ImportError as e:
        print(f"❌ ERROR: CrewAI not installed: {e}")
        print("\nTo fix this:")
        print("  pip install crewai")
        return False
    
    # Try to make an API call
    print("\nTesting API connection...")
    try:
        llm = LLM(
            model=model_name,
            api_key=api_key
        )
        print(f"✓ LLM instance created successfully")
        
        # Simple test call
        print("\nMaking test API call...")
        test_message = [{"role": "user", "content": "Say 'API validation successful' if you can read this."}]
        
        response = llm.call(test_message)
        
        print(f"✓ API call successful!")
        print(f"\nResponse:")
        print("-" * 70)
        print(response)
        print("-" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: API call failed: {str(e)}")
        print("\nPossible issues:")
        print("  1. Invalid API key")
        print("  2. Network connectivity issues")
        print("  3. Model not available or incorrect model name")
        print("  4. Insufficient API credits")
        print("\nCheck your API key at: https://openrouter.ai/")
        return False


def main():
    """Main entry point."""
    success = validate_api_connection()
    
    print("\n" + "="*70)
    if success:
        print("✅ API VALIDATION SUCCESSFUL")
        print("\nYou can now run the Space Hulk Game with OpenRouter:")
        print("  crewai run")
        print("\nOr run integration tests:")
        print("  RUN_REAL_API_TESTS=1 python -m unittest tests.test_integration_sequential")
    else:
        print("❌ API VALIDATION FAILED")
        print("\nPlease fix the issues above and try again.")
    print("="*70)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
