"""
Face database management for storing and retrieving known people.
Uses JSON file for persistence with facial descriptions from Claude.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from v2.vertex_claude import generate_outfit_description


# Database file path
DATABASE_FILE = "face_database.json"


def load_database() -> Dict:
    """
    Load face database from JSON file.

    Returns:
        Database dictionary with 'people' list
    """
    if not os.path.exists(DATABASE_FILE):
        return {"people": []}

    try:
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {DATABASE_FILE} is corrupted. Creating new database.")
        return {"people": []}


def save_database(db: Dict) -> None:
    """
    Save face database to JSON file.

    Args:
        db: Database dictionary to save
    """
    with open(DATABASE_FILE, 'w') as f:
        json.dump(db, f, indent=2)


def add_person(name: str, reference_image_path: str, notes: str = "") -> bool:
    """
    Add an outfit type to the database with Claude-generated outfit description.

    Args:
        name: Outfit name (e.g., "Blue Formal", "Red Casual", "Green Dress")
        reference_image_path: Path to reference photo
        notes: Optional notes about the outfit

    Returns:
        True if successful, False otherwise

    Raises:
        FileNotFoundError: If reference image doesn't exist
        ValueError: If outfit name already exists in database
    """
    # Validate image exists
    if not os.path.exists(reference_image_path):
        raise FileNotFoundError(f"Reference image not found: {reference_image_path}")

    # Load database
    db = load_database()

    # Check if outfit already exists
    if any(p['name'].lower() == name.lower() for p in db['people']):
        raise ValueError(f"Outfit '{name}' already exists in database")

    print(f"Generating outfit description for {name}...")
    print("This may take a few seconds...")

    try:
        # Generate outfit description using Claude
        outfit_description = generate_outfit_description(reference_image_path)

        # Create outfit entry
        person = {
            "name": name,
            "reference_image": str(Path(reference_image_path).absolute()),
            "facial_description": outfit_description,  # Keep key name for compatibility
            "notes": notes,
            "added_date": datetime.now().isoformat()
        }

        # Add to database
        db['people'].append(person)
        save_database(db)

        print(f"\nSuccessfully added {name} to database!")
        print(f"Outfit description preview: {outfit_description[:200]}...")

        return True

    except Exception as e:
        print(f"Error generating outfit description: {e}")
        return False


def remove_person(name: str) -> bool:
    """
    Remove a person from the database.

    Args:
        name: Name of person to remove

    Returns:
        True if person was removed, False if not found
    """
    db = load_database()

    # Find and remove person
    original_count = len(db['people'])
    db['people'] = [p for p in db['people'] if p['name'].lower() != name.lower()]

    if len(db['people']) < original_count:
        save_database(db)
        print(f"Removed {name} from database.")
        return True
    else:
        print(f"Person '{name}' not found in database.")
        return False


def get_person(name: str) -> Optional[Dict]:
    """
    Get person entry from database.

    Args:
        name: Name of person to find

    Returns:
        Person dictionary or None if not found
    """
    db = load_database()

    for person in db['people']:
        if person['name'].lower() == name.lower():
            return person

    return None


def list_people() -> List[Dict]:
    """
    Get list of all people in database.

    Returns:
        List of person dictionaries
    """
    db = load_database()
    return db['people']


def display_all_people() -> None:
    """
    Display all people in database with formatted output.
    """
    people = list_people()

    if not people:
        print("\nDatabase is empty. No people registered yet.")
        return

    print(f"\n{'='*70}")
    print(f"Face Database - {len(people)} people registered")
    print(f"{'='*70}\n")

    for i, person in enumerate(people, 1):
        print(f"{i}. {person['name']}")
        print(f"   Reference: {person['reference_image']}")
        print(f"   Added: {person['added_date'][:10]}")

        if person.get('notes'):
            print(f"   Notes: {person['notes']}")

        print(f"   Description preview: {person['facial_description'][:150]}...")
        print()


def display_person_details(name: str) -> None:
    """
    Display detailed information about a person.

    Args:
        name: Name of person to display
    """
    person = get_person(name)

    if not person:
        print(f"Person '{name}' not found in database.")
        return

    print(f"\n{'='*70}")
    print(f"Details for: {person['name']}")
    print(f"{'='*70}\n")
    print(f"Reference Image: {person['reference_image']}")
    print(f"Added: {person['added_date']}")

    if person.get('notes'):
        print(f"Notes: {person['notes']}")

    print(f"\nFacial Description:")
    print(f"{'-'*70}")
    print(person['facial_description'])
    print(f"{'-'*70}\n")


def get_all_outfit_descriptions() -> Dict[str, str]:
    """
    Get mapping of names to outfit descriptions for all outfits.

    Returns:
        Dictionary mapping outfit names to their outfit descriptions
    """
    db = load_database()
    return {
        person['name']: person['facial_description']  # Key name kept for compatibility
        for person in db['people']
    }

# Keep old function name for compatibility
def get_all_facial_descriptions() -> Dict[str, str]:
    """Alias for get_all_outfit_descriptions for backward compatibility."""
    return get_all_outfit_descriptions()


def database_stats() -> Dict:
    """
    Get statistics about the database.

    Returns:
        Dictionary with database statistics
    """
    db = load_database()
    people = db['people']

    if not people:
        return {
            "total_people": 0,
            "oldest_entry": None,
            "newest_entry": None
        }

    dates = [datetime.fromisoformat(p['added_date']) for p in people]

    return {
        "total_people": len(people),
        "oldest_entry": min(dates).strftime("%Y-%m-%d"),
        "newest_entry": max(dates).strftime("%Y-%m-%d")
    }


def validate_database() -> List[str]:
    """
    Validate database integrity and return list of issues.

    Returns:
        List of validation error messages (empty if valid)
    """
    issues = []

    if not os.path.exists(DATABASE_FILE):
        issues.append("Database file does not exist")
        return issues

    db = load_database()

    # Check structure
    if 'people' not in db:
        issues.append("Database missing 'people' key")
        return issues

    # Check each person entry
    for i, person in enumerate(db['people']):
        prefix = f"Person {i+1}"

        required_fields = ['name', 'reference_image', 'facial_description', 'added_date']
        for field in required_fields:
            if field not in person:
                issues.append(f"{prefix}: Missing required field '{field}'")

        # Check if reference image exists
        if 'reference_image' in person:
            if not os.path.exists(person['reference_image']):
                issues.append(f"{prefix} ({person.get('name', 'Unknown')}): Reference image not found: {person['reference_image']}")

    # Check for duplicate names
    names = [p.get('name', '').lower() for p in db['people']]
    duplicates = [name for name in names if names.count(name) > 1]
    if duplicates:
        issues.append(f"Duplicate names found: {', '.join(set(duplicates))}")

    return issues
