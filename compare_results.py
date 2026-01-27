#!/usr/bin/env python3
"""Compare old and new results and save differences"""
import os
import json
import difflib


def _compare_file_pair(old_path, new_path, diff_path, is_json=False):
    """Compare a pair of old and new files and save differences
    
    Args:
        old_path: Path to old file
        new_path: Path to new file
        diff_path: Path to save differences
        is_json: If True, parse and pretty-print JSON before comparing
    """
    # Check if both files exist
    if not os.path.exists(old_path) or not os.path.exists(new_path):
        return None
    
    # Read both files
    with open(old_path, "r", encoding="utf-8") as f:
        old_content_raw = f.read()
    
    with open(new_path, "r", encoding="utf-8") as f:
        new_content_raw = f.read()
    
    # If JSON files, parse and pretty-print for better comparison
    if is_json:
        try:
            old_json = json.loads(old_content_raw)
            new_json = json.loads(new_content_raw)
            
            # Check if JSON structures are identical
            if old_json == new_json:
                # No differences - create empty file
                with open(diff_path, "w", encoding="utf-8") as f:
                    pass  # Empty file
                return diff_path
            
            # Pretty-print JSON with sorted keys for consistent comparison
            old_content = json.dumps(old_json, indent=2, sort_keys=True).splitlines(keepends=True)
            new_content = json.dumps(new_json, indent=2, sort_keys=True).splitlines(keepends=True)
        except json.JSONDecodeError:
            # If JSON parsing fails, fall back to regular text comparison
            old_content = old_content_raw.splitlines(keepends=True)
            new_content = new_content_raw.splitlines(keepends=True)
    else:
        # Regular text files
        old_content = old_content_raw.splitlines(keepends=True)
        new_content = new_content_raw.splitlines(keepends=True)
    
    # Check if files are identical (for non-JSON or after pretty-print)
    if old_content == new_content:
        # No differences - create empty file
        with open(diff_path, "w", encoding="utf-8") as f:
            pass  # Empty file
        return diff_path
    
    # Generate unified diff
    diff = difflib.unified_diff(
        old_content,
        new_content,
        fromfile="old",
        tofile="new",
        lineterm="",
        n=0  # No context lines
    )
    
    # Keep only lines with additions (+), skip deletions (-)
    diff_lines = []
    for line in diff:
        # Skip header and metadata lines
        if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
            continue
        # Only keep lines that start with + (additions only)
        if line.startswith('+'):
            diff_lines.append(line)
    
    # Save only the actual differences
    with open(diff_path, "w", encoding="utf-8") as f:
        f.write("\n".join(diff_lines))
    
    return diff_path


def compare_files(folder_name):
    """Compare old and new files (both read_results and links_results) and save differences"""
    # Compare read results (text files)
    read_old_path = os.path.join(folder_name, "read_results_old.txt")
    read_new_path = os.path.join(folder_name, "read_results_new.txt")
    read_diff_path = os.path.join(folder_name, "read_differences.txt")
    
    # Compare links results (JSON files)
    links_old_path = os.path.join(folder_name, "links_results_old.txt")
    links_new_path = os.path.join(folder_name, "links_results_new.txt")
    links_diff_path = os.path.join(folder_name, "links_differences.txt")
    
    # Perform comparisons (links are JSON, read results are text)
    read_diff = _compare_file_pair(read_old_path, read_new_path, read_diff_path, is_json=False)
    links_diff = _compare_file_pair(links_old_path, links_new_path, links_diff_path, is_json=True)
    
    return read_diff, links_diff
