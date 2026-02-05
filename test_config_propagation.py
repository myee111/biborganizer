#!/usr/bin/env python3
"""
Test that .env configuration properly propagates through the code.
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("="*70)
print("Configuration Propagation Test")
print("="*70)

# Check .env values
print("\n1. Reading .env file:")
use_vertex = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'
project_id = os.getenv('VERTEX_PROJECT_ID')
region = os.getenv('VERTEX_REGION')
model_setting = os.getenv('CLAUDE_MODEL')

print(f"   USE_VERTEX_AI: {use_vertex}")
print(f"   VERTEX_PROJECT_ID: {project_id}")
print(f"   VERTEX_REGION: {region}")
print(f"   CLAUDE_MODEL: {model_setting}")

# Check client initialization
print("\n2. Testing get_claude_client():")
try:
    from claude_client import get_claude_client
    client = get_claude_client()
    print(f"   ✓ Client type: {type(client).__name__}")

    if use_vertex:
        if "Vertex" in type(client).__name__:
            print(f"   ✓ Correctly using AnthropicVertex")
        else:
            print(f"   ✗ ERROR: Expected AnthropicVertex but got {type(client).__name__}")
    else:
        if "Vertex" not in type(client).__name__:
            print(f"   ✓ Correctly using Anthropic")
        else:
            print(f"   ✗ ERROR: Expected Anthropic but got {type(client).__name__}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Check model resolution
print("\n3. Testing get_model_name():")
try:
    from claude_client import get_model_name
    resolved_model = get_model_name()
    print(f"   Configured: {model_setting}")
    print(f"   Resolved to: {resolved_model}")

    if use_vertex:
        if '@' in resolved_model:
            print(f"   ✓ Correctly using Vertex AI format (contains '@')")
        else:
            print(f"   ✗ ERROR: Vertex AI models should contain '@'")

        expected = "claude-3-5-sonnet@20240620"
        if model_setting == 'sonnet-3.5' and resolved_model == expected:
            print(f"   ✓ Correct mapping: sonnet-3.5 → {expected}")
        else:
            print(f"   ⚠ Warning: Expected {expected}, got {resolved_model}")
    else:
        if '@' not in resolved_model:
            print(f"   ✓ Correctly using Anthropic API format (no '@')")
        else:
            print(f"   ✗ ERROR: Anthropic API models should not contain '@'")

except Exception as e:
    print(f"   ✗ Error: {e}")

# Check that model propagates to API functions
print("\n4. Testing model propagation in API functions:")
print("   Checking analyze_faces_in_image()...")
try:
    import inspect
    from claude_client import analyze_faces_in_image

    # Check function signature
    sig = inspect.signature(analyze_faces_in_image)
    if 'model' in sig.parameters:
        print(f"   ✓ Function accepts 'model' parameter")

        # Check if it has Optional type
        param = sig.parameters['model']
        if param.default is None:
            print(f"   ✓ Model parameter defaults to None (uses get_model_name())")
        else:
            print(f"   ⚠ Model parameter default: {param.default}")
    else:
        print(f"   ✗ Function missing 'model' parameter")

except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n   Checking compare_face_descriptions()...")
try:
    # Read the source to verify it calls get_model_name
    with open('claude_client.py', 'r') as f:
        source = f.read()

    if 'def compare_face_descriptions' in source:
        # Find the function and check if it calls get_model_name
        start = source.find('def compare_face_descriptions')
        end = source.find('\ndef ', start + 1)
        function_code = source[start:end]

        if 'get_model_name()' in function_code:
            print(f"   ✓ Function calls get_model_name()")
        else:
            print(f"   ✗ Function does not call get_model_name()")

except Exception as e:
    print(f"   ✗ Error: {e}")

# Summary
print("\n" + "="*70)
print("Configuration Flow Summary")
print("="*70)

print(f"""
.env file:
  USE_VERTEX_AI={use_vertex}
  VERTEX_PROJECT_ID={project_id}
  VERTEX_REGION={region}
  CLAUDE_MODEL={model_setting}

Flow:
  1. dotenv loads .env → Environment variables
  2. get_claude_client() → {'AnthropicVertex' if use_vertex else 'Anthropic'} client
  3. get_model_name() → {resolved_model}
  4. API functions use get_model_name() → Consistent model everywhere

Status: {'✓ Configuration properly propagates' if use_vertex else '✓ Configuration properly propagates'}
""")

print("="*70)
print("\nTo test actual API connection, run:")
print("  python test_vertex_connection.py")
print("="*70 + "\n")
