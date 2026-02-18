#!/usr/bin/env python3
"""Compare old and new Markdown results and save added lines as differences"""
import os
import difflib


def compare_files(folder_name):
    """Compare results_old.md and results_new.md, saving only added lines.

    Returns:
        diff_path if both files exist and comparison was performed, None otherwise.
        The diff file is empty when there are no differences.
    """
    old_path = os.path.join(folder_name, "results_old.md")
    new_path = os.path.join(folder_name, "results_new.md")
    diff_path = os.path.join(folder_name, "differences.md")

    if not os.path.exists(old_path) or not os.path.exists(new_path):
        return None

    with open(old_path, "r", encoding="utf-8") as f:
        old_content = f.read().splitlines(keepends=True)

    with open(new_path, "r", encoding="utf-8") as f:
        new_content = f.read().splitlines(keepends=True)

    if old_content == new_content:
        with open(diff_path, "w", encoding="utf-8") as f:
            pass  # Empty file — no changes
        return diff_path

    diff = difflib.unified_diff(
        old_content,
        new_content,
        fromfile="old",
        tofile="new",
        lineterm="",
        n=0,
    )

    # Keep only added lines (strip the leading '+')
    diff_lines = []
    for line in diff:
        if line.startswith(('---', '+++', '@@')):
            continue
        if line.startswith('+'):
            diff_lines.append(line[1:])  # strip the '+' prefix

    with open(diff_path, "w", encoding="utf-8") as f:
        f.write("\n".join(diff_lines))

    return diff_path
