#!/usr/bin/env python3
"""Cleanup and prepare folders for next run"""
import os


def cleanup_folder(folder_name: str) -> bool:
    """
    Prepare a folder for the next monitoring cycle:
    1. Rename results_new.md -> results_old.md (new becomes the baseline)
    2. Remove extracted_updates.json (temporary)
    3. Keep differences.md (history)

    Args:
        folder_name: Path to folder to cleanup

    Returns:
        True if cleanup successful, False otherwise
    """
    try:
        new_path = os.path.join(folder_name, "results_new.md")
        old_path = os.path.join(folder_name, "results_old.md")

        if os.path.exists(new_path):
            if os.path.exists(old_path):
                os.remove(old_path)
            os.rename(new_path, old_path)

        extracted_updates_path = os.path.join(folder_name, "extracted_updates.json")
        if os.path.exists(extracted_updates_path):
            os.remove(extracted_updates_path)

        return True

    except Exception as e:
        print(f"  ⚠ Error during cleanup of {folder_name}: {e}")
        return False


def cleanup_all_folders(folder_names: list) -> None:
    """
    Clean up multiple folders.

    Args:
        folder_names: List of folder paths to cleanup
    """
    print("\n✓ Cleaning up and preparing for next run...")

    success_count = sum(cleanup_folder(f) for f in folder_names)
    print(f"✓ Cleaned up {success_count}/{len(folder_names)} folder(s)")
    print("✓ Ready for next monitoring cycle")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python cleanup.py <folder_name>")
        print("Example: python cleanup.py ieee_jsac")
        sys.exit(1)

    folder = sys.argv[1]
    if cleanup_folder(folder):
        print(f"✓ Cleaned up {folder}")
    else:
        print(f"✗ Failed to clean up {folder}")
