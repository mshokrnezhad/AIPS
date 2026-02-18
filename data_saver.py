#!/usr/bin/env python3
"""Data saver module for storing fetched Markdown results"""
import os
import re


def sanitize_folder_name(name):
    """Convert a name to a safe folder name"""
    safe_name = re.sub(r'[^\w\s-]', '', name)
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    return safe_name.strip('_').lower()


def save_results(folder_name, md_data):
    """Save markdown data to a file in a folder.

    On first run saves as results_old.md (baseline).
    On subsequent runs saves as results_new.md (for comparison).
    """
    os.makedirs(folder_name, exist_ok=True)

    old_path = os.path.join(folder_name, "results_old.md")
    suffix = "new" if os.path.exists(old_path) else "old"

    results_path = os.path.join(folder_name, f"results_{suffix}.md")
    with open(results_path, "w", encoding="utf-8") as f:
        f.write(md_data)

    return results_path
