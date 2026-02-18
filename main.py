#!/usr/bin/env python3
"""Main script - process multiple URLs from urls.json"""
import json
import os
import time
from dotenv import load_dotenv
from api_fetcher import fetch_markdown
from data_saver import save_results, sanitize_folder_name
from compare_results import compare_files
from llm_extractor import process_folder_updates
from link_verifier import verify_links
from email_sender import send_combined_updates
from cleanup import cleanup_all_folders

load_dotenv()


def validate_fetch_size(new_data, old_path, min_ratio=0.5):
    """
    Validate that newly fetched data is not suspiciously smaller than the previous snapshot.

    Returns True if data is acceptable, False if it looks truncated.
    """
    if not os.path.exists(old_path):
        return True

    try:
        with open(old_path, "r", encoding="utf-8") as f:
            old_data = f.read()

        old_size = len(old_data)
        if old_size < 100:
            return True

        ratio = len(new_data) / old_size
        if ratio < min_ratio:
            print(f"  ⚠ New data too small: {len(new_data)} bytes vs {old_size} bytes (ratio: {ratio:.2f})")
            return False

        return True

    except Exception as e:
        print(f"  ⚠ Error validating size: {e}")
        return True


def process_url(name, url):
    """Fetch, save, diff, and extract updates for a single URL.

    Returns:
        Tuple of (folder_name, updates_list or None)
    """
    print(f"Processing: {name}")
    folder_name = sanitize_folder_name(name)

    # Fetch markdown with size validation and retry
    max_attempts = 2
    md_data = ""
    time.sleep(5)  # Avoid hitting Cloudflare rate limits
    for attempt in range(max_attempts):
        md_data, status = fetch_markdown(url)

        old_path = os.path.join(folder_name, "results_old.md")
        if validate_fetch_size(md_data, old_path):
            break
        elif attempt < max_attempts - 1:
            print(f"  🔄 Retrying fetch...")
            time.sleep(3)
        else:
            print(f"  ⚠ Using potentially incomplete data after {max_attempts} attempts")

    # Save to folder (old on first run, new on subsequent runs)
    save_results(folder_name, md_data)
    print(f"✓ Saved to {folder_name}/")

    # Compare old vs new (only possible from the second run onward)
    diff_path = compare_files(folder_name)
    if diff_path:
        print(f"✓ Differences saved to {diff_path}")

    # Extract structured updates via LLM if there are differences
    updates = None
    if diff_path and os.path.getsize(diff_path) > 0:
        if os.getenv("OPENROUTER_API_KEY"):
            updates_result = process_folder_updates(folder_name, source_url=url)
            if updates_result and updates_result.updates:
                print(f"✓ Extracted {len(updates_result.updates)} structured updates")
                print(f"✓ Verifying links...")
                updates_result = verify_links(updates_result)
                updates = updates_result.model_dump()["updates"]
        else:
            print("ℹ Skipping LLM extraction (OPENROUTER_API_KEY not set)")

    return folder_name, updates


def main():
    """Main function - read URLs and process each one"""
    with open("urls.json", "r", encoding="utf-8") as f:
        urls_data = json.load(f)

    print(f"Processing {len(urls_data)} URLs...\n")

    all_updates = {}
    processed_folders = []

    for key, data in urls_data.items():
        name = data["name"]
        url = data["url"]
        folder_name, updates = process_url(name, url)

        processed_folders.append(folder_name)

        if updates:
            all_updates[name] = updates

        print()

    if all_updates:
        send_combined_updates(all_updates)
    else:
        print("ℹ No updates found across all sources\n")

    cleanup_all_folders(processed_folders)
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
