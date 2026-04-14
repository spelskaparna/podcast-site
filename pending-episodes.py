#!/usr/bin/env python3
"""
List transcription files that don't have matching episode files yet.
Outputs candidate episodes for Claude to match.

Usage:
    python pending-episodes.py
"""

import os
import re
import json
import glob
from datetime import datetime
from typing import Dict, List, Optional, Tuple

CACHE_FILE = ".matched_episodes.json"
EPISODE_DIR = "content/episode"
TRANSCRIPTION_PATTERN = "Spelskaparna_*.txt"


def parse_transcription_filename(filename: str) -> Optional[Tuple[str, datetime]]:
    """Parse guest name and date from transcription filename."""
    # Pattern: Spelskaparna_{Guest}_{YYMMDD}.txt
    match = re.match(r'Spelskaparna_(.+)_(\d{6})\.txt$', filename)
    if not match:
        return None

    guest = match.group(1)
    date_str = match.group(2)

    # Parse YYMMDD
    try:
        year = 2000 + int(date_str[:2])
        month = int(date_str[2:4])
        day = int(date_str[4:6])
        date = datetime(year, month, day)
    except ValueError:
        return None

    return guest, date


def parse_episode_frontmatter(filepath: str) -> Optional[Dict]:
    """Extract frontmatter from an episode markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract TOML frontmatter between +++ markers
    match = re.match(r'\+\+\+\n(.*?)\n\+\+\+', content, re.DOTALL)
    if not match:
        return None

    frontmatter = match.group(1)
    data = {}

    # Parse episode number from filename
    basename = os.path.basename(filepath)
    num_match = re.match(r'(\d+)\.md$', basename)
    if num_match:
        data['episode_num'] = int(num_match.group(1))

    # Parse key fields
    for key in ['date', 'name', 'subtitle', 'spotify_episode_id', 'company', 'occupation']:
        pattern = rf'{key}\s*=\s*"([^"]*)"'
        m = re.search(pattern, frontmatter)
        if m:
            data[key] = m.group(1)
        else:
            # Try date format without quotes
            if key == 'date':
                m = re.search(r'date\s*=\s*(\S+)', frontmatter)
                if m:
                    data[key] = m.group(1)

    return data


def load_cache() -> Dict[str, int]:
    """Load matched episodes cache. Returns {transcription_base: episode_num}"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}


def get_all_episodes() -> List[Dict]:
    """Get all episode metadata."""
    episodes = []
    for filepath in glob.glob(f"{EPISODE_DIR}/*.md"):
        data = parse_episode_frontmatter(filepath)
        if data and 'episode_num' in data:
            episodes.append(data)

    # Sort by episode number
    episodes.sort(key=lambda x: x['episode_num'])
    return episodes


def get_unmatched_transcriptions() -> List[Tuple[str, str, datetime]]:
    """Get transcription files not in cache. Returns [(filename, guest, date)]"""
    cache = load_cache()
    unmatched = []

    for filepath in glob.glob(TRANSCRIPTION_PATTERN):
        filename = os.path.basename(filepath)
        base = filename.replace('.txt', '')

        if base in cache:
            continue

        parsed = parse_transcription_filename(filename)
        if parsed:
            guest, date = parsed
            unmatched.append((filename, guest, date))

    # Sort by date (oldest first)
    unmatched.sort(key=lambda x: x[2])
    return unmatched


def main():
    unmatched = get_unmatched_transcriptions()

    if not unmatched:
        print("No unmatched transcriptions found.")
        return

    episodes = get_all_episodes()

    print(f"Found {len(unmatched)} unmatched transcription(s):\n")

    for filename, guest, date in unmatched:
        print(f"## Transcription: {filename}")
        print(f"   Guest hint: {guest}")
        print(f"   Date: {date.strftime('%Y-%m-%d')}")
        print()

        # Find candidate episodes (date >= transcription date)
        candidates = [
            ep for ep in episodes
            if 'date' in ep and ep['date'][:10] >= date.strftime('%Y-%m-%d')
        ]

        if candidates:
            print("   Candidate episodes:")
            for ep in candidates[:10]:  # Limit to 10 candidates
                name = ep.get('name', 'Unknown')
                subtitle = ep.get('subtitle', '')[:40]
                ep_date = ep.get('date', '')[:10]
                spotify = ep.get('spotify_episode_id', '')
                print(f"   - {ep['episode_num']}: {name} - {subtitle}... ({ep_date}, spotify: {spotify})")
        else:
            print("   No candidate episodes found (may need to create new)")

        print()


if __name__ == "__main__":
    main()
