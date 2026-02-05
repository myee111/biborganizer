# 404 Error - Fix Summary

## What Was the Problem?

You were getting a 404 error:
```
Error code: 404 - Publisher Model was not found or your project does not have access to it.
```

## What I Fixed

✅ **Updated model identifiers** for Vertex AI compatibility
✅ **Added automatic fallback** from newer to available models
✅ **Created Vertex AI model mappings** (separate from Anthropic API)
✅ **Updated configuration files** with correct model versions

## Current Configuration

Your `.env` file is now set to:
```bash
USE_VERTEX_AI=true
VERTEX_PROJECT_ID=itpc-gcp-product-all-claude
VERTEX_REGION=us-east5
CLAUDE_MODEL=sonnet-3.5
```

Model resolves to: `claude-3-5-sonnet@20240620`

## Why You're Still Getting 404

The error means **Anthropic models are not enabled** in your GCP project yet. This is a common issue with Vertex AI.

## Next Steps - Choose One Option

### Option A: Enable Anthropic on Vertex AI (Recommended for GCP Users)

**Follow the complete guide:** [ENABLE_VERTEX_ANTHROPIC.md](ENABLE_VERTEX_ANTHROPIC.md)

**Quick version:**

1. **Enable Vertex AI API:**
   ```bash
   gcloud services enable aiplatform.googleapis.com --project=itpc-gcp-product-all-claude
   ```

2. **Request Access to Anthropic Models:**
   - Go to [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
   - Search for "Claude"
   - Click "Enable" or "Request Access"

3. **Verify IAM Permissions:**
   ```bash
   gcloud projects add-iam-policy-binding itpc-gcp-product-all-claude \
     --member="user:YOUR_EMAIL" \
     --role="roles/aiplatform.user"
   ```

4. **Test again:**
   ```bash
   source venv/bin/activate
   python test_vertex_connection.py
   ```

**Timeline:** May take 1-2 business days for model access approval

### Option B: Use Anthropic API Directly (Immediate Access)

**Fastest way to start organizing photos now!**

1. **Get Anthropic API key:**
   - Go to https://console.anthropic.com
   - Create account and get API key

2. **Update `.env`:**
   ```bash
   nano .env
   ```

   Change to:
   ```bash
   USE_VERTEX_AI=false
   ANTHROPIC_API_KEY=sk-ant-api03-xxx...
   CLAUDE_MODEL=sonnet-4.5
   ```

3. **Test:**
   ```bash
   source venv/bin/activate
   python test_installation.py
   ```

4. **Start organizing:**
   ```bash
   python manage_database.py
   python organize.py ~/Photos --dry-run
   ```

**Timeline:** Immediate - works right away!

## Files Created/Updated

### Updated Files
- ✅ `claude_client.py` - Added Vertex AI model mappings
- ✅ `.env` - Configured for Vertex AI with correct model
- ✅ `.env.example` - Updated with both auth methods
- ✅ `config.json` - Separate model lists for Anthropic vs Vertex

### New Documentation
- 📄 `ENABLE_VERTEX_ANTHROPIC.md` - Complete Vertex AI setup guide
- 📄 `VERTEX_MODELS.md` - Model availability on Vertex AI
- 📄 `test_vertex_connection.py` - Connection testing tool
- 📄 `FIX_SUMMARY.md` - This file

## Recommended Path

**For most users:** Option B (Anthropic API) is fastest

1. Use Anthropic API to start organizing photos today
2. Work on Vertex AI access in parallel
3. Switch to Vertex AI later when approved

**To switch between them:** Just edit one line in `.env`:
```bash
USE_VERTEX_AI=true   # Use Vertex AI
USE_VERTEX_AI=false  # Use Anthropic API
```

## Model Comparison

| Model | Anthropic API | Vertex AI |
|-------|---------------|-----------|
| Sonnet 4.5 | ✅ Available | ❌ Not yet |
| Opus 4.5 | ✅ Available | ❌ Not yet |
| Sonnet 3.7 | ✅ Available | ❌ Not yet |
| Sonnet 3.5 | ✅ Available | ✅ Available* |
| Haiku 3.5 | ✅ Available | ✅ Available* |
| Opus 3 | ✅ Available | ✅ Available* |

*Requires enablement in your GCP project

## Test Your Setup

### For Anthropic API
```bash
source venv/bin/activate
python test_installation.py
```

### For Vertex AI
```bash
source venv/bin/activate
python test_vertex_connection.py
```

## Questions?

- **"Which should I use?"** → Anthropic API for immediate access
- **"Can I switch later?"** → Yes, just edit `.env`
- **"Which is cheaper?"** → Similar pricing, Vertex if you have GCP credits
- **"Which has better models?"** → Anthropic API has newer models (4.5, 3.7)

## Get Started Now

**Fastest path to organizing photos:**

```bash
# 1. Get Anthropic API key from console.anthropic.com
# 2. Update .env:
nano .env
# Set: USE_VERTEX_AI=false
#      ANTHROPIC_API_KEY=sk-ant-xxx...

# 3. Test
source venv/bin/activate
python test_installation.py

# 4. Start organizing!
python manage_database.py
```

You can have photos organized in the next 30 minutes with this approach!

## Support

- **Vertex AI Issues:** See [ENABLE_VERTEX_ANTHROPIC.md](ENABLE_VERTEX_ANTHROPIC.md)
- **Anthropic API Issues:** Check [README.md](README.md)
- **Model Selection:** See [MODEL_SELECTION.md](MODEL_SELECTION.md)
