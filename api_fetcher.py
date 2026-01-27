#!/usr/bin/env python3
"""API fetcher module for DeepCrawl API"""
import requests
import time
import random

API_KEY = "dc_vEZJVYmLtGohjBFuHgkSJTBPhtluFZfcesuhwesCnueSUWhYtZYpfXuLluMADcvi"


def fetch_read(url, retries=10):
    """
    Fetch read results from DeepCrawl API with retry logic and random backoff
    
    Args:
        url: URL to fetch
        retries: Number of retry attempts (default: 10)
    
    Returns:
        Tuple of (response_text, status_code)
    """
    api_url = f"https://api.deepcrawl.dev/read?url={url}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    for attempt in range(retries):
        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            
            # Check if we got a valid response
            if response.status_code == 200 and len(response.text) > 100:
                return response.text, response.status_code
            
            # If response is too small or failed, retry with random backoff
            if attempt < retries - 1:
                # Random backoff between 2 and 8 seconds
                backoff = random.uniform(2, 10)
                print(f"  ⚠ Attempt {attempt + 1} got small/invalid response, retrying in {backoff:.1f}s...")
                time.sleep(backoff)
            else:
                print(f"  ⚠ All {retries} attempts failed for read fetch")
                return response.text, response.status_code
                
        except Exception as e:
            if attempt < retries - 1:
                # Random backoff between 2 and 8 seconds
                backoff = random.uniform(2, 10)
                print(f"  ⚠ Attempt {attempt + 1} failed: {e}, retrying in {backoff:.1f}s...")
                time.sleep(backoff)
            else:
                print(f"  ✗ All {retries} attempts failed: {e}")
                return "", 500
    
    return "", 500


def fetch_links(url, retries=10):
    """
    Fetch links results from DeepCrawl API with retry logic and random backoff
    
    Args:
        url: URL to fetch
        retries: Number of retry attempts (default: 10)
    
    Returns:
        Tuple of (response_text, status_code)
    """
    api_url = f"https://api.deepcrawl.dev/links?url={url}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    for attempt in range(retries):
        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            
            # Check if we got a valid response
            if response.status_code == 200 and len(response.text) > 100:
                return response.text, response.status_code
            
            # If response is too small or failed, retry with random backoff
            if attempt < retries - 1:
                # Random backoff between 2 and 8 seconds
                backoff = random.uniform(2, 10)
                print(f"  ⚠ Attempt {attempt + 1} got small/invalid response, retrying in {backoff:.1f}s...")
                time.sleep(backoff)
            else:
                print(f"  ⚠ All {retries} attempts failed for links fetch")
                return response.text, response.status_code
                
        except Exception as e:
            if attempt < retries - 1:
                # Random backoff between 2 and 8 seconds
                backoff = random.uniform(2, 10)
                print(f"  ⚠ Attempt {attempt + 1} failed: {e}, retrying in {backoff:.1f}s...")
                time.sleep(backoff)
            else:
                print(f"  ✗ All {retries} attempts failed: {e}")
                return "", 500
    
    return "", 500
