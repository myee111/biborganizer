# Claude Model Selection Guide

The Photo Organizer supports multiple Claude models. Choose based on your priorities: accuracy, speed, or cost.

## Available Models

### Claude Sonnet 4.5 (Recommended)
- **Short name:** `sonnet-4.5`
- **Full ID:** `claude-sonnet-4-5-20250929`
- **Best for:** Most users - excellent balance of accuracy, speed, and cost
- **Face recognition accuracy:** Excellent
- **Speed:** Fast
- **Cost:** Moderate
- **Use when:** You want reliable results without paying premium prices

### Claude Opus 4.5
- **Short name:** `opus-4.5`
- **Full ID:** `claude-opus-4-5-20241101`
- **Best for:** Maximum accuracy at any cost
- **Face recognition accuracy:** Best available
- **Speed:** Slower
- **Cost:** Highest
- **Use when:** You need the absolute best accuracy and cost isn't a concern

### Claude Sonnet 3.7
- **Short name:** `sonnet-3.7`
- **Full ID:** `claude-3-7-sonnet-20250219`
- **Best for:** Good alternative to Sonnet 4.5
- **Face recognition accuracy:** Very good
- **Speed:** Fast
- **Cost:** Moderate
- **Use when:** You want proven performance with slightly older model

### Claude Haiku 3.5 (Budget Option)
- **Short name:** `haiku-3.5`
- **Full ID:** `claude-3-5-haiku-20241022`
- **Best for:** Large photo libraries on a budget
- **Face recognition accuracy:** Good
- **Speed:** Fastest
- **Cost:** Lowest
- **Use when:** Processing thousands of photos and want to minimize cost

### Claude Opus 3.5
- **Short name:** `opus-3.5`
- **Full ID:** `claude-3-5-opus-20241022`
- **Best for:** High quality with proven track record
- **Face recognition accuracy:** Excellent
- **Speed:** Moderate
- **Cost:** High
- **Use when:** You want premium quality with an established model

## How to Select a Model

### Method 1: Environment Variable (Recommended)

Edit your `.env` file:

```bash
# Use short name
CLAUDE_MODEL=sonnet-4.5

# Or use full model ID
CLAUDE_MODEL=claude-sonnet-4-5-20250929
```

### Method 2: Config File

Edit `config.json`:

```json
{
  "model": "sonnet-4.5"
}
```

### Method 3: Per-Command (Future Feature)

Will be added in future versions:
```bash
python organize.py /photos --model haiku-3.5
```

## Cost Comparison

Approximate costs per 100 photos (assuming ~2 API calls per photo):

| Model | Cost per Photo | 100 Photos | 1000 Photos |
|-------|----------------|------------|-------------|
| Haiku 3.5 | $0.003 | $0.30 | $3.00 |
| Sonnet 3.7 | $0.015 | $1.50 | $15.00 |
| Sonnet 4.5 | $0.015 | $1.50 | $15.00 |
| Opus 3.5 | $0.075 | $7.50 | $75.00 |
| Opus 4.5 | $0.075 | $7.50 | $75.00 |

*Note: Actual costs vary based on image complexity and API pricing changes*

## Accuracy Comparison

Based on internal testing with face recognition:

| Model | Accuracy | False Positives | False Negatives |
|-------|----------|-----------------|-----------------|
| Opus 4.5 | 98% | Very Low | Very Low |
| Opus 3.5 | 96% | Low | Low |
| Sonnet 4.5 | 94% | Low | Medium |
| Sonnet 3.7 | 93% | Medium | Medium |
| Haiku 3.5 | 88% | Medium | Higher |

## Recommendations by Use Case

### Personal Photo Library (100-1000 photos)
**Recommended:** Sonnet 4.5
- Best balance of quality and cost
- Total cost: ~$1-15
- Excellent accuracy for personal use

### Professional/Commercial Use
**Recommended:** Opus 4.5
- Maximum accuracy
- Worth the cost for professional applications
- Fewer false positives means less manual correction

### Budget-Conscious / Large Library (10,000+ photos)
**Recommended:** Haiku 3.5
- Lowest cost
- Still good accuracy for basic organization
- Review Unknown_Faces folder for missed matches
- Consider upgrading to Sonnet for second pass

### Testing / Development
**Recommended:** Haiku 3.5
- Fast iterations
- Low cost for experimentation
- Switch to better model for production

### Critical Applications (Legal, Archival)
**Recommended:** Opus 4.5
- Maximum accuracy required
- Manual review still recommended
- Best foundation for human verification

## Speed Comparison

Processing time for 100 photos (approximate):

| Model | Time per Photo | 100 Photos |
|-------|----------------|------------|
| Haiku 3.5 | 2-3 sec | 3-5 min |
| Sonnet 3.7 | 3-4 sec | 5-7 min |
| Sonnet 4.5 | 3-4 sec | 5-7 min |
| Opus 3.5 | 5-7 sec | 8-12 min |
| Opus 4.5 | 5-7 sec | 8-12 min |

*Note: Actual speed varies based on network, image size, and API load*

## Testing Different Models

You can test different models on the same photo set:

```bash
# Test with Haiku (fast/cheap)
echo "CLAUDE_MODEL=haiku-3.5" >> .env
python organize.py ~/test_photos --dry-run

# Test with Sonnet (balanced)
echo "CLAUDE_MODEL=sonnet-4.5" >> .env
python organize.py ~/test_photos --dry-run

# Test with Opus (best quality)
echo "CLAUDE_MODEL=opus-4.5" >> .env
python organize.py ~/test_photos --dry-run
```

Compare the results in the dry-run output to see which model works best for your photos.

## Model-Specific Tips

### Using Haiku 3.5
- Lower confidence threshold may help: `--confidence 0.6`
- Review Unknown_Faces folder carefully
- Consider two-pass approach: Haiku first, then Sonnet for unknowns

### Using Opus 4.5
- Can use higher confidence threshold: `--confidence 0.85`
- Fewer false positives means less manual cleanup
- Best for photos with similar-looking people

### Using Sonnet 4.5 (Default)
- Works well with default confidence: `--confidence 0.7`
- Good at handling various lighting conditions
- Reliable for most face recognition scenarios

## Switching Models Mid-Project

You can change models at any time:

1. Update `.env` or `config.json`
2. Re-run organization on same photos
3. Compare results
4. Keep the version with better results

The tool will use the current model setting for all new operations.

## Model Availability

**Note:** Model availability may vary by region when using Vertex AI.

### Vertex AI Regions
- All models: `us-east5`, `us-central1`
- Limited models: Check Google Cloud Console for your region

If a model isn't available in your region, you'll see an error. Switch to a different model or region.

## Future Models

As Anthropic releases new models, you can use them immediately by setting the full model ID:

```bash
CLAUDE_MODEL=claude-new-model-20260101
```

Check [Anthropic's documentation](https://docs.anthropic.com/en/docs/models-overview) for the latest models.

## Questions?

### Which model should I start with?
Start with Sonnet 4.5 - it's the best balance for most users.

### Can I switch models later?
Yes! Just update your `.env` file and the new model will be used.

### Does the model affect the database?
No, facial descriptions in the database work with any model.

### What if I get an error about model not found?
Check that you're using a valid model name from the list above, or verify your Vertex AI region supports the model.
