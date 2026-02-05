# Photo Organizer

Automatically organize your photo library by identifying people using Claude Vision API. This tool scans photos, recognizes faces, and organizes them into person-specific directories.

## Features

- **Face Recognition**: Uses Claude Sonnet 4.5 Vision API for accurate face identification
- **Privacy-Focused**: All face descriptions stored locally, no biometric data or embeddings
- **Flexible Organization**: Handles single-person photos, group photos, unknown faces, and landscapes
- **Safe Operations**: Default copy mode preserves originals, with undo functionality
- **HEIC Support**: Automatically handles iPhone photos and other formats
- **Batch Processing**: Efficiently processes large photo libraries with progress tracking

## Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd biborganizer

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 2. Register Known People

Before organizing photos, add people to the face database:

```bash
python manage_database.py
```

Follow the interactive menu to:
- Add people with reference photos
- View registered people
- Manage the database

### 3. Organize Your Photos

```bash
# Basic usage (copy mode)
python organize.py /path/to/your/photos

# Preview without changes
python organize.py /path/to/your/photos --dry-run

# Move files instead of copying
python organize.py /path/to/your/photos --mode move

# Custom output directory
python organize.py /path/to/your/photos -o /path/to/organized
```

## How It Works

### Two-Phase Workflow

**Phase 1: Database Building**
1. Register known people with reference photos
2. Claude analyzes each reference photo and generates detailed facial descriptions
3. Descriptions are stored locally in `face_database.json`

**Phase 2: Photo Organization**
1. Scan your photo directory for images
2. Claude analyzes each photo and detects all faces
3. Compare detected faces against the database
4. Organize photos into directories based on who's in them

### Directory Structure

After organization, your photos will be organized like this:

```
organized_photos/
├── John_Doe/                    # Photos with only John
│   ├── photo1.jpg
│   ├── photo2.jpg
├── Jane_Smith/                  # Photos with only Jane
│   ├── photo3.jpg
├── Multiple_People/             # Group photos
│   ├── Jane_Smith_John_Doe/    # Photos with both
│   │   ├── photo4.jpg
├── Unknown_Faces/               # Unrecognized people
│   ├── photo5.jpg
├── No_Faces_Detected/           # Landscapes, objects, etc.
│   ├── landscape1.jpg
├── organization_log.json        # Detailed statistics
└── .original_paths.json         # For undo functionality
```

## Command-Line Reference

### organize.py

Main tool for organizing photos.

```bash
python organize.py <source_dir> [OPTIONS]

Options:
  -o, --output DIR          Output directory (default: ./organized_photos)
  --mode {copy,move}        Copy or move files (default: copy)
  --dry-run                 Preview without making changes
  -r, --recursive           Scan subdirectories (default: True)
  --confidence FLOAT        Minimum confidence threshold (default: 0.7)
  --undo                    Undo previous organization
```

**Examples:**

```bash
# Preview organization
python organize.py ~/Pictures/Vacation --dry-run

# Organize with custom output
python organize.py ~/Pictures/Vacation -o ~/Pictures/Organized

# Move files instead of copying
python organize.py ~/Pictures/Vacation --mode move

# Adjust confidence threshold (higher = stricter matching)
python organize.py ~/Pictures/Vacation --confidence 0.85

# Undo organization
python organize.py -o ~/Pictures/Organized --undo
```

### manage_database.py

Interactive tool for managing the face database.

```bash
python manage_database.py
```

**Menu Options:**
1. Add person to database
2. Remove person from database
3. List all people
4. View person details
5. Database statistics
6. Validate database
7. Exit

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "confidence_threshold": 0.7,        // Similarity threshold (0.0-1.0)
  "supported_formats": [...],         // Image formats to process
  "max_image_size_mb": 5.0,          // Max image size for API
  "max_image_dimension": 8000,       // Max pixel dimension
  "model": "claude-sonnet-4-5-20250929",
  "batch_size": 50,                   // Future use
  "retry_attempts": 3,                // API retry count
  "retry_delay_seconds": 2            // Retry delay
}
```

## Tips for Best Results

### Reference Photos

- Use clear, well-lit photos
- Face should be clearly visible
- Front-facing or slight angle works best
- Avoid sunglasses, masks, or heavy shadows
- One person per reference photo

### Confidence Threshold

- **0.7** (default): Balanced - good for most cases
- **0.8-0.9**: Strict - fewer false positives, may miss some matches
- **0.5-0.6**: Lenient - catches more matches, may have false positives

### Processing Large Libraries

- Start with `--dry-run` to preview
- Process in batches if you have thousands of photos
- Use `copy` mode first to preserve originals
- Review `Unknown_Faces` directory to identify missing people

## Troubleshooting

### "No known people registered"

**Solution**: Run `python manage_database.py` and add people first.

### "ANTHROPIC_API_KEY not found"

**Solution**: Create a `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
```

### HEIC images not working

**Solution**: Install HEIC support:
```bash
pip install pillow-heif
```

### High API costs

**Tips to reduce costs:**
- Use `--dry-run` first to estimate
- Process smaller batches
- Adjust `--confidence` threshold to reduce re-processing
- Build a complete database before organizing

### Poor face matching accuracy

**Solutions:**
- Add more reference photos for each person
- Use clearer reference photos
- Adjust `--confidence` threshold
- Check that reference photos are front-facing

### "Reference image not found" error

**Solution**: Use absolute paths or ensure the reference image still exists at the original location.

## Privacy & Data

### What Gets Stored

- **Locally**: Facial descriptions (text), reference image paths, person names
- **Not Stored**: Biometric templates, embeddings, or face vectors
- **Cloud**: Images sent to Claude API for analysis (not retained by Anthropic)

### Data Control

- All data in `face_database.json` - you can delete it anytime
- No cloud storage of your face database
- You control all reference images
- API calls use Anthropic's privacy policy

### Deleting Your Data

```bash
# Remove the database
rm face_database.json

# Remove organized photos
rm -rf organized_photos
```

## Cost Estimates

Claude Vision API pricing (approximate):

- **Face database**: ~$0.03 per person (one-time)
- **Photo organization**: ~$0.01-0.02 per photo
- **100 photos**: ~$1-2
- **1,000 photos**: ~$10-20
- **10,000 photos**: ~$100-200

Actual costs vary based on image sizes and complexity.

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- HEIC (.heic) - requires `pillow-heif`

## Requirements

- Python 3.8+
- Anthropic API key
- Internet connection (for API calls)
- Sufficient disk space for organized copies

## Limitations

- Requires internet for Claude API
- Processing speed depends on photo count
- Accuracy depends on photo quality and reference photos
- May not recognize people with significant appearance changes
- Group photos with many people may be slower

## Future Enhancements

Potential features (not currently implemented):

- Web UI for reviewing results
- Automatic face clustering for unknown people
- Organization by date + person
- EXIF metadata extraction
- Duplicate photo detection
- Parallel processing for speed
- Export to photo management apps

## License

This project is provided as-is for personal use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the `organization_log.json` for errors
3. Validate your database with `manage_database.py`
4. Check Anthropic API status

## Acknowledgments

- Built with Claude Sonnet 4.5 Vision API
- Uses Pillow for image processing
- Progress tracking with tqdm
