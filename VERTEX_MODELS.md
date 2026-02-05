# Vertex AI Model Availability

Vertex AI uses different model identifiers than the direct Anthropic API. This guide explains which models are available and how to use them.

## Available Models on Vertex AI

### Claude 3.5 Sonnet (Recommended)
- **Short name:** `sonnet-3.5`
- **Vertex ID:** `claude-3-5-sonnet@20241022`
- **Best for:** Most use cases - excellent quality and speed
- **Availability:** ✅ Available now

### Claude 3.5 Haiku
- **Short name:** `haiku-3.5`
- **Vertex ID:** `claude-3-5-haiku@20241022`
- **Best for:** Budget-conscious users, large photo libraries
- **Availability:** ✅ Available now

### Claude 3 Opus
- **Short name:** `opus-3`
- **Vertex ID:** `claude-3-opus@20240229`
- **Best for:** Maximum quality for critical applications
- **Availability:** ✅ Available now

## Models NOT Yet Available on Vertex AI

These models are only available via direct Anthropic API:
- ❌ Claude Sonnet 4.5 (`sonnet-4.5`)
- ❌ Claude Opus 4.5 (`opus-4.5`)
- ❌ Claude Sonnet 3.7 (`sonnet-3.7`)

**Note:** If you specify these models while using Vertex AI, the tool will automatically fall back to the closest available model (Claude 3.5 Sonnet) with a warning.

## Configuration

### Current Setup (.env)
```bash
USE_VERTEX_AI=true
VERTEX_PROJECT_ID=itpc-gcp-product-all-claude
VERTEX_REGION=us-east5
CLAUDE_MODEL=sonnet-3.5
```

### Change Model

Edit your `.env` file:

```bash
# For best quality (recommended)
CLAUDE_MODEL=sonnet-3.5

# For budget/speed
CLAUDE_MODEL=haiku-3.5

# For maximum quality
CLAUDE_MODEL=opus-3
```

Or use the full Vertex AI model identifier:

```bash
CLAUDE_MODEL=claude-3-5-sonnet@20241022
```

## Model Comparison

| Model | Quality | Speed | Cost | Recommended For |
|-------|---------|-------|------|-----------------|
| **Sonnet 3.5** | Excellent | Fast | $$ | Most users |
| Haiku 3.5 | Good | Fastest | $ | Large libraries |
| Opus 3 | Best | Medium | $$$ | Critical work |

## Regional Availability

Vertex AI model availability varies by region. Your configured region: **us-east5**

### Models by Region

**us-east5** (recommended):
- ✅ All models available

**us-central1**:
- ✅ All models available

**europe-west1**:
- ✅ All models available

**Other regions**:
- Check availability in GCP Console

To change region, edit `.env`:
```bash
VERTEX_REGION=us-central1
```

## Cost Comparison (Vertex AI)

Approximate costs for 1000 photos (~2 API calls per photo):

| Model | Per Photo | 1000 Photos |
|-------|-----------|-------------|
| Haiku 3.5 | $0.003 | $3 |
| Sonnet 3.5 | $0.015 | $15 |
| Opus 3 | $0.075 | $75 |

## Performance Tips

### For Budget (Haiku 3.5)
```bash
CLAUDE_MODEL=haiku-3.5
```
Run with lower confidence threshold:
```bash
python organize.py ~/photos --confidence 0.6
```

### For Quality (Sonnet 3.5)
```bash
CLAUDE_MODEL=sonnet-3.5
```
Use default confidence:
```bash
python organize.py ~/photos --confidence 0.7
```

### For Critical Work (Opus 3)
```bash
CLAUDE_MODEL=opus-3
```
Use higher confidence threshold:
```bash
python organize.py ~/photos --confidence 0.85
```

## Switching to Anthropic API for Newer Models

If you need Sonnet 4.5, Opus 4.5, or Sonnet 3.7, switch to direct Anthropic API:

1. Edit `.env`:
```bash
USE_VERTEX_AI=false
ANTHROPIC_API_KEY=sk-ant-api03-xxx...
CLAUDE_MODEL=sonnet-4.5
```

2. Test the setup:
```bash
source venv/bin/activate
python test_installation.py
```

## Troubleshooting

### Error: "404 - Model not found"

**Cause:** Using Anthropic API model ID with Vertex AI

**Solution:** Use Vertex AI model identifiers:
- ❌ `claude-sonnet-4-5-20250929`
- ✅ `claude-3-5-sonnet@20241022`

Or use short names (automatically resolved):
- ✅ `sonnet-3.5`

### Error: "Model not available in region"

**Cause:** Model not deployed in your Vertex region

**Solution 1:** Switch to us-east5:
```bash
VERTEX_REGION=us-east5
```

**Solution 2:** Use a different model available in your region

### Fallback Warning

If you see:
```
Note: sonnet-4.5 not yet available on Vertex AI. Using claude-3-5-sonnet@20241022 instead.
```

This is normal - the tool automatically uses the best available model.

## When to Use Which Model

### Personal Photo Library (100-1000 photos)
**Use:** Sonnet 3.5
```bash
CLAUDE_MODEL=sonnet-3.5
```
Cost: ~$1-15, excellent accuracy

### Large Library (10,000+ photos)
**Use:** Haiku 3.5
```bash
CLAUDE_MODEL=haiku-3.5
```
Cost: ~$30, good accuracy, fast processing

### Professional/Archival Work
**Use:** Opus 3
```bash
CLAUDE_MODEL=opus-3
```
Cost: ~$75 per 1000 photos, best accuracy

## Checking Current Configuration

Run the test to see your current setup:
```bash
source venv/bin/activate
python test_installation.py
```

Look for:
```
Authentication mode: Vertex AI
✓ VERTEX_PROJECT_ID found: itpc-gcp-product-all-claude
✓ VERTEX_REGION: us-east5
```

## Updates

As new models become available on Vertex AI, update your configuration:

1. Check Anthropic's Vertex AI documentation
2. Update `CLAUDE_MODEL` in `.env`
3. Test with `--dry-run`

## Questions?

- **Which model is best?** → Sonnet 3.5 for most users
- **Can I use Sonnet 4.5?** → Not on Vertex AI yet; switch to Anthropic API
- **How do I minimize cost?** → Use Haiku 3.5
- **Which is most accurate?** → Opus 3 (on Vertex AI)
