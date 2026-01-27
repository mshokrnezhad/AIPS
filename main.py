#!/usr/bin/env python3
"""Main script - process multiple URLs from urls.json"""
import json
import os
import time
from dotenv import load_dotenv
from api_fetcher import fetch_read, fetch_links
from data_saver import save_results, sanitize_folder_name
from compare_results import compare_files
from llm_extractor import process_folder_updates
from email_sender import send_combined_updates
from cleanup import cleanup_all_folders

# Load environment variables from .env file
load_dotenv()


def validate_fetch_size(new_data, old_path, min_ratio=0.5):
    """
    Validate if new fetched data is reasonable compared to old data
    
    Args:
        new_data: Newly fetched data
        old_path: Path to old data file
        min_ratio: Minimum acceptable ratio of new/old size (default 0.5 = 50%)
    
    Returns:
        True if data is valid, False if too small
    """
    if not os.path.exists(old_path):
        # No old data to compare, accept new data
        return True
    
    try:
        with open(old_path, "r", encoding="utf-8") as f:
            old_data = f.read()
        
        new_size = len(new_data)
        old_size = len(old_data)
        
        # If old data is very small, don't validate
        if old_size < 100:
            return True
        
        ratio = new_size / old_size
        
        if ratio < min_ratio:
            print(f"  ⚠ New data too small: {new_size} bytes vs {old_size} bytes (ratio: {ratio:.2f})")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ⚠ Error validating size: {e}")
        return True  # Accept if we can't validate


def process_url(name, url):
    """Process a single URL - fetch and save results
    
    Returns:
        Tuple of (folder_name, updates_list or None)
    """
    print(f"Processing: {name}")
    
    folder_name = sanitize_folder_name(name)
    
    # Fetch read results with validation
    max_attempts = 2
    for attempt in range(max_attempts):
        read_data, read_status = fetch_read(url)
        
        # Validate read data size
        read_old_path = os.path.join(folder_name, "read_results_old.txt")
        if validate_fetch_size(read_data, read_old_path):
            break
        elif attempt < max_attempts - 1:
            print(f"  🔄 Retrying fetch for read data...")
            time.sleep(3)
        else:
            print(f"  ⚠ Using potentially incomplete read data after {max_attempts} attempts")
    
    # Fetch links results with validation
    for attempt in range(max_attempts):
        links_data, links_status = fetch_links(url)
        
        # Validate links data size
        links_old_path = os.path.join(folder_name, "links_results_old.txt")
        if validate_fetch_size(links_data, links_old_path):
            break
        elif attempt < max_attempts - 1:
            print(f"  🔄 Retrying fetch for links data...")
            time.sleep(3)
        else:
            print(f"  ⚠ Using potentially incomplete links data after {max_attempts} attempts")
    
    # Save results to folder
    save_results(folder_name, read_data, links_data)
    print(f"✓ Saved to {folder_name}/")
    
    # Compare old and new results if both exist
    read_diff_path, links_diff_path = compare_files(folder_name)
    if read_diff_path:
        print(f"✓ Read differences saved to {read_diff_path}")
    if links_diff_path:
        print(f"✓ Links differences saved to {links_diff_path}")
    
    # Extract structured updates using LLM if differences exist
    updates = None
    if read_diff_path or links_diff_path:
        # Only call LLM if API key is set
        if os.getenv("OPENROUTER_API_KEY"):
            updates_result = process_folder_updates(folder_name)
            if updates_result and updates_result.updates:
                print(f"✓ Extracted {len(updates_result.updates)} structured updates")
                # Return updates for later email sending
                updates = updates_result.model_dump()['updates']
        else:
            print("ℹ Skipping LLM extraction (OPENROUTER_API_KEY not set)")
    
    return folder_name, updates


def main():
    """Main function - read URLs and process each one"""
    # Load URLs from JSON file
    with open("urls.json", "r", encoding="utf-8") as f:
        urls_data = json.load(f)
    
    print(f"Processing {len(urls_data)} URLs...\n")
    
    # Dictionary to collect all updates and list of folders to cleanup
    all_updates = {}
    processed_folders = []
    
    # Process each URL
    for key, data in urls_data.items():
        name = data["name"]
        url = data["url"]
        folder_name, updates = process_url(name, url)
        
        # Track processed folder
        processed_folders.append(folder_name)
        
        # Collect updates if found
        if updates:
            all_updates[name] = updates
        
        print()  # Empty line between sources
    
    # Send combined email with all updates
    if all_updates:
        send_combined_updates(all_updates)
    else:
        print("ℹ No updates found across all sources\n")
    
    # Cleanup all folders and prepare for next run
    cleanup_all_folders(processed_folders)
    
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
