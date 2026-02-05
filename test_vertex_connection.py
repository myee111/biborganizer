#!/usr/bin/env python3
"""
Test Vertex AI connection and model selection.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_model_resolution():
    """Test that model names are correctly resolved for Vertex AI."""
    from claude_client import get_model_name

    print("="*70)
    print("Testing Model Resolution")
    print("="*70)

    use_vertex = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'
    configured_model = os.getenv('CLAUDE_MODEL', 'not set')

    print(f"\nAuthentication: {'Vertex AI' if use_vertex else 'Anthropic API'}")
    print(f"Configured model: {configured_model}")

    resolved_model = get_model_name()
    print(f"Resolved model ID: {resolved_model}")

    if use_vertex:
        if '@' in resolved_model:
            print("✓ Using Vertex AI model format")
        else:
            print("✗ Warning: Not using Vertex AI model format")
    else:
        if '@' not in resolved_model:
            print("✓ Using Anthropic API model format")
        else:
            print("✗ Warning: Not using Anthropic API model format")

    return resolved_model


def test_api_connection():
    """Test actual API connection."""
    from claude_client import get_claude_client

    print("\n" + "="*70)
    print("Testing API Connection")
    print("="*70)

    try:
        client = get_claude_client()
        print("\n✓ Client initialized successfully")

        # Get the resolved model
        from claude_client import get_model_name
        model = get_model_name()

        print(f"Testing with model: {model}")
        print("Sending test message to Claude...")

        response = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello! API connection successful.' and nothing else."
                }
            ]
        )

        result = response.content[0].text
        print(f"\n✓ API Response: {result}")
        print("\n✓ Connection test PASSED!")
        return True

    except Exception as e:
        print(f"\n✗ Connection test FAILED!")
        print(f"Error: {str(e)}")

        # Provide helpful error messages
        if "404" in str(e):
            print("\nTroubleshooting:")
            print("- Check that you're using the correct model for your auth method")
            print("- Vertex AI models: sonnet-3.5, haiku-3.5, opus-3")
            print("- Anthropic API models: sonnet-4.5, opus-4.5, etc.")
        elif "authentication" in str(e).lower() or "credentials" in str(e).lower():
            print("\nTroubleshooting:")
            print("- Run: gcloud auth application-default login")
            print("- Verify your project ID is correct")
            print("- Check that Vertex AI API is enabled")

        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("Vertex AI Connection Test")
    print("="*70)

    # Test model resolution
    model = test_model_resolution()

    # Test API connection
    success = test_api_connection()

    print("\n" + "="*70)
    if success:
        print("✓ All tests passed! You're ready to organize photos.")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
    print("="*70 + "\n")

    return 0 if success else 1


if __name__ == '__main__':
    import sys
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
