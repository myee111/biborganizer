"""
Photo organization core logic.
Handles directory scanning, face identification, organization planning, and file operations.
"""

import os
import json
import shutil
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
from datetime import datetime

from tqdm import tqdm

from vision_client import detect_and_describe_all_faces, compare_face_descriptions
from face_database import load_database, get_all_facial_descriptions


# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic'}

# Hidden/system file patterns to skip
SKIP_PATTERNS = [
    r'^\.',  # Hidden files
    r'^~',   # Temporary files
    r'Thumbs\.db$',
    r'\.DS_Store$',
]


def should_skip_file(file_path: str) -> bool:
    """
    Check if file should be skipped based on name patterns.

    Args:
        file_path: Path to file

    Returns:
        True if file should be skipped
    """
    filename = os.path.basename(file_path)

    for pattern in SKIP_PATTERNS:
        if re.search(pattern, filename):
            return True

    return False


def scan_directory_for_images(directory: str, recursive: bool = True) -> List[str]:
    """
    Scan directory for supported image files.

    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories

    Returns:
        List of image file paths
    """
    image_files = []
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    # Use glob for recursive or non-recursive scanning
    pattern = "**/*" if recursive else "*"

    for item in directory.glob(pattern):
        if item.is_file():
            if item.suffix.lower() in SUPPORTED_FORMATS:
                if not should_skip_file(str(item)):
                    image_files.append(str(item.absolute()))

    return sorted(image_files)


def sanitize_directory_name(name: str) -> str:
    """
    Convert name to safe directory name.

    Args:
        name: Name to sanitize

    Returns:
        Safe directory name
    """
    # Replace spaces with underscores
    safe_name = name.replace(' ', '_')

    # Remove or replace unsafe characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '', safe_name)

    # Remove leading/trailing dots and spaces
    safe_name = safe_name.strip('. ')

    # Ensure not empty
    if not safe_name:
        safe_name = "Unknown"

    return safe_name


def handle_duplicate_filename(target_path: str) -> str:
    """
    Add numeric suffix if file already exists.

    Args:
        target_path: Desired target file path

    Returns:
        Available file path (may have numeric suffix)
    """
    if not os.path.exists(target_path):
        return target_path

    path = Path(target_path)
    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter:03d}{suffix}"
        if not os.path.exists(new_path):
            return str(new_path)
        counter += 1


def identify_all_faces_in_image(image_path: str, face_db: Dict[str, str], confidence_threshold: float = 0.7) -> List[Dict]:
    """
    Detect all faces in image and match against database.

    Args:
        image_path: Path to image
        face_db: Dictionary mapping names to facial descriptions
        confidence_threshold: Minimum similarity score to consider a match

    Returns:
        List of face matches: [{'name': 'John', 'confidence': 0.95}, ...]
        Name is None for unknown faces
    """
    try:
        # Detect all faces in image
        faces_json = detect_and_describe_all_faces(image_path)

        # Parse response
        try:
            # Try to extract JSON from response
            if "```json" in faces_json:
                start = faces_json.find("```json") + 7
                end = faces_json.find("```", start)
                faces_json = faces_json[start:end].strip()
            elif "```" in faces_json:
                start = faces_json.find("```") + 3
                end = faces_json.find("```", start)
                faces_json = faces_json[start:end].strip()

            faces_data = json.loads(faces_json)

            # Handle different response formats
            if isinstance(faces_data, dict) and 'faces' in faces_data:
                faces = faces_data['faces']
            elif isinstance(faces_data, list):
                faces = faces_data
            else:
                faces = []

        except json.JSONDecodeError:
            # If JSON parsing fails, check for NO_FACES_DETECTED
            if "NO_FACES_DETECTED" in faces_json:
                return []
            print(f"Warning: Could not parse face detection response for {image_path}")
            return []

        # If no faces detected
        if not faces:
            return []

        # Match each face against database
        matches = []

        for face in faces:
            face_description = face.get('description', '')
            if not face_description:
                continue

            best_match = None
            best_score = 0.0

            # Compare against all known people
            for name, known_description in face_db.items():
                similarity = compare_face_descriptions(known_description, face_description)

                if similarity > best_score:
                    best_score = similarity
                    best_match = name

            # Add match if above threshold
            if best_score >= confidence_threshold:
                matches.append({
                    'name': best_match,
                    'confidence': best_score
                })
            else:
                # Unknown face
                matches.append({
                    'name': None,
                    'confidence': 0.0
                })

        return matches

    except Exception as e:
        print(f"Error identifying faces in {image_path}: {e}")
        return []


