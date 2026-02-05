# Setup Summary - Vertex AI & Model Selection

## What's Been Configured

✅ **Vertex AI Authentication** - Ready to use Google Cloud Platform
✅ **Multiple Model Support** - Choose from 5 different Claude models
✅ **Virtual Environment** - Dependencies installed and isolated
✅ **Installation Test** - All checks passing

## Current Configuration

Your `.env` file is set up for:
- **Authentication:** Google Cloud Vertex AI
- **Model:** Claude Sonnet 4.5 (recommended)
- **Region:** us-east5

## Next Steps to Complete Setup

### 1. Update Your GCP Project ID

Edit `.env` and replace `your-gcp-project-id` with your actual Google Cloud project ID:

```bash
nano .env
```

Change this line:
```
VERTEX_PROJECT_ID=your-gcp-project-id
```

To your actual project ID, for example:
```
VERTEX_PROJECT_ID=my-photo-project-123456
```

### 2. Authenticate with Google Cloud

If you haven't already, authenticate with Google Cloud:

```bash
# Login to GCP
gcloud auth application-default login

# Verify your project
gcloud config get-value project

# If needed, set your project
gcloud config set project YOUR_PROJECT_ID

# Enable Vertex AI API (if not already enabled)
gcloud services enable aiplatform.googleapis.com
```

### 3. Verify Setup

Test that everything works:

```bash
source venv/bin/activate
python test_installation.py
```

You should see all checkmarks (✓).

### 4. Start Using the Photo Organizer

```bash
# Add people to the database
python manage_database.py

# Test with a small set of photos
python organize.py ~/path/to/test/photos --dry-run

# Actually organize photos
python organize.py ~/path/to/photos
```

## Authentication Options

You have two authentication methods available:

### Option A: Vertex AI (Currently Configured)

**Pros:**
- Integrated with Google Cloud billing
- Can use existing GCP credits
- Centralized cloud management
- Service account support for automation

**Cons:**
- Requires GCP setup
- Regional availability may vary

**Configuration (.env):**
```
USE_VERTEX_AI=true
VERTEX_PROJECT_ID=your-project-id
VERTEX_REGION=us-east5
CLAUDE_MODEL=sonnet-4.5
```

### Option B: Direct Anthropic API

**Pros:**
- Simple setup (just API key)
- Direct access to all models
- No cloud provider dependencies

**Cons:**
- Separate billing from GCP
- Requires Anthropic account

**To switch to Anthropic API:**

Edit `.env`:
```
USE_VERTEX_AI=false
ANTHROPIC_API_KEY=sk-ant-api03-xxx...
CLAUDE_MODEL=sonnet-4.5
```

## Model Selection

You can use any of these models:

| Model | Best For | Cost | Speed |
|-------|----------|------|-------|
| **sonnet-4.5** ⭐ | Recommended - best balance | $$ | Fast |
| haiku-3.5 | Budget / large libraries | $ | Fastest |
| sonnet-3.7 | Good alternative | $$ | Fast |
| opus-3.5 | High quality | $$$ | Medium |
| opus-4.5 | Maximum accuracy | $$$ | Medium |

**To change models**, edit `.env`:
```
CLAUDE_MODEL=haiku-3.5    # For budget
CLAUDE_MODEL=sonnet-4.5   # For balance (default)
CLAUDE_MODEL=opus-4.5     # For maximum accuracy
```

See [MODEL_SELECTION.md](MODEL_SELECTION.md) for detailed comparison.

## File Structure

Your project now includes:

```
biborganizer/
├── .env                      # Your configuration (DO NOT COMMIT)
├── .env.example             # Template for others
├── claude_client.py         # API integration (Vertex + Anthropic)
├── face_database.py         # Person management
├── photo_organizer.py       # Core organization logic
├── manage_database.py       # Database CLI tool
├── organize.py              # Main CLI tool
├── test_installation.py     # Installation verification
├── config.json              # Default settings
├── requirements.txt         # Python dependencies
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start guide
├── VERTEX_AI_SETUP.md       # Vertex AI detailed setup
├── MODEL_SELECTION.md       # Model comparison guide
└── venv/                    # Virtual environment
```

## Common Commands

**Always activate virtual environment first:**
```bash
source venv/bin/activate
```

**Manage face database:**
```bash
python manage_database.py
```

**Organize photos (preview):**
```bash
python organize.py ~/Pictures/MyPhotos --dry-run
```

**Organize photos (copy mode):**
```bash
python organize.py ~/Pictures/MyPhotos
```

**Organize photos (move mode):**
```bash
python organize.py ~/Pictures/MyPhotos --mode move
```

**Adjust confidence threshold:**
```bash
python organize.py ~/Pictures/MyPhotos --confidence 0.8
```

**Undo organization:**
```bash
python organize.py -o organized_photos --undo
```

## Troubleshooting

### "VERTEX_PROJECT_ID not found"
→ Update `.env` with your actual GCP project ID

### "Permission denied" or "403 Forbidden"
→ Run: `gcloud auth application-default login`
→ Verify Vertex AI API is enabled: `gcloud services enable aiplatform.googleapis.com`

### "Model not found" error
→ Check model name in `.env` matches available models
→ Verify your region supports the model
→ See available regions: https://cloud.google.com/vertex-ai/docs/general/locations

### "No module named 'anthropic'"
→ Activate virtual environment: `source venv/bin/activate`
→ If still failing: `pip install -r requirements.txt`

### Wrong authentication method
→ Check `USE_VERTEX_AI` setting in `.env`
→ Make sure you have the right credentials configured

## Cost Management

**Estimate costs before processing:**

1. Start with dry-run mode: `--dry-run`
2. Test on small batch first (10-20 photos)
3. Calculate: `(number of photos × 2 API calls × cost per call)`

**Cost per call by model (approximate):**
- Haiku 3.5: $0.0015 per call
- Sonnet 3.7/4.5: $0.0075 per call
- Opus 3.5/4.5: $0.0375 per call

**Example for 1000 photos:**
- Haiku: ~$3
- Sonnet: ~$15
- Opus: ~$75

**Monitor costs:**
- GCP Console → Vertex AI → Usage
- Set up budget alerts in GCP

## Security Best Practices

1. ✅ `.env` is in `.gitignore` (never commit it)
2. ✅ Use service accounts for production
3. ✅ Enable audit logging in GCP
4. ✅ Set up budget alerts
5. ✅ Regularly rotate credentials
6. ✅ Use separate projects for dev/prod

## Documentation

- **Full documentation:** [README.md](README.md)
- **Quick start:** [QUICKSTART.md](QUICKSTART.md)
- **Vertex AI setup:** [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md)
- **Model selection:** [MODEL_SELECTION.md](MODEL_SELECTION.md)

## Support

If you encounter issues:

1. Run installation test: `python test_installation.py`
2. Check documentation in the files above
3. Verify GCP authentication: `gcloud auth list`
4. Check API is enabled: `gcloud services list --enabled | grep aiplatform`

## You're Ready!

Once you've updated your `VERTEX_PROJECT_ID` and authenticated with `gcloud`, you're ready to:

1. Add people to the database
2. Organize your photos
3. Save hours of manual sorting!

Happy organizing! 📸
