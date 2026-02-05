#!/usr/bin/env python3
"""
Main CLI entry point for photo organization.
Scans directories, identifies faces, and organizes photos by person.
"""

import argparse
import sys
import os
from pathlib import Path

from photo_organizer import (
    scan_directory_for_images,
    create_organization_plan,
    execute_organization_plan,
    generate_organization_report,
    undo_organization
)
from face_database import load_database, get_all_facial_descriptions, validate_database


def validate_inputs(args):
    """
    Validate command-line arguments.

    Args:
        args: Parsed arguments

    Returns:
        True if valid, False otherwise
    """
    # Check if undo mode
    if args.undo:
        if not os.path.exists(args.output):
            print(f"Error: Output directory does not exist: {args.output}")
            return False
        return True

    # Check source directory
    if not os.path.exists(args.source_dir):
        print(f"Error: Source directory does not exist: {args.source_dir}")
        return False

    if not os.path.isdir(args.source_dir):
        print(f"Error: Not a directory: {args.source_dir}")
        return False

    # Check if output directory exists and is not empty (warn)
    if os.path.exists(args.output):
        if os.listdir(args.output):
            print(f"Warning: Output directory is not empty: {args.output}")
            if not args.dry_run:
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Cancelled.")
                    return False

    # Check database exists
    db = load_database()
    if not db.get('people'):
        print("\nWarning: Face database is empty!")
        print("No known people registered. All faces will be categorized as 'Unknown'.")
        print("\nRun 'python manage_database.py' to add people to the database first.")

        if not args.dry_run:
            confirm = input("\nContinue anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Cancelled.")
                return False

    # Validate database
    issues = validate_database()
    if issues:
        print("\nWarning: Database validation found issues:")
        for issue in issues:
            print(f"  - {issue}")

        if not args.dry_run:
            confirm = input("\nContinue anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Cancelled.")
                return False

    return True


def print_plan_summary(plan):
    """
    Display organization plan summary.

    Args:
        plan: Organization plan dictionary
    """
    print("\n" + "="*70)
    print("Organization Plan Summary")
    print("="*70 + "\n")

    # Single person photos
    single_total = sum(len(paths) for paths in plan['single_person'].values())
    print(f"Single person photos: {single_total}")
    for name, paths in sorted(plan['single_person'].items()):
        print(f"  - {name}: {len(paths)} photos")

    # Multiple people photos
    multi_total = sum(len(paths) for paths in plan['multiple_people'].values())
    print(f"\nMultiple people photos: {multi_total}")
    for names, paths in sorted(plan['multiple_people'].items()):
        names_str = " & ".join(names)
        print(f"  - {names_str}: {len(paths)} photos")

    # Unknown faces
    print(f"\nUnknown faces: {len(plan['unknown'])} photos")

    # No faces
    print(f"No faces detected: {len(plan['no_faces'])} photos")

    # Errors
    if plan.get('errors'):
        print(f"\nErrors: {len(plan['errors'])} files")
        print("(See organization_log.json for details)")

    total = single_total + multi_total + len(plan['unknown']) + len(plan['no_faces'])
    print(f"\nTotal photos to organize: {total}")
    print("="*70)


