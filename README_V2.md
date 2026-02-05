# Photo Organizer V2 - Simplified Architecture

A streamlined photo organization tool using Claude via Vertex AI for facial recognition. Automatically organizes your photo library by detecting and identifying people in photos.

## Features

- **Two Organization Modes:**
  - **Database Mode**: Organize photos by matching faces against pre-registered people
  - **Auto-Cluster Mode**: Automatically group similar faces without a database (NEW!)

- **Facial Recognition**: Uses Claude's vision capabilities via Google Cloud Vertex AI
- **Multiple File Formats**: Supports JPG, PNG, GIF, WebP, HEIC
- **Safe Operations**: Copy or move modes with undo functionality
- **Detailed Reports**: JSON logs of all organization operations

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Google Cloud account with Vertex AI enabled
- Anthropic models enabled in Vertex AI Model Garden

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Enable Anthropic Models on Vertex AI

1. Go to [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/publishers/anthropic/model-garden/claude-3-5-sonnet)
2. Select your project: `itpc-gcp-product-all-claude`
3. Click "Enable" and accept terms of service
4. Available models:
   - `claude-3-5-sonnet@20240620` (recommended)
   - `claude-3-opus@20240229`
   - `claude-3-5-haiku@20241022`

### 4. Authenticate with Google Cloud

```bash
# Authenticate
gcloud auth application-default login

# Set your project
gcloud config set project itpc-gcp-product-all-claude
```

### 5. Configure Environment

Create a `.env` file in the project root:

```env
VERTEX_PROJECT_ID=itpc-gcp-product-all-claude
VERTEX_REGION=us-central1
CLAUDE_MODEL=claude-3-5-sonnet@20240620
CONFIDENCE_THRESHOLD=0.7
```

### 6. Choose Your Workflow

#### Option A: Database Mode (Recommended for family/friends)

```bash
# 1. Add people to database
python -m v2.cli_database

# 2. Organize photos
python -m v2.cli_organize ~/Photos --dry-run  # Preview
python -m v2.cli_organize ~/Photos             # Execute
```

#### Option B: Auto-Cluster Mode (For events/unknown people)

```bash
# Automatically group photos by similar faces
python -m v2.cli_organize ~/Photos --mode auto-cluster --dry-run  # Preview
python -m v2.cli_organize ~/Photos --mode auto-cluster             # Execute
```

## Usage Guide

### Database Management

Add people with reference photos:

```bash
python -m v2.cli_database
```

Interactive menu options:
1. Add person to database
2. Remove person from database
3. List all people
4. View person details
5. Database statistics
6. Validate database
7. Exit

### Photo Organization

Basic usage:

```bash
# Preview organization (recommended first step)
python -m v2.cli_organize /path/to/photos --dry-run

# Organize photos (copy mode - keeps originals)
python -m v2.cli_organize /path/to/photos

# Auto-cluster mode (no database needed)
python -m v2.cli_organize /path/to/photos --mode auto-cluster

# Move files instead of copying
python -m v2.cli_organize /path/to/photos --copy-or-move move

# Custom output directory
python -m v2.cli_organize /path/to/photos -o /path/to/organized

# Adjust confidence threshold (0.0-1.0)
python -m v2.cli_organize /path/to/photos --confidence 0.8

# Undo organization
python -m v2.cli_organize -o /path/to/organized --undo
```

### Output Structure

After organization, your photos will be organized like this:

**Database Mode:**
```
organized_photos/
├── John_Doe/              # Photos with only John
│   ├── IMG_001.jpg
│   └── IMG_002.jpg
├── Jane_Smith/            # Photos with only Jane
│   └── IMG_003.jpg
├── Multiple_People/
│   ├── Jane_Smith_John_Doe/  # Photos with both
│   │   └── IMG_004.jpg
│   └── Jane_Smith_Unknown/   # Jane + unknown person
│       └── IMG_005.jpg
├── Unknown_Faces/         # Unrecognized people
│   └── IMG_006.jpg
├── No_Faces_Detected/     # Landscapes, objects, etc.
│   └── IMG_007.jpg
└── organization_log.json  # Detailed report
```

