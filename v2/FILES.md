# Photo Organizer V2 - File Structure

## Complete File Listing

```
biborganizer/
├── v2/                              # NEW - V2 Implementation
│   ├── __init__.py                  # Package initialization
│   ├── config.py                    # Configuration management
│   ├── image_utils.py               # Image processing utilities
│   ├── prompts.py                   # Centralized AI prompts
│   ├── vertex_claude.py             # Claude Vertex AI client
│   ├── database.py                  # Face database management
│   ├── organizer.py                 # Photo organization logic
│   ├── cli_organize.py              # Main CLI interface
│   ├── cli_database.py              # Database management CLI
│   ├── test_suite.py                # Unified test suite
│   ├── IMPLEMENTATION_SUMMARY.md    # Implementation details
│   ├── QUICK_START.md               # Quick start guide
│   └── FILES.md                     # This file
│
├── README_V2.md                     # V2 Documentation
├── .env.example                     # Configuration template
├── requirements.txt                 # Updated dependencies
│
└── [V1 files kept as reference]
    ├── claude_client.py
    ├── gemini_client.py
    ├── vision_client.py
    ├── face_database.py
    ├── photo_organizer.py
    ├── organize.py
    ├── manage_database.py
    └── ...
```

## File Purposes

### Core V2 Modules

**v2/__init__.py** (246 lines)
- Package initialization
- Version information
- Module docstring

**v2/config.py** (~50 lines)
- Load configuration from .env
- Validate required settings
- Provide configuration defaults

**v2/image_utils.py** (~100 lines)
- Load images (including HEIC conversion)
- Resize and compress images for API
- Base64 encoding
- Format validation

**v2/prompts.py** (~30 lines)
- FACIAL_DESCRIPTION_PROMPT - Generate face descriptions
- DETECT_FACES_PROMPT - Find all faces in image
- COMPARE_FACES_PROMPT - Compare two face descriptions

**v2/vertex_claude.py** (~150 lines)
- Initialize AnthropicVertex client
- `analyze_image()` - Send image + prompt to Claude
- `generate_facial_description()` - Create face description
- `detect_faces()` - Find faces in image
- `compare_faces()` - Compare face similarity
- `extract_json()` - Parse JSON from responses

**v2/database.py** (~250 lines)
- `load_database()` / `save_database()` - Persistence
- `add_person()` / `remove_person()` - CRUD operations
- `list_people()` / `get_person()` - Queries
- `display_all_people()` - Formatted output
- `validate_database()` - Integrity checks

**v2/organizer.py** (~500 lines)
- `scan_directory_for_images()` - Find photos
- `identify_all_faces_in_image()` - Detect & match faces
- `create_organization_plan()` - Database mode planning
- `auto_cluster_photos()` - Auto-cluster mode (NEW)
- `execute_organization_plan()` - File operations
- `generate_organization_report()` - Create logs
- `undo_organization()` - Restore originals

**v2/cli_organize.py** (~300 lines)
- Main command-line interface
- Argument parsing (mode, confidence, etc.)
- Workflow orchestration
- Progress display
- User confirmations

**v2/cli_database.py** (~200 lines)
- Interactive database management menu
- Add/remove people workflows
- View database contents
- Statistics and validation

**v2/test_suite.py** (~150 lines)
- Unit tests for all modules
- Configuration tests
- Image utility tests
- Database operation tests
- Integration test stubs

### Documentation Files

**README_V2.md**
- Complete user guide
- Setup instructions
- Usage examples
- Architecture overview
- Troubleshooting

**v2/IMPLEMENTATION_SUMMARY.md**
- Implementation statistics
- Architecture highlights
- Comparison with V1
- Verification checklist

**v2/QUICK_START.md**
- 5-minute setup guide
- Common commands
- Example workflows
- Quick troubleshooting

**v2/FILES.md** (this file)
- Complete file structure
- File purposes
- Module organization

### Configuration Files

**.env.example**
- Template for environment variables
- All configuration options documented
- Default values shown

**requirements.txt**
- All Python dependencies
- Version constraints
- Updated with pytest

## Module Dependencies

### Import Graph

```
cli_organize.py
    imports: organizer, database, config
    
cli_database.py
    imports: database
    
organizer.py
    imports: vertex_claude, config
    
database.py
    imports: vertex_claude
    
vertex_claude.py
    imports: config, image_utils, prompts
    
config.py
    imports: (stdlib only)
    
image_utils.py
    imports: (stdlib + pillow)
    
prompts.py
    imports: (none - just strings)
    
test_suite.py
    imports: ALL modules (for testing)
```

### External Dependencies

From `requirements.txt`:
- anthropic>=0.18.0 - Claude API client
- google-cloud-aiplatform>=1.38.0 - Vertex AI
- pillow>=10.0.0 - Image processing
- python-dotenv>=1.0.0 - Environment variables
- tqdm>=4.65.0 - Progress bars
- pillow-heif>=0.10.0 - HEIC support
- pytest>=7.0.0 - Testing framework

## Running the Code

### Database Management
```bash
python -m v2.cli_database
```

Runs interactive menu from `v2/cli_database.py`

### Photo Organization
```bash
python -m v2.cli_organize SOURCE_DIR [OPTIONS]
```

Runs CLI from `v2/cli_organize.py`

### Tests
```bash
pytest v2/test_suite.py
```

Runs test suite from `v2/test_suite.py`

## Data Files

### Created at Runtime

**face_database.json** (in project root)
- Stores registered people
- Format: `{"people": [...]}`
- Shared between V1 and V2

**organized_photos/** (output directory)
- Organized photo folders
- `.original_paths.json` - Undo information
- `organization_log.json` - Operation log

## Code Statistics

- **Total V2 modules**: 9 Python files
- **Total V2 lines**: ~2,156 lines
- **Core logic**: ~1,730 lines (excluding tests)
- **Documentation**: 4 markdown files
- **Configuration**: 2 files (.env.example, requirements.txt)

## Comparison with V1

| Aspect | V1 | V2 |
|--------|----|----|
| **Files** | 15+ files | 9 files |
| **Total lines** | ~2,400 | ~1,730 |
| **AI providers** | 2 (Claude, Gemini) | 1 (Claude) |
| **Client files** | 3 (claude, gemini, vision) | 1 (vertex_claude) |
| **Test files** | 3 separate | 1 unified |
| **Config complexity** | High | Low |
| **Organization modes** | 1 | 2 |

## Development Notes

All V2 code uses:
- Absolute imports: `from v2.module import ...`
- Type hints in function signatures
- Comprehensive docstrings
- Consistent error handling
- Clear separation of concerns

V1 code is preserved in the root directory for reference but is not used by V2.
