#!/usr/bin/env python3
"""API fetcher module - fetches URLs as Markdown via Cloudflare Browser Rendering API"""
import os
import requests
import time
import random
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")


def fetch_markdown(url, retries=10):
    """
    Fetch a URL as Markdown via Cloudflare Browser Rendering API

    Args:
        url: URL to fetch
        retries: Number of retry attempts (default: 10)

    Returns:
        Tuple of (markdown_text, status_code)
    """
    api_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/browser-rendering/markdown"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
    }
    payload = {"url": url}

    for attempt in range(retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result = data.get("result", "")
                    if len(result) > 100:
                        return result, 200
                    err = "Response too small"
                else:
                    err = data.get("errors", [{}])[0].get("message", str(data))
            elif response.status_code == 429:
                err = "HTTP 429 (rate limited)"
            else:
                err = f"HTTP {response.status_code}"

            if attempt < retries - 1:
                # Back off longer on rate-limit responses
                backoff = random.uniform(5, 15) if response.status_code == 429 else random.uniform(2, 10)
                print(f"  ⚠ Attempt {attempt + 1} failed ({err}), retrying in {backoff:.1f}s...")
                time.sleep(backoff)
            else:
                print(f"  ⚠ All {retries} attempts failed for {url}")
                return "", 500

        except Exception as e:
            if attempt < retries - 1:
                backoff = random.uniform(2, 10)
                print(f"  ⚠ Attempt {attempt + 1} failed: {e}, retrying in {backoff:.1f}s...")
                time.sleep(backoff)
            else:
                print(f"  ✗ All {retries} attempts failed: {e}")
                return "", 500

    return "", 500
