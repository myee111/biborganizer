# Gemini Setup Guide

Your photo organizer is now configured to use **Google Gemini** instead of Claude!

## Why Gemini?

✅ **Works immediately** - No waiting for GCP approval
✅ **Free tier available** - 1500 requests/day for free
✅ **Fast** - Gemini Flash is very quick
✅ **High quality** - Excellent for face recognition
✅ **Easy setup** - Just need an API key

## Step 1: Get Your Gemini API Key (2 minutes)

1. **Go to Google AI Studio:**
   ```
   https://aistudio.google.com/apikey
   ```

2. **Sign in with your Google account**

3. **Click "Create API Key"**

4. **Copy the API key** (starts with `AIza...`)

## Step 2: Add API Key to .env

```bash
nano .env
```

On line 7, replace:
```
GEMINI_API_KEY=GET_YOUR_KEY_FROM_AISTUDIO_GOOGLE_COM
```

With your actual key:
```
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Save: `Ctrl+X`, `Y`, `Enter`

## Step 3: Test It

```bash
source venv/bin/activate
python test_installation.py
```

You should see:
```
✓ Using Gemini
✓ All tests passed!
```

## Step 4: Start Organizing Photos!

```bash
# Add people to database
python manage_database.py

# Test organization
python organize.py ~/Photos --dry-run

# Actually organize
python organize.py ~/Photos
```

## Available Models

| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| **flash** (default) | Fastest | Very Good | Free* |
| flash-1.5 | Fast | Good | Free* |
| pro | Medium | Excellent | Free* |
| pro-2 | Fast | Excellent | Free* |

*Free tier: 1500 requests/day. After that, very low cost (~$0.001-0.01 per image)

### Change Model

Edit `.env`:
```bash
GEMINI_MODEL=flash      # Fastest (default)
GEMINI_MODEL=pro        # Best quality
GEMINI_MODEL=pro-2      # Latest experimental
```

## Cost Estimates

### Free Tier (1500 requests/day)
- Enough for ~750 photos/day
- Perfect for personal use
- Resets daily

### After Free Tier
- Flash: ~$0.001 per photo
- Pro: ~$0.005 per photo
- 1000 photos: $1-5
- Much cheaper than Claude!

## Troubleshooting

### "GEMINI_API_KEY not found"
→ Make sure you edited `.env` and added your API key

### "Invalid API key"
→ Double-check the key from https://aistudio.google.com/apikey
→ Make sure there are no extra spaces

### "Quota exceeded"
→ You've used your free tier (1500 requests/day)
→ Wait for daily reset or enable billing

### Want to use Claude instead?
Edit `.env`:
```bash
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxx...
```

## Comparison: Gemini vs Claude

| Feature | Gemini | Claude |
|---------|--------|--------|
| Setup time | 2 minutes | 5 minutes |
| Free tier | 1500/day | $5 credit |
| Cost (after free) | $1-5 per 1000 | $10-20 per 1000 |
| Speed | Very fast | Fast |
| Quality | Excellent | Excellent |
| Best for | Most users | Max accuracy |

## You're All Set!

Once you add your Gemini API key, you can start organizing photos immediately!

```bash
# Quick start:
nano .env  # Add your GEMINI_API_KEY
source venv/bin/activate
python manage_database.py  # Add people
python organize.py ~/Photos --dry-run  # Test
python organize.py ~/Photos  # Organize!
```

Enjoy your photo organizer powered by Google Gemini! 🎉
