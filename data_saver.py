#!/usr/bin/env python3
"""Data saver module for storing API results"""
import os
import re


def sanitize_folder_name(name):
    """Convert a name to a safe folder name"""
    # Remove or replace invalid characters
    safe_name = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces with underscores
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    return safe_name.strip('_').lower()


def save_results(folder_name, read_data, links_data):
    """Save read and links data to separate files in a folder"""
    # Create folder if it doesn't exist
    os.makedirs(folder_name, exist_ok=True)
    
    # Check if old files exist to determine suffix
    read_old_path = os.path.join(folder_name, "read_results_old.txt")
    links_old_path = os.path.join(folder_name, "links_results_old.txt")
    
    # Determine suffix based on whether old files exist
    if os.path.exists(read_old_path):
        suffix = "new"
    else:
        suffix = "old"
    
    # Save read results
    read_path = os.path.join(folder_name, f"read_results_{suffix}.txt")
    with open(read_path, "w", encoding="utf-8") as f:
        f.write(read_data)
    
    # Save links results
    links_path = os.path.join(folder_name, f"links_results_{suffix}.txt")
    with open(links_path, "w", encoding="utf-8") as f:
        f.write(links_data)
    
    return read_path, links_path
