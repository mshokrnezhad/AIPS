#!/usr/bin/env python3
"""Link verifier - finds working links via Brave Search API."""
import os
import time
import random
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from llm_extractor import UpdatesList, UpdateEntry

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "X-Subscription-Token": BRAVE_API_KEY,
}


def get_domain(url: str) -> str:
    return urlparse(url).netloc


def search_verified_link(title: str, original_link: str) -> str | None:
    """
    Search Brave for `title`, scan the top 10 results, and return the first URL
    whose domain matches the original link's domain. Returns None if not found.
    """
    original_domain = get_domain(original_link)
    params = {"q": title, "count": 10}

    for attempt in range(1, 4):
        try:
            r = requests.get(BRAVE_ENDPOINT, headers=HEADERS, params=params, timeout=15)

            if r.status_code == 429:
                wait = random.uniform(5, 12)
                print(f"  ⚠ Rate limited (attempt {attempt}), retrying in {wait:.1f}s...")
                time.sleep(wait)
                continue

            if r.status_code != 200:
                print(f"  ⚠ Brave API error {r.status_code}: {r.text[:120]}")
                return None

            results = r.json().get("web", {}).get("results", [])
            for result in results:
                url = result.get("url", "")
                if get_domain(url) == original_domain:
                    return url

            return None  # Results returned but none match the domain

        except Exception as e:
            wait = random.uniform(3, 7)
            print(f"  ⚠ Search error (attempt {attempt}): {e}, retrying in {wait:.1f}s...")
            time.sleep(wait)

    return None


def verify_links(updates_result: UpdatesList) -> UpdatesList:
    """
    For every update entry, search Brave for the title and replace the link
    with the first same-domain result found. If nothing matches, keep original.
    """
    verified = []

    for entry in updates_result.updates:
        time.sleep(2)
        print(f"  🔍 Searching: {entry.title}")

        found = search_verified_link(entry.title, entry.link)

        if found and found != entry.link:
            print(f"  ↪ Link updated: {entry.link}\n           → {found}")
            verified.append(UpdateEntry(title=entry.title, link=found))
        elif found:
            print(f"  ✓ Link confirmed: {entry.link}")
            verified.append(entry)
        else:
            print(f"  ⚠ No same-domain result, keeping original: {entry.link}")
            verified.append(entry)

    return UpdatesList(updates=verified)
