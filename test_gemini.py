#!/usr/bin/env python3
"""
Test Gemini configuration and connection.
"""

import sys
from dotenv import load_dotenv
import os

load_dotenv()

print("="*70)
print("Gemini Configuration Test")
print("="*70)

# Check configuration
print("\n1. Configuration:")
provider = os.getenv('AI_PROVIDER', 'gemini')
project_id = os.getenv('VERTEX_PROJECT_ID')
region = os.getenv('VERTEX_REGION', 'us-central1')
model = os.getenv('GEMINI_MODEL', 'flash')

print(f"   AI_PROVIDER: {provider}")
print(f"   VERTEX_PROJECT_ID: {project_id}")
print(f"   VERTEX_REGION: {region}")
print(f"   GEMINI_MODEL: {model}")

if provider != 'gemini':
    print(f"\n   ⚠ Warning: AI_PROVIDER is '{provider}', expected 'gemini'")

# Test Gemini client
print("\n2. Testing Gemini Client:")
try:
    from gemini_client import initialize_vertex_ai, get_model_name

    # Initialize
    proj, reg = initialize_vertex_ai()
    print(f"   ✓ Vertex AI initialized")
    print(f"   ✓ Project: {proj}")
    print(f"   ✓ Region: {reg}")

    # Get model
    model_name = get_model_name()
    print(f"   ✓ Model: {model_name}")

except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test a simple API call
print("\n3. Testing Gemini API:")
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel

    vertexai.init(project=project_id, location=region)

    model = GenerativeModel(model_name)

    response = model.generate_content("Say 'Hello! Gemini is working.' and nothing else.")

    print(f"   ✓ API Response: {response.text}")
    print(f"\n   ✓ Gemini API connection successful!")

except Exception as e:
    print(f"   ✗ API Error: {e}")
    print(f"\n   Troubleshooting:")
    print(f"   - Make sure you're authenticated: gcloud auth application-default login")
    print(f"   - Verify project ID is correct: {project_id}")
    print(f"   - Check region is supported: {region}")
    sys.exit(1)

# Test vision client wrapper
print("\n4. Testing Vision Client Wrapper:")
try:
    from vision_client import get_provider

    detected_provider = get_provider()
    print(f"   ✓ Detected provider: {detected_provider}")

    if detected_provider == 'gemini':
        print(f"   ✓ Correctly configured for Gemini")
    else:
        print(f"   ⚠ Warning: Expected 'gemini', got '{detected_provider}'")

except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*70)
print("Summary")
print("="*70)
print(f"""
Configuration:
  ✓ Using Gemini via Vertex AI
  ✓ Project: {project_id}
  ✓ Region: {region}
  ✓ Model: {model_name}

Status:
  ✓ All tests passed!
  ✓ Ready to organize photos with Gemini

Next steps:
  1. python manage_database.py  # Add people
  2. python organize.py /path/to/photos --dry-run  # Test
  3. python organize.py /path/to/photos  # Organize!
""")
print("="*70 + "\n")