**Auto-Cluster Mode:**
```
organized_photos/
├── Person_1/              # First discovered person
│   ├── IMG_001.jpg
│   └── IMG_002.jpg
├── Person_2/              # Second discovered person
│   └── IMG_003.jpg
├── Person_3/              # Third discovered person
│   └── IMG_004.jpg
├── Multiple_People/       # Photos with multiple faces
│   └── IMG_005.jpg
├── No_Faces_Detected/     # Landscapes, objects, etc.
│   └── IMG_006.jpg
└── organization_log.json  # Detailed report
```

In auto-cluster mode, you can rename `Person_1`, `Person_2`, etc. folders after reviewing the photos.

## Architecture

The V2 architecture is significantly simplified compared to V1:

### Core Modules

- **config.py** (50 lines): Configuration management
- **image_utils.py** (100 lines): Image processing utilities
- **prompts.py** (30 lines): Centralized AI prompts
- **vertex_claude.py** (150 lines): Claude API client (Vertex AI only)
- **database.py** (250 lines): Face database management
- **organizer.py** (500 lines): Photo organization logic
- **cli_organize.py** (300 lines): Main CLI interface
- **cli_database.py** (200 lines): Database management CLI
- **test_suite.py** (150 lines): Unified test suite

**Total: ~1,730 lines** (down from ~2,400 lines in V1, a 28% reduction)

### Key Simplifications from V1

- ❌ Removed Gemini support
- ❌ Removed vision client abstraction layer
- ❌ Removed direct Anthropic API support (Vertex AI only)
- ❌ Removed multiple configuration methods
- ✅ Single AI provider (Claude via Vertex AI)
- ✅ Cleaner module structure
- ✅ Centralized prompts
- ✅ Unified test suite

## Configuration

All configuration is in `.env`:

```env
# Required
VERTEX_PROJECT_ID=your-gcp-project-id

# Optional (with defaults)
VERTEX_REGION=us-central1
CLAUDE_MODEL=claude-3-5-sonnet@20240620
CONFIDENCE_THRESHOLD=0.7
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest v2/test_suite.py

# Run with verbose output
pytest v2/test_suite.py -v

# Run specific test class
pytest v2/test_suite.py::TestConfig -v

# Skip integration tests (require API access)
pytest v2/test_suite.py -v -m "not integration"
```

## Troubleshooting

### Authentication Issues

```bash
# Verify authentication
gcloud auth application-default print-access-token

# Re-authenticate if needed
gcloud auth application-default login
```

### Model Not Available

If you get errors about model availability:
1. Go to [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/publishers/anthropic)
2. Enable the Anthropic models for your project
3. Accept the terms of service

### HEIC Images Not Loading

Install the HEIC converter:

```bash
pip install pillow-heif
```

On macOS, you may also need:

```bash
brew install libheif
```

### Configuration Errors

Verify your `.env` file:

```bash
python -c "from v2.config import load_config; print(load_config())"
```

## Requirements

See `requirements.txt`:

```
anthropic>=0.18.0
pillow>=10.0.0
python-dotenv>=1.0.0
tqdm>=4.65.0
pillow-heif>=0.10.0
pytest>=7.0.0
```

## Differences from V1

| Aspect | V1 | V2 |
|--------|----|----|
| Lines of code | ~2,400 | ~1,730 (-28%) |
| AI providers | Claude + Gemini | Claude only |
| Auth methods | API keys + Vertex | Vertex only |
| Organization modes | Database only | Database + Auto-cluster |
| Config files | .env (complex) | .env (simple) |
| Test files | 3 separate | 1 unified |
| Abstraction layers | vision_client wrapper | Direct imports |
| Code duplication | High | Low |
| Maintenance burden | High | Low |

## License

This is a personal tool for photo organization. Use at your own discretion.

## Support

For issues or questions:
1. Check this README
2. Review the code comments
3. Check the plan document for design decisions
