# Photo Organizer V2 - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd /Users/myee/repos/biborganizer
pip install -r requirements.txt
```

### 2. Authenticate with Google Cloud
```bash
gcloud auth application-default login
gcloud config set project itpc-gcp-product-all-claude
```

### 3. Enable Claude on Vertex AI
Visit: https://console.cloud.google.com/vertex-ai/publishers/anthropic/model-garden/claude-3-5-sonnet?project=itpc-gcp-product-all-claude

Click "Enable" if not already enabled.

### 4. Configure Environment
```bash
# Copy example config
cp .env.example .env

# Edit .env and set your project ID (already set for you):
# VERTEX_PROJECT_ID=itpc-gcp-product-all-claude
```

### 5. Choose Your Mode

#### Option A: Database Mode (For Known People)
```bash
# Step 1: Add people to database
python -m v2.cli_database

# Follow prompts to add people with reference photos

# Step 2: Organize photos
python -m v2.cli_organize ~/path/to/photos --dry-run  # Preview first!
python -m v2.cli_organize ~/path/to/photos             # Then execute
```

#### Option B: Auto-Cluster Mode (For Unknown People)
```bash
# Automatically group similar faces (no database needed)
python -m v2.cli_organize ~/path/to/photos --mode auto-cluster --dry-run
python -m v2.cli_organize ~/path/to/photos --mode auto-cluster
```

## Common Commands

### Database Management
```bash
# Interactive menu
python -m v2.cli_database

# What you can do:
# - Add person (provide name + reference photo)
# - Remove person
# - List all people
# - View person details
# - Database statistics
```

### Photo Organization
```bash
# Preview (no changes)
python -m v2.cli_organize SOURCE_DIR --dry-run

# Copy mode (keeps originals)
python -m v2.cli_organize SOURCE_DIR

# Move mode (relocates files)
python -m v2.cli_organize SOURCE_DIR --copy-or-move move

# Custom output directory
python -m v2.cli_organize SOURCE_DIR -o OUTPUT_DIR

# Auto-cluster mode
python -m v2.cli_organize SOURCE_DIR --mode auto-cluster

# Higher confidence threshold (stricter matching)
python -m v2.cli_organize SOURCE_DIR --confidence 0.8

# Undo organization
python -m v2.cli_organize -o OUTPUT_DIR --undo
```

## Output Structure

After running the organizer, photos will be organized:

**Database Mode:**
```
organized_photos/
├── John_Doe/              ← Photos with only John
├── Jane_Smith/            ← Photos with only Jane
├── Multiple_People/
│   ├── Jane_Smith_John_Doe/   ← Photos with both
│   └── Jane_Smith_Unknown/    ← Jane + stranger
├── Unknown_Faces/         ← Unrecognized people
├── No_Faces_Detected/     ← Landscapes, etc.
└── organization_log.json  ← Detailed report
```

**Auto-Cluster Mode:**
```
organized_photos/
├── Person_1/              ← First discovered person
├── Person_2/              ← Second discovered person
├── Person_3/              ← Third discovered person
├── Multiple_People/       ← Photos with multiple faces
├── No_Faces_Detected/     ← Landscapes, etc.
└── organization_log.json  ← Detailed report
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- HEIC (.heic, .heif)

## Tips

1. **Always use --dry-run first** to preview the organization
2. **Start with a small test set** (10-20 photos) to verify it works
3. **Use copy mode initially** so you can always go back to originals
4. **Adjust confidence threshold** if you get too many false matches/misses
5. **In auto-cluster mode**, rename Person_N folders after reviewing

## Troubleshooting

### "Configuration error: VERTEX_PROJECT_ID is required"
Edit `.env` and set your project ID.

### "Authentication error"
Run: `gcloud auth application-default login`

### "Model not available"
Enable Anthropic models in Vertex AI Model Garden (see step 3 above)

### "HEIC images not loading"
Install: `pip install pillow-heif`

### "Too many unknown faces"
Lower the confidence threshold: `--confidence 0.6`

### "Too many false matches"
Raise the confidence threshold: `--confidence 0.8`

## Getting Help

```bash
# View all options
python -m v2.cli_organize --help

# View database options
python -m v2.cli_database
```

## Full Documentation

See `README_V2.md` for complete documentation.

## Example Workflow

```bash
# 1. Test with a small sample
mkdir ~/test_photos
cp ~/Photos/*.jpg ~/test_photos  # Copy a few test photos

# 2. Preview organization
python -m v2.cli_organize ~/test_photos --dry-run

# 3. If it looks good, run for real
python -m v2.cli_organize ~/test_photos

# 4. Check results
ls -R organized_photos/

# 5. If happy, run on full library
python -m v2.cli_organize ~/Photos -o ~/OrganizedPhotos --dry-run
python -m v2.cli_organize ~/Photos -o ~/OrganizedPhotos

# 6. If something went wrong, undo
python -m v2.cli_organize -o ~/OrganizedPhotos --undo
```

That's it! You're ready to organize your photos with Claude.
