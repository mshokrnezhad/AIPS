#!/usr/bin/env python3
"""Extract structured updates using LLM via OpenRouter API"""
import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class UpdateEntry(BaseModel):
    """Single update entry with title and link"""
    title: str = Field(description="The title of the update or article")
    link: str = Field(description="The corresponding URL/link for this update")


class UpdatesList(BaseModel):
    """List of updates extracted from differences"""
    updates: List[UpdateEntry] = Field(description="List of new updates found")


def call_llm_extract_updates(differences: str, source_name: str, source_url: str = "") -> UpdatesList:
    """
    Call LLM via OpenRouter to extract structured updates from a Markdown diff.

    Args:
        differences: Added lines from differences.md (new content since last run)
        source_name: Name of the source being processed
        source_url: The URL being monitored (used to filter self-referential links)

    Returns:
        UpdatesList: Structured list of updates with titles and links
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = """
        You are an expert at filtering and extracting structured information from website change logs.
        You will receive lines that were added to a webpage since the last monitoring check.

        Your ONLY job is to extract genuinely NEW PUBLISHED CONTENT that a human subscriber
        would want to be notified about — such as:
        - A new article, blog post, or research paper
        - A new product release or version announcement
        - A new event, conference, or call-for-papers posting

        Apply this single semantic test to every candidate:
        "Would a reader who follows this source specifically want to receive an email
        notification about this item?" If the answer is no or uncertain, discard it.

        ALWAYS DISCARD — regardless of how prominent they appear in the diff:
        - The page itself or its own URL (a link pointing back to the monitored page)
        - Static or recurring page sections: calls-for-papers landing pages, submission
          guidelines, author instructions, editorial board listings
        - Cookie / GDPR / privacy consent notices
        - Newsletter, subscription, or mailing-list sign-up prompts
        - Login, register, or account management prompts
        - Paywalls or access-restriction messages
        - Navigation menus, sidebars, breadcrumbs, headers, footers
        - Advertisements, sponsored content labels, or promotional banners
        - Pagination controls, "Load more" buttons, or UI widgets
        - Session-specific or personalised text (e.g. "Welcome back", "Recently viewed")
        - Pure metadata changes: updated timestamps, view/download counts, rankings
        - Social sharing buttons or share counts
        - Anything that is clearly website UI chrome rather than editorial content

        Each extracted item MUST have both a meaningful human-readable title AND a direct
        link to the specific new content. If either is missing or the link points to the
        monitored page itself, omit the item entirely.

        Return an empty list if nothing in the diff qualifies. It is far better to return
        nothing than to return noise.
    """

    user_prompt = f"""
        Monitored source: {source_name}
        Source URL (ignore any link that points here): {source_url}

        Lines added since last check (Markdown diff):
        ```
        {differences}
        ```

        Extract only the new published content items. Discard everything else.
    """

    response = client.beta.chat.completions.parse(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=UpdatesList,
        temperature=0.1,
    )

    return response.choices[0].message.parsed


def process_folder_updates(folder_name: str, source_url: str = "") -> Optional[UpdatesList]:
    """
    Read differences.md from a folder and extract structured updates via LLM.

    Args:
        folder_name: Path to folder containing differences.md
        source_url: The URL being monitored (passed to LLM to filter self-referential links)

    Returns:
        UpdatesList or None if the file is missing or empty
    """
    diff_path = os.path.join(folder_name, "differences.md")

    if not os.path.exists(diff_path):
        print(f"  ⚠ differences.md not found in {folder_name}")
        return None

    with open(diff_path, "r", encoding="utf-8") as f:
        differences = f.read().strip()

    if not differences:
        print(f"  ℹ No new content in differences.md for {folder_name}")
        return None

    source_name = os.path.basename(folder_name)
    print(f"  ✓ Calling LLM to extract updates from {source_name}...")

    try:
        updates = call_llm_extract_updates(differences, source_name, source_url)

        output_path = os.path.join(folder_name, "extracted_updates.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(updates.model_dump(), f, indent=2, ensure_ascii=False)

        print(f"  ✓ Extracted {len(updates.updates)} updates")
        print(f"  ✓ Saved to {output_path}")

        return updates

    except Exception as e:
        print(f"  ✗ Error extracting updates: {e}")
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python llm_extractor.py <folder_name>")
        print("Example: python llm_extractor.py ieee_jsac")
        sys.exit(1)

    folder = sys.argv[1]
    result = process_folder_updates(folder)

    if result:
        print("\nExtracted Updates:")
        for i, update in enumerate(result.updates, 1):
            print(f"{i}. {update.title}")
            print(f"   {update.link}")
            print()
