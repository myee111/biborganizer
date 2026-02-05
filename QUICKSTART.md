# Quick Start Guide

Get started with Photo Organizer in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create a virtual environment (recommended)
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Verify installation
python test_installation.py
```

## Step 2: Set Up API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get your key from: https://console.anthropic.com/
```

Your `.env` should look like:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxx...
```

## Step 3: Add Known People

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the database management tool
python manage_database.py
```

In the menu, select option 1 and add each person:
- Enter their name
- Provide path to a clear reference photo
- Add optional notes

**Example:**
```
Enter person's name: John Doe
Enter path to reference image: ~/Pictures/john_reference.jpg
Enter notes (optional): My brother
```

Repeat for each person you want to recognize.

## Step 4: Organize Photos

### Preview First (Recommended)

```bash
# See what will happen without making changes
python organize.py ~/Pictures/MyPhotos --dry-run
```

### Actually Organize

```bash
# Copy mode (keeps originals)
python organize.py ~/Pictures/MyPhotos

# Or specify output directory
python organize.py ~/Pictures/MyPhotos -o ~/Pictures/Organized
```

## Step 5: Review Results

Check the organized photos:

```
organized_photos/
├── John_Doe/              # Photos with John
├── Jane_Smith/            # Photos with Jane
├── Multiple_People/       # Group photos
│   ├── Jane_Smith_John_Doe/
├── Unknown_Faces/         # Unrecognized people
└── No_Faces_Detected/     # Landscapes, etc.
```

## Optional: Undo If Needed

```bash
# Restore original organization
python organize.py -o ~/Pictures/Organized --undo
```

## Tips

1. **Start Small**: Test with 10-20 photos first
2. **Use Clear Reference Photos**: Well-lit, front-facing works best
3. **Check Unknown Faces**: Add missing people to database
4. **Use Copy Mode**: Keeps originals safe (default)
5. **Dry Run First**: Preview before organizing large libraries

## Common Commands

**Note:** Always activate the virtual environment first: `source venv/bin/activate`

```bash
# Add people to database
python manage_database.py

# Preview organization
python organize.py /path/to/photos --dry-run

# Organize photos (copy mode)
python organize.py /path/to/photos

# Move instead of copy
python organize.py /path/to/photos --mode move

# Undo organization
python organize.py -o organized_photos --undo
```

## Need Help?

See the full [README.md](README.md) for detailed documentation.
