#!/usr/bin/env python3
"""Extract structured updates using LLM via OpenRouter API"""
import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class UpdateEntry(BaseModel):
    """Single update entry with title and link"""
    title: str = Field(description="The title of the update or article")
    link: str = Field(description="The corresponding URL/link for this update")

class UpdatesList(BaseModel):
    """List of updates extracted from differences"""
    updates: List[UpdateEntry] = Field(description="List of new updates found")

def call_llm_extract_updates(read_differences: str, links_differences: str, source_name: str) -> UpdatesList:
    """
    Call LLM via OpenRouter to extract structured updates
    
    Args:
        read_differences: Content from read_differences.txt (potential titles)
        links_differences: Content from links_differences.txt (potential links)
        source_name: Name of the source being processed
    
    Returns:
        UpdatesList: Structured list of updates with titles and links
    """
    # Initialize OpenRouter client (OpenAI-compatible API)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    # Prepare the prompt
    system_prompt = """
        You are an expert at extracting structured information from website change logs.
        You will receive two pieces of information:
        1. Read differences: Text content showing new titles, headlines, or article names
        2. Links differences: JSON differences showing new URLs or links

        Your task is to:
        - Identify new articles, papers, or updates from the read differences
        - Match each title with its corresponding link from the links differences
        - Return a structured list of updates, each with a title and link
        - Only include actual new content (ignore metadata, timestamps, or navigation changes)
        - Set confidence level based on how certain you are about the title-link matching

        Be precise and only extract clear, meaningful updates.
    """

    user_prompt = f"""
        Source: {source_name}

        Read Differences (potential titles):
        ```
        {read_differences}
        ```

        Links Differences (potential links):
        ```
        {links_differences}
        ```

        Please extract all new updates, matching titles with their corresponding links.
    """
    
    # Call LLM with structured output
    response = client.beta.chat.completions.parse(
        model="openai/gpt-5-nano",  # You can change this to other models
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=UpdatesList,
        temperature=0.1,  # Low temperature for more consistent extraction
    )
    
    # Extract and return the parsed result
    result = response.choices[0].message.parsed
    return result


def process_folder_updates(folder_name: str) -> Optional[UpdatesList]:
    """
    Process differences files in a folder and extract updates
    
    Args:
        folder_name: Path to folder containing difference files
    
    Returns:
        UpdatesList or None if files don't exist or are empty
    """
    read_diff_path = os.path.join(folder_name, "read_differences.txt")
    links_diff_path = os.path.join(folder_name, "links_differences.txt")
    
    # Check if both files exist
    if not os.path.exists(read_diff_path) or not os.path.exists(links_diff_path):
        print(f"  ⚠ Difference files not found in {folder_name}")
        return None
    
    # Read the differences
    with open(read_diff_path, "r", encoding="utf-8") as f:
        read_differences = f.read().strip()
    
    with open(links_diff_path, "r", encoding="utf-8") as f:
        links_differences = f.read().strip()
    
    # Skip if read differences are empty (no new titles to extract)
    if not read_differences:
        print(f"  ℹ No new content in read differences for {folder_name}")
        return None
    
    # Skip if both are empty
    if not read_differences and not links_differences:
        print(f"  ℹ No differences found in {folder_name}")
        return None
    
    # Extract source name from folder
    source_name = os.path.basename(folder_name)
    
    print(f"  ✓ Calling LLM to extract updates from {source_name}...")
    
    # Call LLM to extract updates
    try:
        updates = call_llm_extract_updates(read_differences, links_differences, source_name)
        
        # Save structured output
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
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python llm_extractor.py <folder_name>")
        print("Example: python llm_extractor.py ieee_jsac")
        sys.exit(1)
    
    folder = sys.argv[1]
    result = process_folder_updates(folder)
    
    if result:
        print("\n📋 Extracted Updates:")
        for i, update in enumerate(result.updates, 1):
            print(f"{i}. {update.title}")
            print(f"   🔗 {update.link}")
            print(f"   📊 Confidence: {update.confidence}")
            print()
