#!/usr/bin/env python3
"""Cleanup and prepare folders for next run"""
import os


def cleanup_folder(folder_name: str) -> bool:
    """
    Clean up temporary files and rename new results to old for next run
    
    This function:
    1. Renames *_new.txt to *_old.txt (if new files exist)
    2. Removes temporary files: extracted_updates.json
    3. Keeps difference files for history: *_differences.txt
    
    Note: For new URLs, *_old.txt files are preserved as baseline
    
    Args:
        folder_name: Path to folder to cleanup
    
    Returns:
        True if cleanup successful, False otherwise
    """
    try:
        # Rename new files to old first
        rename_pairs = [
            (os.path.join(folder_name, "links_results_new.txt"), 
             os.path.join(folder_name, "links_results_old.txt")),
            (os.path.join(folder_name, "read_results_new.txt"), 
             os.path.join(folder_name, "read_results_old.txt")),
        ]
        
        for new_path, old_path in rename_pairs:
            if os.path.exists(new_path):
                # Remove old file first if it exists
                if os.path.exists(old_path):
                    os.remove(old_path)
                # Rename new to old
                os.rename(new_path, old_path)
        
        # Remove temporary files (only extracted_updates.json)
        extracted_updates_path = os.path.join(folder_name, "extracted_updates.json")
        if os.path.exists(extracted_updates_path):
            os.remove(extracted_updates_path)
        
        return True
    
    except Exception as e:
        print(f"  ⚠ Error during cleanup of {folder_name}: {e}")
        return False


def cleanup_all_folders(folder_names: list) -> None:
    """
    Clean up multiple folders
    
    Args:
        folder_names: List of folder paths to cleanup
    """
    print("\n✓ Cleaning up and preparing for next run...")
    
    success_count = 0
    for folder_name in folder_names:
        if cleanup_folder(folder_name):
            success_count += 1
    
    print(f"✓ Cleaned up {success_count}/{len(folder_names)} folder(s)")
    print("✓ Ready for next monitoring cycle")


if __name__ == "__main__":
    # Example usage for testing
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