def create_organization_plan(image_paths: List[str], face_db: Dict[str, str], confidence_threshold: float = 0.7) -> Dict:
    """
    Process all images and create organization plan.

    Args:
        image_paths: List of image file paths
        face_db: Dictionary mapping names to facial descriptions
        confidence_threshold: Minimum similarity score

    Returns:
        Organization plan dictionary with categorized file mappings
    """
    plan = {
        'single_person': defaultdict(list),  # {name: [paths]}
        'multiple_people': defaultdict(list),  # {(name1, name2): [paths]}
        'unknown': [],  # Unknown faces
        'no_faces': [],  # No faces detected
        'errors': []  # Files that couldn't be processed
    }

    print("\nAnalyzing photos...")

    for image_path in tqdm(image_paths, desc="Identifying faces", unit="photo"):
        try:
            matches = identify_all_faces_in_image(image_path, face_db, confidence_threshold)

            if not matches:
                # No faces detected
                plan['no_faces'].append(image_path)
                continue

            # Extract names (filter out None for unknowns)
            identified_names = [m['name'] for m in matches if m['name'] is not None]
            has_unknown = any(m['name'] is None for m in matches)

            if not identified_names and has_unknown:
                # Only unknown faces
                plan['unknown'].append(image_path)
            elif len(identified_names) == 1 and not has_unknown:
                # Single known person
                plan['single_person'][identified_names[0]].append(image_path)
            elif len(identified_names) > 1:
                # Multiple known people
                # Sort names for consistent directory naming
                key = tuple(sorted(identified_names))
                plan['multiple_people'][key].append(image_path)
            elif identified_names and has_unknown:
                # Mix of known and unknown - put in multiple people with "Unknown"
                names = sorted(identified_names) + ['Unknown']
                key = tuple(names)
                plan['multiple_people'][key].append(image_path)

        except Exception as e:
            print(f"\nError processing {image_path}: {e}")
            plan['errors'].append({
                'path': image_path,
                'error': str(e)
            })

    # Convert defaultdicts to regular dicts for JSON serialization
    plan['single_person'] = dict(plan['single_person'])
    plan['multiple_people'] = dict(plan['multiple_people'])

    return plan


def execute_organization_plan(plan: Dict, source_dir: str, target_dir: str, mode: str = 'copy') -> Dict:
    """
    Execute file operations based on organization plan.

    Args:
        plan: Organization plan from create_organization_plan
        source_dir: Source directory (for validation)
        target_dir: Target directory for organized photos
        mode: 'copy' or 'move'

    Returns:
        Dictionary with operation results and statistics
    """
    if mode not in ('copy', 'move'):
        raise ValueError(f"Invalid mode: {mode}. Must be 'copy' or 'move'")

    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    operations = []
    stats = {
        'total_files': 0,
        'successful': 0,
        'failed': 0,
        'skipped': 0
    }

    print(f"\n{mode.capitalize()}ing files to organized directories...")

    # Process single person photos
    for name, paths in plan['single_person'].items():
        person_dir = target_path / sanitize_directory_name(name)
        person_dir.mkdir(parents=True, exist_ok=True)

        for src_path in tqdm(paths, desc=f"Organizing {name}", unit="photo"):
            stats['total_files'] += 1
            try:
                filename = os.path.basename(src_path)
                dst_path = handle_duplicate_filename(str(person_dir / filename))

                if mode == 'copy':
                    shutil.copy2(src_path, dst_path)
                else:
                    shutil.move(src_path, dst_path)

                operations.append({
                    'source': src_path,
                    'destination': dst_path,
                    'category': 'single_person',
                    'label': name
                })
                stats['successful'] += 1

            except Exception as e:
                print(f"\nError processing {src_path}: {e}")
                stats['failed'] += 1

    # Process multiple people photos
    for names_tuple, paths in plan['multiple_people'].items():
        # Create subdirectory under Multiple_People
        multi_dir = target_path / "Multiple_People"
        names_str = "_".join(sanitize_directory_name(n) for n in names_tuple)
        group_dir = multi_dir / names_str
        group_dir.mkdir(parents=True, exist_ok=True)

        for src_path in tqdm(paths, desc=f"Organizing {names_str}", unit="photo"):
            stats['total_files'] += 1
            try:
                filename = os.path.basename(src_path)
                dst_path = handle_duplicate_filename(str(group_dir / filename))

                if mode == 'copy':
                    shutil.copy2(src_path, dst_path)
                else:
                    shutil.move(src_path, dst_path)

                operations.append({
                    'source': src_path,
                    'destination': dst_path,
                    'category': 'multiple_people',
                    'label': names_str
                })
                stats['successful'] += 1

            except Exception as e:
                print(f"\nError processing {src_path}: {e}")
                stats['failed'] += 1

    # Process unknown faces
    if plan['unknown']:
        unknown_dir = target_path / "Unknown_Faces"
        unknown_dir.mkdir(parents=True, exist_ok=True)

        for src_path in tqdm(plan['unknown'], desc="Organizing unknown faces", unit="photo"):
            stats['total_files'] += 1
            try:
                filename = os.path.basename(src_path)
                dst_path = handle_duplicate_filename(str(unknown_dir / filename))

                if mode == 'copy':
                    shutil.copy2(src_path, dst_path)
                else:
                    shutil.move(src_path, dst_path)

                operations.append({
                    'source': src_path,
                    'destination': dst_path,
                    'category': 'unknown',
                    'label': 'Unknown_Faces'
                })
                stats['successful'] += 1

            except Exception as e:
                print(f"\nError processing {src_path}: {e}")
                stats['failed'] += 1

    # Process no faces
    if plan['no_faces']:
        no_faces_dir = target_path / "No_Faces_Detected"
        no_faces_dir.mkdir(parents=True, exist_ok=True)

        for src_path in tqdm(plan['no_faces'], desc="Organizing photos without faces", unit="photo"):
            stats['total_files'] += 1
            try:
                filename = os.path.basename(src_path)
                dst_path = handle_duplicate_filename(str(no_faces_dir / filename))

                if mode == 'copy':
                    shutil.copy2(src_path, dst_path)
                else:
                    shutil.move(src_path, dst_path)

                operations.append({
                    'source': src_path,
                    'destination': dst_path,
                    'category': 'no_faces',
                    'label': 'No_Faces_Detected'
                })
                stats['successful'] += 1

            except Exception as e:
                print(f"\nError processing {src_path}: {e}")
                stats['failed'] += 1

    # Save backup mapping for undo
    backup_file = target_path / ".original_paths.json"
    with open(backup_file, 'w') as f:
        json.dump({
            'operations': operations,
            'mode': mode,
            'created': datetime.now().isoformat()
        }, f, indent=2)

    return {
        'operations': operations,
        'stats': stats
    }