def main():
    """Main CLI workflow."""
    parser = argparse.ArgumentParser(
        description='Organize photos by identifying people using Claude Vision API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Organize photos (copy mode)
  python organize.py /path/to/photos

  # Organize with custom output directory
  python organize.py /path/to/photos -o /path/to/organized

  # Move files instead of copying
  python organize.py /path/to/photos --mode move

  # Preview organization without making changes
  python organize.py /path/to/photos --dry-run

  # Undo previous organization
  python organize.py /path/to/photos -o /path/to/organized --undo

  # Adjust confidence threshold
  python organize.py /path/to/photos --confidence 0.8

Note: Run 'python manage_database.py' first to register known people.
        """
    )

    parser.add_argument(
        'source_dir',
        nargs='?',
        help='Source directory containing photos'
    )

    parser.add_argument(
        '-o', '--output',
        default='./organized_photos',
        help='Output directory for organized photos (default: ./organized_photos)'
    )

    parser.add_argument(
        '--mode',
        choices=['copy', 'move'],
        default='copy',
        help='Copy or move files (default: copy)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview organization without making changes'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        default=True,
        help='Scan subdirectories (default: True)'
    )

    parser.add_argument(
        '--confidence',
        type=float,
        default=0.7,
        help='Minimum confidence threshold for face matching (default: 0.7)'
    )

    parser.add_argument(
        '--undo',
        action='store_true',
        help='Undo previous organization and restore original files'
    )

    args = parser.parse_args()

    # Handle undo mode
    if args.undo:
        if not args.source_dir:
            # Allow undo without source_dir if output is specified
            args.source_dir = None

        print("\n" + "="*70)
        print("Photo Organizer - Undo Mode")
        print("="*70)

        if not validate_inputs(args):
            sys.exit(1)

        success = undo_organization(args.output)
        sys.exit(0 if success else 1)

    # Normal mode requires source_dir
    if not args.source_dir:
        parser.print_help()
        sys.exit(1)

    # Print header
    print("\n" + "="*70)
    print("Photo Organizer")
    print("="*70)
    print(f"\nSource: {args.source_dir}")
    print(f"Output: {args.output}")
    print(f"Mode: {args.mode.upper()}")
    print(f"Confidence threshold: {args.confidence}")

    if args.dry_run:
        print("\n*** DRY RUN MODE - No files will be modified ***")

    # Validate inputs
    if not validate_inputs(args):
        sys.exit(1)

    try:
        # Scan directory
        print("\n" + "="*70)
        print("Step 1: Scanning for images")
        print("="*70)

        image_files = scan_directory_for_images(args.source_dir, args.recursive)

        if not image_files:
            print(f"\nNo supported image files found in {args.source_dir}")
            print("Supported formats: .jpg, .jpeg, .png, .gif, .webp, .heic")
            sys.exit(1)

        print(f"\nFound {len(image_files)} images")

        # Load face database
        print("\n" + "="*70)
        print("Step 2: Loading face database")
        print("="*70)

        face_db = get_all_facial_descriptions()
        print(f"\nLoaded {len(face_db)} known people")

        # Create organization plan
        print("\n" + "="*70)
        print("Step 3: Analyzing photos and identifying faces")
        print("="*70)
        print("\nThis may take a while depending on the number of photos...")

        plan = create_organization_plan(image_files, face_db, args.confidence)

        # Display plan summary
        print_plan_summary(plan)

        # Dry run mode - exit here
        if args.dry_run:
            print("\n*** DRY RUN COMPLETE - No files were modified ***")
            sys.exit(0)

        # Confirm execution
        print("\n" + "="*70)
        print("Step 4: Execute organization")
        print("="*70)

        confirm = input(f"\nProceed to {args.mode} files? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            sys.exit(0)

        # Execute plan
        result = execute_organization_plan(plan, args.source_dir, args.output, args.mode)

        # Generate report
        generate_organization_report(plan, result, args.output)

        # Print final statistics
        print("\n" + "="*70)
        print("Organization Complete!")
        print("="*70)
        print(f"\nTotal files processed: {result['stats']['total_files']}")
        print(f"Successful: {result['stats']['successful']}")
        print(f"Failed: {result['stats']['failed']}")

        print(f"\nOrganized photos are in: {args.output}")
        print(f"Organization log: {args.output}/organization_log.json")

        if args.mode == 'copy':
            print(f"\nOriginal files remain in: {args.source_dir}")
        else:
            print(f"\nOriginal files have been moved from: {args.source_dir}")

        print(f"\nTo undo this organization, run:")
        print(f"  python organize.py -o {args.output} --undo")

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
