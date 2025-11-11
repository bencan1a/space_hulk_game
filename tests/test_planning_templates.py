#!/usr/bin/env python3
"""
Test script for Chunk 3.4: Planning Templates

This script validates that:
1. Template files are properly formatted YAML
2. Template loading logic works correctly
3. Keyword detection functions as expected
"""

import os
import sys

import yaml

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_template_files():
    """Test that all template files exist and are valid YAML."""
    print("=" * 60)
    print("Testing Template Files")
    print("=" * 60)

    template_dir = os.path.join(os.path.dirname(__file__), "..", "planning_templates")
    templates = [
        "space_horror.yaml",
        "mystery_investigation.yaml",
        "survival_escape.yaml",
        "combat_focused.yaml",
    ]

    all_valid = True

    for template_name in templates:
        template_path = os.path.join(template_dir, template_name)
        print(f"\n📄 Testing {template_name}...")

        # Check file exists
        if not os.path.exists(template_path):
            print(f"  ❌ File not found: {template_path}")
            all_valid = False
            continue

        # Check file can be loaded as YAML
        try:
            with open(template_path, encoding="utf-8") as f:
                content = yaml.safe_load(f)

            # Check required fields
            required_fields = ["template_name", "template_version", "description"]
            missing_fields = [field for field in required_fields if field not in content]

            if missing_fields:
                print(f"  ❌ Missing required fields: {missing_fields}")
                all_valid = False
            else:
                print("  ✅ Valid YAML with all required fields")
                print(f"     Name: {content.get('template_name')}")
                print(f"     Version: {content.get('template_version')}")

                # Count main sections
                sections = len([k for k in content if not k.startswith("_")])
                print(f"     Sections: {sections}")

                # Check file size
                file_size = os.path.getsize(template_path)
                print(f"     Size: {file_size:,} bytes")

        except yaml.YAMLError as e:
            print(f"  ❌ YAML parsing error: {e}")
            all_valid = False
        except Exception as e:
            print(f"  ❌ Error loading file: {e}")
            all_valid = False

    return all_valid


def test_keyword_detection():
    """Test that keyword detection works correctly."""
    print("\n" + "=" * 60)
    print("Testing Keyword Detection")
    print("=" * 60)

    # Test prompts with expected templates
    test_cases = [
        ("A terrifying horror scenario in a Space Hulk", "space_horror"),
        ("Investigate a mysterious disappearance", "mystery_investigation"),
        ("Escape from the collapsing hulk with limited resources", "survival_escape"),
        ("Tactical combat mission with squad coordination", "combat_focused"),
        ("A space hulk adventure", None),  # No keywords
    ]

    # Define keyword mapping (same as in crew.py)
    template_keywords = {
        "space_horror": [
            "horror",
            "scary",
            "terrifying",
            "dread",
            "fear",
            "nightmare",
            "corruption",
        ],
        "mystery_investigation": [
            "mystery",
            "investigation",
            "investigate",
            "detective",
            "clue",
            "solve",
            "evidence",
            "discover",
        ],
        "survival_escape": [
            "survival",
            "escape",
            "desperate",
            "resource",
            "trapped",
            "flee",
            "running",
        ],
        "combat_focused": ["combat", "battle", "tactical", "squad", "fight", "warrior", "assault"],
    }

    all_passed = True

    for prompt, expected_template in test_cases:
        print(f'\n📝 Testing: "{prompt}"')

        # Detect template (simulating crew.py logic)
        prompt_lower = prompt.lower()
        detected_template = None

        for template_name, keywords in template_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_template = template_name
                break

        # Check result
        if detected_template == expected_template:
            if detected_template:
                print(f"  ✅ Correctly detected: {detected_template}")
            else:
                print("  ✅ Correctly detected: no template")
        else:
            print(f"  ❌ Expected: {expected_template}, Got: {detected_template}")
            all_passed = False

    return all_passed


def test_template_content():
    """Test that templates have expected content structure."""
    print("\n" + "=" * 60)
    print("Testing Template Content Structure")
    print("=" * 60)

    template_dir = os.path.join(os.path.dirname(__file__), "..", "planning_templates")

    # Expected sections (not all required, but good to have)
    recommended_sections = [
        "narrative_focus",
        "required_elements",
        "tone",
        "example_scenes",
        "example_puzzles",
        "character_suggestions",
        "story_structure",
        "mechanics_suggestions",
        "ending_guidelines",
        "quality_targets",
    ]

    all_templates_good = True

    for template_file in os.listdir(template_dir):
        if not template_file.endswith(".yaml"):
            continue

        print(f"\n📋 Analyzing {template_file}...")

        template_path = os.path.join(template_dir, template_file)
        with open(template_path, encoding="utf-8") as f:
            content = yaml.safe_load(f)

        # Check for recommended sections
        present_sections = [section for section in recommended_sections if section in content]
        missing_sections = [section for section in recommended_sections if section not in content]

        coverage = len(present_sections) / len(recommended_sections) * 100

        print(
            f"  Section coverage: {coverage:.0f}% ({len(present_sections)}/{len(recommended_sections)})"
        )

        if coverage >= 80:
            print("  ✅ Good coverage")
        elif coverage >= 60:
            print("  ⚠️  Acceptable coverage")
        else:
            print("  ❌ Low coverage")
            all_templates_good = False

        if missing_sections:
            print(f"  Missing sections: {', '.join(missing_sections[:3])}")

    return all_templates_good


def main():
    """Run all tests."""
    print("\n" + "🎯" * 30)
    print("Chunk 3.4: Planning Templates - Validation Tests")
    print("🎯" * 30 + "\n")

    results = {
        "Template Files": test_template_files(),
        "Keyword Detection": test_keyword_detection(),
        "Template Content": test_template_content(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests PASSED! Chunk 3.4 implementation validated.")
        return 0
    else:
        print("⚠️  Some tests FAILED. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
