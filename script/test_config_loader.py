#!/usr/bin/env python3
"""
Test script for configuration loader.
"""

import sys
from pathlib import Path

try:
    from config_loader import ConfigLoader, ConfigError, load_config
except ImportError as e:
    print(f"Error importing config_loader: {e}")
    print("Please make sure PyYAML is installed: pip install PyYAML")
    sys.exit(1)


def get_example_config_path():
    """Get path to example configuration file."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    return project_root / "config" / "example.yaml"


def test_check_enabled():
    """Test checking if checks are enabled."""
    print("\n" + "=" * 80)
    print("Test 2: Checking if checks are enabled")
    print("=" * 80)

    try:
        example_config = get_example_config_path()
        loader = ConfigLoader(str(example_config))
        config = loader.load()

        test_checks = ["cover", "table_of_contents", "captions", "references"]
        for check_name in test_checks:
            enabled = loader.get_check_enabled(check_name)
            status = "✓" if enabled else "✗"
            print(f"  {status} {check_name}: {enabled}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_check_config():
    """Test getting check configuration."""
    print("\n" + "=" * 80)
    print("Test 3: Getting check configuration")
    print("=" * 80)

    try:
        example_config = get_example_config_path()
        loader = ConfigLoader(str(example_config))
        config = loader.load()

        cover_config = loader.get_check_config("cover")
        if cover_config:
            print("✓ Cover configuration retrieved")
            print(f"  Enabled: {cover_config.get('enabled', 'N/A')}")
            print(f"  Required elements: {cover_config.get('required_elements', [])}")
        else:
            print("✗ Cover configuration not found")
            return False

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_format_config():
    """Test getting format configuration."""
    print("\n" + "=" * 80)
    print("Test 4: Getting format configuration")
    print("=" * 80)

    try:
        example_config = get_example_config_path()
        loader = ConfigLoader(str(example_config))
        config = loader.load()

        cover_title_format = loader.get_format_config("cover", "title")
        if cover_title_format:
            print("✓ Cover title format retrieved")
            print(f"  Font: {cover_title_format.get('font')}")
            print(f"  Size: {cover_title_format.get('size')}")
            print(f"  Bold: {cover_title_format.get('bold')}")
            print(f"  Alignment: {cover_title_format.get('alignment')}")
        else:
            print("✗ Cover title format not found")
            return False

        caption_format = loader.get_format_config("captions", "figure")
        if caption_format:
            print("\n✓ Figure caption format retrieved")
            format_config = caption_format.get("format", {})
            print(f"  Font: {format_config.get('font')}")
            print(f"  Size: {format_config.get('size')}")
            print(f"  Alignment: {format_config.get('alignment')}")
        else:
            print("\n✗ Figure caption format not found")
            return False

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_numbering_config():
    """Test getting numbering configuration."""
    print("\n" + "=" * 80)
    print("Test 5: Getting numbering configuration")
    print("=" * 80)

    try:
        example_config = get_example_config_path()
        loader = ConfigLoader(str(example_config))
        config = loader.load()

        toc_numbering = loader.get_numbering_config("table_of_contents")
        if toc_numbering:
            print("✓ Table of contents numbering config retrieved")
            print(f"  Check continuity: {toc_numbering.get('check_continuity')}")
            print(f"  Format pattern: {toc_numbering.get('format_pattern')}")
        else:
            print("✗ Table of contents numbering config not found")
            return False

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_regex_compilation():
    """Test regex pattern compilation."""
    print("\n" + "=" * 80)
    print("Test 6: Compiling regex patterns")
    print("=" * 80)

    try:
        example_config = get_example_config_path()
        loader = ConfigLoader(str(example_config))
        config = loader.load()

        toc_numbering = loader.get_numbering_config("table_of_contents")
        if toc_numbering:
            pattern_str = toc_numbering.get("format_pattern")
            pattern = loader.compile_regex_pattern(pattern_str)
            if pattern:
                print(f"✓ Regex pattern compiled: {pattern_str}")
                test_cases = ["1", "1.1", "1.1.1", "invalid"]
                for test_case in test_cases:
                    match = pattern.match(test_case)
                    status = "✓" if match else "✗"
                    print(f"  {status} '{test_case}': {bool(match)}")
            else:
                print(f"✗ Failed to compile regex pattern: {pattern_str}")
                return False

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_all_enabled_checks():
    """Test getting all enabled checks."""
    print("\n" + "=" * 80)
    print("Test 7: Getting all enabled checks")
    print("=" * 80)

    try:
        example_config = get_example_config_path()
        loader = ConfigLoader(str(example_config))
        config = loader.load()

        enabled_checks = loader.get_all_enabled_checks()
        print(f"✓ Found {len(enabled_checks)} enabled checks")
        print(f"  Enabled checks: {', '.join(enabled_checks[:10])}...")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_convenience_functions():
    """Test convenience functions."""
    print("\n" + "=" * 80)
    print("Test 8: Testing convenience functions")
    print("=" * 80)

    try:
        example_config = get_example_config_path()

        if not example_config.exists():
            print(f"✗ Example config not found: {example_config}")
            return False

        config = load_config(str(example_config))
        print("✓ load_config() works")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_invalid_config():
    """Test handling of invalid configuration."""
    print("\n" + "=" * 80)
    print("Test 9: Testing error handling for invalid config")
    print("=" * 80)

    try:
        invalid_path = Path(__file__).parent / "nonexistent_config.yaml"
        loader = ConfigLoader(str(invalid_path))
        try:
            config = loader.load()
            print("✗ Should have raised ConfigError for nonexistent file")
            return False
        except ConfigError:
            print("✓ Correctly raised ConfigError for nonexistent file")
            return True
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Run all tests."""
    print("Configuration Loader Test Suite")
    print("=" * 80)

    tests = [
        test_check_enabled,
        test_get_check_config,
        test_get_format_config,
        test_get_numbering_config,
        test_regex_compilation,
        test_get_all_enabled_checks,
        test_convenience_functions,
        test_invalid_config,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
