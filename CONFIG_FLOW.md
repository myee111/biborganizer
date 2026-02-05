# Configuration Flow - How .env Controls Everything

## Overview

All configuration comes from the `.env` file and propagates through the entire codebase. There are **no hardcoded models** in the API calls.

## Your Current Configuration

```bash
# .env file
USE_VERTEX_AI=true
VERTEX_PROJECT_ID=itpc-gcp-product-all-claude
VERTEX_REGION=us-central1
CLAUDE_MODEL=sonnet-3.5
```

## Configuration Flow Diagram

```
.env file
    ↓
Environment Variables (loaded by python-dotenv)
    ↓
┌─────────────────────────────────────────────┐
│         claude_client.py                     │
├─────────────────────────────────────────────┤
│                                              │
│  1. get_claude_client()                      │
│     Reads: USE_VERTEX_AI                     │
│     Creates: AnthropicVertex client          │
│     Uses: VERTEX_PROJECT_ID, VERTEX_REGION   │
│                                              │
│  2. get_model_name()                         │
│     Reads: USE_VERTEX_AI, CLAUDE_MODEL       │
│     Maps: sonnet-3.5 → claude-3-5-sonnet@... │
│     Returns: Vertex AI model identifier      │
│                                              │
└─────────────────────────────────────────────┘
    ↓
All API Functions
    ↓
┌─────────────────────────────────────────────┐
│  analyze_faces_in_image()                    │
│    → calls get_model_name()                  │
│                                              │
│  generate_facial_description()               │
│    → calls analyze_faces_in_image()          │
│      → calls get_model_name()                │
│                                              │
│  detect_and_describe_all_faces()             │
│    → calls analyze_faces_in_image()          │
│      → calls get_model_name()                │
│                                              │
│  compare_face_descriptions()                 │
│    → calls get_model_name()                  │
└─────────────────────────────────────────────┘
    ↓
Claude API Call
    ↓
Using: claude-3-5-sonnet@20240620
Via: AnthropicVertex client
To: projects/itpc-gcp-product-all-claude/locations/us-central1
```

## Code Implementation

### 1. Client Creation (claude_client.py:103-133)

```python
def get_claude_client() -> Union[Anthropic, AnthropicVertex]:
    use_vertex = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'

    if use_vertex:
        project_id = os.getenv('VERTEX_PROJECT_ID')
        region = os.getenv('VERTEX_REGION', 'us-east5')
        return AnthropicVertex(project_id=project_id, region=region)
    else:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        return Anthropic(api_key=api_key)
```

**Current behavior:**
- ✅ Reads `USE_VERTEX_AI=true` from .env
- ✅ Creates `AnthropicVertex` client
- ✅ Uses `project_id=itpc-gcp-product-all-claude`
- ✅ Uses `region=us-central1`

### 2. Model Resolution (claude_client.py:52-100)

```python
def get_model_name() -> str:
    use_vertex = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'
    model_map = VERTEX_MODELS if use_vertex else ANTHROPIC_MODELS

    model_env = os.getenv('CLAUDE_MODEL')

    if model_env and model_env in model_map:
        return model_map[model_env]

    # Default based on auth method
    return 'claude-3-5-sonnet@20240620' if use_vertex else 'claude-sonnet-4-5-20250929'
```

**Current behavior:**
- ✅ Reads `CLAUDE_MODEL=sonnet-3.5` from .env
- ✅ Uses `VERTEX_MODELS` map (because USE_VERTEX_AI=true)
- ✅ Maps `sonnet-3.5` → `claude-3-5-sonnet@20240620`

### 3. API Calls Use get_model_name()

**analyze_faces_in_image()** (claude_client.py:238-287)
```python
def analyze_faces_in_image(image_path: str, prompt: str, model: Optional[str] = None):
    client = get_claude_client()  # ← Uses .env

    if model is None:
        model = get_model_name()  # ← Uses .env

    response = client.messages.create(model=model, ...)
```

**compare_face_descriptions()** (claude_client.py:354-415)
```python
def compare_face_descriptions(description1: str, description2: str):
    client = get_claude_client()  # ← Uses .env
    model = get_model_name()  # ← Uses .env

    response = client.messages.create(model=model, ...)
```

**All wrapper functions:**
- `generate_facial_description()` → calls `analyze_faces_in_image()`
- `detect_and_describe_all_faces()` → calls `analyze_faces_in_image()`

## Model Mapping Tables

### Anthropic API Models (when USE_VERTEX_AI=false)

| Short Name | Resolved Model ID |
|-----------|-------------------|
| sonnet-4.5 | claude-sonnet-4-5-20250929 |
| opus-4.5 | claude-opus-4-5-20241101 |
| sonnet-3.7 | claude-3-7-sonnet-20250219 |
| sonnet-3.5 | claude-3-5-sonnet-20241022 |
| haiku-3.5 | claude-3-5-haiku-20241022 |

### Vertex AI Models (when USE_VERTEX_AI=true) ← **You're using this**

| Short Name | Resolved Model ID |
|-----------|-------------------|
| sonnet-3.5 | claude-3-5-sonnet@20240620 |
| haiku-3.5 | claude-3-5-haiku@20241022 |
| opus-3 | claude-3-opus@20240229 |

## How to Change Configuration

### Change Model

Edit `.env`:
```bash
CLAUDE_MODEL=haiku-3.5  # For faster/cheaper
CLAUDE_MODEL=sonnet-3.5 # For balanced (current)
CLAUDE_MODEL=opus-3     # For best quality
```

### Change Region

Edit `.env`:
```bash
VERTEX_REGION=us-east5
VERTEX_REGION=us-central1  # Current
VERTEX_REGION=europe-west1
```

### Switch to Anthropic API

Edit `.env`:
```bash
USE_VERTEX_AI=false
ANTHROPIC_API_KEY=sk-ant-api03-xxx...
CLAUDE_MODEL=sonnet-4.5  # Now you can use 4.5!
```

## Verification

Run the configuration test:
```bash
source venv/bin/activate
python test_config_propagation.py
```

Expected output:
```
✓ Correctly using AnthropicVertex
✓ Correct mapping: sonnet-3.5 → claude-3-5-sonnet@20240620
✓ Function calls get_model_name()
✓ Configuration properly propagates
```

## No Hardcoded Models

Search the codebase:
```bash
grep -n "model=" *.py | grep -v get_model_name
```

Result: All model assignments use `get_model_name()` ✅

## Summary

**Every API call follows this path:**

1. Your `.env` file sets: `CLAUDE_MODEL=sonnet-3.5`
2. `get_model_name()` reads `.env` and resolves to: `claude-3-5-sonnet@20240620`
3. All API functions call `get_model_name()`
4. Model is used consistently across all API calls

**To change the model everywhere:** Just edit one line in `.env`

```bash
CLAUDE_MODEL=haiku-3.5  # Changes ALL API calls to use Haiku
```

That's it! ✅
