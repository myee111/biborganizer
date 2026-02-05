#!/usr/bin/env python3
"""
Interactive CLI for managing the face database.
Allows adding, removing, and viewing registered people.
"""

import sys
from pathlib import Path

from v2.database import (
    add_person,
    remove_person,
    list_people,
    display_all_people,
    display_person_details,
    database_stats,
    validate_database
)


def print_menu():
    """Print the main menu."""
    print("\n" + "="*70)
    print("Outfit Database Management")
    print("="*70)
    print("\n1. Add outfit type to database")
    print("2. Remove outfit type from database")
    print("3. List all outfit types")
    print("4. View outfit details")
    print("5. Database statistics")
    print("6. Validate database")
    print("7. Exit")
    print()


def add_person_interactive():
    """Interactive workflow for adding an outfit type."""
    print("\n--- Add Outfit Type to Database ---\n")
    print("TIP: Use descriptive names based on colors and style")
    print("Examples: 'Blue_Formal', 'Red_Dress', 'Green_Casual_Shirt'\n")

    # Get name
    name = input("Enter outfit name: ").strip()
    if not name:
        print("Error: Name cannot be empty")
        return

    # Get reference image path
    ref_image = input("Enter path to reference image: ").strip()
    if not ref_image:
        print("Error: Image path cannot be empty")
        return

    # Expand user home directory if needed
    ref_image = str(Path(ref_image).expanduser())

    # Check if file exists
    if not Path(ref_image).exists():
        print(f"Error: File not found: {ref_image}")
        return

    # Get optional notes
    notes = input("Enter notes (optional): ").strip()

    # Confirm
    print(f"\nAbout to add:")
    print(f"  Outfit Name: {name}")
    print(f"  Reference: {ref_image}")
    if notes:
        print(f"  Notes: {notes}")

    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    # Add outfit
    try:
        success = add_person(name, ref_image, notes)
        if success:
            print(f"\nSuccessfully added {name} to database!")
    except ValueError as e:
        print(f"\nError: {e}")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


def remove_person_interactive():
    """Interactive workflow for removing a person."""
    print("\n--- Remove Person from Database ---\n")

    # Show current people
    people = list_people()
    if not people:
        print("Database is empty.")
        return

    print("Current people in database:")
    for i, person in enumerate(people, 1):
        print(f"  {i}. {person['name']}")

    # Get name
    name = input("\nEnter name to remove: ").strip()
    if not name:
        print("Error: Name cannot be empty")
        return

    # Confirm
    confirm = input(f"Are you sure you want to remove '{name}'? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    # Remove person
    success = remove_person(name)
    if success:
        print(f"\nSuccessfully removed {name} from database!")


def view_person_details_interactive():
    """Interactive workflow for viewing person details."""
    print("\n--- View Person Details ---\n")

    # Show current people
    people = list_people()
    if not people:
        print("Database is empty.")
        return

    print("People in database:")
    for i, person in enumerate(people, 1):
        print(f"  {i}. {person['name']}")

    # Get name
    name = input("\nEnter name to view: ").strip()
    if not name:
        print("Error: Name cannot be empty")
        return

    # Display details
    display_person_details(name)


def show_database_stats():
    """Show database statistics."""
    stats = database_stats()

    print("\n" + "="*70)
    print("Database Statistics")
    print("="*70)

    if stats['total_people'] == 0:
        print("\nDatabase is empty.")
    else:
        print(f"\nTotal people: {stats['total_people']}")
        print(f"Oldest entry: {stats['oldest_entry']}")
        print(f"Newest entry: {stats['newest_entry']}")


def validate_database_interactive():
    """Validate database and show issues."""
    print("\n--- Database Validation ---\n")

    issues = validate_database()

    if not issues:
        print("Database is valid! No issues found.")
    else:
        print(f"Found {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")


def main():
    """Main interactive loop."""
    print("\n" + "="*70)
    print("Photo Organizer V2 - Outfit Database Management")
    print("="*70)
    print("\nThis tool manages the database of outfit types.")
    print("Add outfit types with reference photos for database mode organization.")
    print("\nNOTE: For auto-cluster mode, you don't need a database!")
    print("      Just run: python -m v2.cli_organize /path/to/photos --mode auto-cluster")

    while True:
        print_menu()

        choice = input("Enter choice (1-7): ").strip()

        if choice == '1':
            add_person_interactive()
        elif choice == '2':
            remove_person_interactive()
        elif choice == '3':
            display_all_people()
        elif choice == '4':
            view_person_details_interactive()
        elif choice == '5':
            show_database_stats()
        elif choice == '6':
            validate_database_interactive()
        elif choice == '7':
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please enter 1-7.")

        input("\nPress Enter to continue...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