def generate_organization_report(plan: Dict, result: Dict, target_dir: str) -> None:
    """
    Generate and save organization report.

    Args:
        plan: Organization plan
        result: Execution result
        target_dir: Target directory
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'statistics': {
            'total_processed': result['stats']['total_files'],
            'successful': result['stats']['successful'],
            'failed': result['stats']['failed'],
            'single_person_photos': sum(len(paths) for paths in plan['single_person'].values()),
            'multiple_people_photos': sum(len(paths) for paths in plan['multiple_people'].values()),
            'unknown_faces': len(plan['unknown']),
            'no_faces': len(plan['no_faces']),
            'errors': len(plan.get('errors', []))
        },
        'categories': {
            'single_person': {name: len(paths) for name, paths in plan['single_person'].items()},
            'multiple_people': {str(names): len(paths) for names, paths in plan['multiple_people'].items()},
        },
        'errors': plan.get('errors', [])
    }

    report_file = Path(target_dir) / "organization_log.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: {report_file}")


def undo_organization(target_dir: str) -> bool:
    """
    Restore files to original locations using backup mapping.

    Args:
        target_dir: Target directory containing .original_paths.json

    Returns:
        True if successful
    """
    backup_file = Path(target_dir) / ".original_paths.json"

    if not backup_file.exists():
        print(f"Error: Backup file not found: {backup_file}")
        return False

    try:
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)

        operations = backup_data['operations']
        mode = backup_data['mode']

        print(f"\nRestoring {len(operations)} files...")

        success_count = 0
        fail_count = 0

        for op in tqdm(operations, desc="Restoring files", unit="file"):
            try:
                src = op['destination']
                dst = op['source']

                if not os.path.exists(src):
                    print(f"\nWarning: File not found: {src}")
                    fail_count += 1
                    continue

                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dst), exist_ok=True)

                if mode == 'copy':
                    # For copied files, just delete the copy
                    os.remove(src)
                else:
                    # For moved files, move back
                    shutil.move(src, dst)

                success_count += 1

            except Exception as e:
                print(f"\nError restoring {src}: {e}")
                fail_count += 1

        print(f"\nRestore complete: {success_count} successful, {fail_count} failed")

        # Clean up empty directories
        try:
            for root, dirs, files in os.walk(target_dir, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
        except Exception as e:
            print(f"Warning: Error cleaning up directories: {e}")

        return True

    except Exception as e:
        print(f"Error during undo: {e}")
        return False
