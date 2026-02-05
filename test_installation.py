#!/usr/bin/env python3
"""
Installation test script.
Verifies that all dependencies are installed correctly.
"""

import sys


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing package imports...")

    packages = [
        ("anthropic", "Anthropic SDK"),
        ("PIL", "Pillow"),
        ("dotenv", "python-dotenv"),
        ("tqdm", "tqdm"),
    ]

    all_ok = True

    for package, name in packages:
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT FOUND")
            all_ok = False

    # Optional: pillow-heif
    try:
        __import__("pillow_heif")
        print(f"  ✓ pillow-heif (optional, for HEIC support)")
    except ImportError:
        print(f"  ⚠ pillow-heif - NOT FOUND (optional, install for HEIC support)")

    return all_ok


def test_modules():
    """Test that project modules can be imported."""
    print("\nTesting project modules...")

    modules = [
        "claude_client",
        "face_database",
        "photo_organizer",
    ]

    all_ok = True

    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}.py")
        except ImportError as e:
            print(f"  ✗ {module}.py - ERROR: {e}")
            all_ok = False

    return all_ok


def test_env():
    """Test environment configuration."""
    print("\nTesting environment...")

    import os
    from dotenv import load_dotenv

    load_dotenv()

    use_vertex = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'

    if use_vertex:
        # Check Vertex AI configuration
        project_id = os.getenv('VERTEX_PROJECT_ID')
        region = os.getenv('VERTEX_REGION', 'us-east5')

        print(f"  Authentication mode: Vertex AI")

        if project_id:
            print(f"  ✓ VERTEX_PROJECT_ID found: {project_id}")
            print(f"  ✓ VERTEX_REGION: {region}")
            print(f"  Note: Make sure you're authenticated with gcloud:")
            print(f"    gcloud auth application-default login")
            return True
        else:
            print(f"  ✗ VERTEX_PROJECT_ID not found in .env file")
            print(f"    Set up Vertex AI configuration in .env:")
            print(f"    USE_VERTEX_AI=true")
            print(f"    VERTEX_PROJECT_ID=your-gcp-project-id")
            print(f"    VERTEX_REGION=us-east5")
            return False
    else:
        # Check direct Anthropic API key
        print(f"  Authentication mode: Anthropic API")

        api_key = os.getenv('ANTHROPIC_API_KEY')

        if api_key:
            # Mask the key for security
            masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
            print(f"  ✓ ANTHROPIC_API_KEY found: {masked}")
            return True
        else:
            print(f"  ✗ ANTHROPIC_API_KEY not found in .env file")
            print(f"    Create a .env file with your API key:")
            print(f"    cp .env.example .env")
            print(f"    # Then edit .env and add your key")
            print(f"    ")
            print(f"    Or use Vertex AI by setting:")
            print(f"    USE_VERTEX_AI=true")
            print(f"    VERTEX_PROJECT_ID=your-gcp-project-id")
            return False


def main():
    """Run all tests."""
    print("="*70)
    print("Photo Organizer - Installation Test")
    print("="*70)

    tests = [
        ("Package imports", test_imports),
        ("Project modules", test_modules),
        ("Environment", test_env),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\nError running {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*70)
    print("Summary")
    print("="*70)

    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False

    print()

    if all_passed:
        print("✓ All tests passed! Installation is complete.")
        print("\nNext steps:")
        print("  1. Run: python manage_database.py")
        print("  2. Add people to the database")
        print("  3. Run: python organize.py /path/to/photos --dry-run")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("\nTo install missing packages:")
        print("  pip install -r requirements.txt")

    print()

    return 0 if all_passed else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(1)
