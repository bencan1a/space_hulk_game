#!/usr/bin/env python3
"""
Connectivity Test Report for OpenRouter API and CrewAI Dependencies

This script tests network connectivity to required services after firewall
rule updates.
"""

import os
import sys


def main():
    print("\n" + "=" * 70)
    print("CONNECTIVITY TEST REPORT")
    print("=" * 70)

    # Import test
    print("\n✓ Step 1: Import CrewAI")
    try:
        from crewai import LLM

        print("  SUCCESS: CrewAI is installed and importable")
    except ImportError as e:
        print(f"  FAILED: {e}")
        return False

    # Connectivity test
    print("\n✓ Step 2: Test OpenRouter API Connectivity")
    import requests  # type: ignore[import-untyped]

    try:
        response = requests.get("https://openrouter.ai/api/v1/models", timeout=5)
        print(f"  SUCCESS: OpenRouter API is reachable (HTTP {response.status_code})")
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    # Scarf test
    print("\n⚠ Step 3: Test Scarf Analytics (optional)")
    try:
        response = requests.get("https://scarf.sh", timeout=5)
        print(f"  SUCCESS: Scarf is reachable (HTTP {response.status_code})")
    except Exception as e:
        print(f"  BLOCKED: {type(e).__name__}")
        print("  NOTE: CrewAI may send analytics to Scarf, but this is optional")
        print("        The main functionality should work without it")

    # LLM initialization test
    print("\n✓ Step 4: Test LLM Initialization")
    try:
        llm = LLM(model="openrouter/anthropic/claude-3.5-sonnet", api_key="test-placeholder")
        print("  SUCCESS: LLM instance can be created")
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    # API endpoint test
    print("\n✓ Step 5: Test OpenRouter API Endpoint")
    try:
        llm.call([{"role": "user", "content": "test"}])
        print("  UNEXPECTED: Call succeeded without valid key")
    except Exception as e:
        error_str = str(e).lower()
        if "401" in error_str or "auth" in error_str:
            print("  SUCCESS: API endpoint is reachable")
            print("  Got expected authentication error (401) - this is correct!")
        else:
            print(f"  ERROR: {type(e).__name__}: {str(e)[:100]}")
            return False

    # Credentials check
    print("\n⚠ Step 6: Check API Credentials")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print(f"  FOUND: OPENROUTER_API_KEY (length: {len(api_key)})")
        print("  ✓ Ready to run real API tests!")
        return True
    else:
        print("  NOT SET: OPENROUTER_API_KEY environment variable")
        print("\n  To complete the real API tests, please set:")
        print("    export OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        print("    export OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet  # optional")
        print("\n  Then run:")
        print("    python -m unittest tests.test_api_validation -v")
        return None  # Connectivity OK, but no credentials

    print("\n" + "=" * 70)


if __name__ == "__main__":
    result = main()

    print("\n" + "=" * 70)
    print("FINAL STATUS")
    print("=" * 70)

    if result is True:
        print("✅ READY FOR REAL API TESTS")
        print("   All connectivity checks passed and credentials are available")
        sys.exit(0)
    elif result is None:
        print("✅ CONNECTIVITY OK - CREDENTIALS NEEDED")
        print("   Network access is working, waiting for API credentials")
        sys.exit(0)
    else:
        print("❌ CONNECTIVITY ISSUES")
        print("   Please check firewall configuration")
        sys.exit(1)
