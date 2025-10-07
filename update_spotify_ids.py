#!/usr/bin/env python3
"""
Update all Spotify episode IDs from old Anchor format to new Spotify format.

Requirements:
    pip install spotipy python-dotenv

Setup:
1. Go to https://developer.spotify.com/dashboard
2. Create an app
3. Get your Client ID and Client Secret
4. Create a .env file with:
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret

Usage:
    python update_spotify_ids.py --dry-run  # Preview changes without updating
    python update_spotify_ids.py            # Update all episode files
"""

import os
import re
import sys
import glob
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import click
from typing import Dict, Optional, Tuple

# Load environment variables
load_dotenv()

# Spelskaparna's Spotify show ID (you may need to verify/update this)
SPELSKAPARNA_SHOW_ID = "1NduuMiLdFyKWqnlHHGDJV"


def get_spotify_client():
    """Initialize Spotify client with credentials."""
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("Error: Missing Spotify credentials!")
        print("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
        print("\n1. Go to https://developer.spotify.com/dashboard")
        print("2. Create an app")
        print("3. Add credentials to .env file")
        sys.exit(1)

    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def find_show_id(sp):
    """Find the Spelskaparna show ID."""
    results = sp.search(q="Spelskaparna", type='show', market='SE', limit=5)

    for show in results['shows']['items']:
        if "Spelskaparna" in show['name'] and "Olle" in show['publisher']:
            print(f"Found show: {show['name']} by {show['publisher']}")
            print(f"Show ID: {show['id']}")
            return show['id']

    print("Warning: Could not find Spelskaparna show, using default ID")
    return SPELSKAPARNA_SHOW_ID


def get_all_episodes(sp, show_id, limit=200):
    """Get all episodes from the show."""
    episodes = []
    offset = 0

    while offset < limit:
        try:
            results = sp.show_episodes(show_id, limit=50, offset=offset, market='SE')

            if results and 'items' in results:
                episodes.extend(results['items'])
                print(f"  Fetched {len(results['items'])} episodes (offset: {offset})")
            else:
                print(f"  No items in results at offset {offset}")
                break

            if not results.get('next'):
                break
            offset += 50
        except Exception as e:
            print(f"Error fetching episodes at offset {offset}: {e}")
            break

    return episodes


def parse_episode_number(name: str) -> Optional[int]:
    """Extract episode number from episode name."""
    # Try different patterns
    patterns = [
        r'^(\d+)\s+',           # "171 Guest Name"
        r'^#(\d+)\s+',          # "#171 Guest Name"
        r'Episode\s+(\d+)',     # "Episode 171"
        r'^(\d+)\.',            # "171. Guest Name"
    ]

    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            return int(match.group(1))

    return None


def build_episode_mapping(episodes) -> Dict[int, str]:
    """Build a mapping of episode number to Spotify ID."""
    mapping = {}

    if not episodes:
        print("  No episodes to process")
        return mapping

    for episode in episodes:
        if not episode or 'name' not in episode:
            print(f"  Skipping invalid episode: {episode}")
            continue

        episode_num = parse_episode_number(episode['name'])
        if episode_num:
            mapping[episode_num] = episode['id']
            print(f"  Episode {episode_num}: {episode['name'][:50]}... -> {episode['id']}")

    return mapping


def read_episode_file(filepath: str) -> Tuple[str, Optional[str], Optional[int]]:
    """Read an episode file and extract current Spotify ID and episode number."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract episode number from filename
    filename = os.path.basename(filepath)
    episode_num_match = re.match(r'^(\d+)\.md$', filename)
    episode_num = int(episode_num_match.group(1)) if episode_num_match else None

    # Extract current Spotify ID
    spotify_id_match = re.search(r'spotify_episode_id\s*=\s*"([^"]*)"', content)
    current_id = spotify_id_match.group(1) if spotify_id_match else None

    return content, current_id, episode_num


def update_episode_file(filepath: str, new_spotify_id: str, dry_run: bool = False):
    """Update the Spotify ID in an episode file."""
    content, current_id, episode_num = read_episode_file(filepath)

    if not current_id:
        # No existing spotify_episode_id field
        if dry_run:
            print(f"  Would add: spotify_episode_id = \"{new_spotify_id}\"")
        else:
            # Find where to insert (after libsynid if it exists)
            libsyn_match = re.search(r'(libsynid\s*=\s*"[^"]*"\n)', content)
            if libsyn_match:
                insert_pos = libsyn_match.end()
                new_content = (content[:insert_pos] +
                             f'spotify_episode_id = "{new_spotify_id}"\n' +
                             content[insert_pos:])
            else:
                # Insert before the closing +++
                closing_match = re.search(r'\n\+\+\+', content)
                if closing_match:
                    insert_pos = closing_match.start()
                    new_content = (content[:insert_pos] +
                                 f'\nspotify_episode_id = "{new_spotify_id}"' +
                                 content[insert_pos:])
                else:
                    print(f"  Error: Could not find where to insert Spotify ID")
                    return False

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        return True

    # Check if it's already a new format ID (no dashes, typical length)
    if '-' not in current_id and len(current_id) > 15:
        print(f"  Already has new format ID: {current_id}")
        return False

    if dry_run:
        print(f"  Would update: {current_id} -> {new_spotify_id}")
    else:
        # Replace the old ID with new one
        pattern = r'(spotify_episode_id\s*=\s*)"[^"]*"'
        new_content = re.sub(pattern, rf'\1"{new_spotify_id}"', content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"  Updated: {current_id} -> {new_spotify_id}")

    return True


@click.command()
@click.option('--dry-run', is_flag=True, help='Preview changes without updating files')
@click.option('--episode', type=int, help='Update only specific episode number')
@click.option('--show-id', help='Spotify show ID (will search if not provided)')
def main(dry_run, episode, show_id):
    """Update all Spotify episode IDs to new format."""

    if dry_run:
        print("DRY RUN MODE - No files will be modified\n")

    # Initialize Spotify client
    print("Connecting to Spotify API...")
    sp = get_spotify_client()

    # Find or verify show ID
    if not show_id:
        print("\nSearching for Spelskaparna show...")
        show_id = find_show_id(sp)

    # Get all episodes from Spotify
    print(f"\nFetching episodes from Spotify (show ID: {show_id})...")
    episodes = get_all_episodes(sp, show_id)
    print(f"Found {len(episodes)} episodes on Spotify")

    # Build episode number to Spotify ID mapping
    print("\nBuilding episode mapping...")
    episode_mapping = build_episode_mapping(episodes)
    print(f"Mapped {len(episode_mapping)} episodes")

    # Find all episode files
    episode_files = glob.glob('content/episode/*.md')
    episode_files.sort(key=lambda x: int(re.findall(r'\d+', os.path.basename(x))[0]) if re.findall(r'\d+', os.path.basename(x)) else 0)

    print(f"\nFound {len(episode_files)} local episode files")

    # Update each episode file
    updated = 0
    skipped = 0
    errors = 0

    for filepath in episode_files:
        filename = os.path.basename(filepath)
        _, current_id, episode_num = read_episode_file(filepath)

        if episode and episode_num != episode:
            continue

        print(f"\nProcessing {filename}:")

        if episode_num and episode_num in episode_mapping:
            new_id = episode_mapping[episode_num]
            if update_episode_file(filepath, new_id, dry_run):
                updated += 1
            else:
                skipped += 1
        else:
            print(f"  No Spotify match found for episode {episode_num}")
            if current_id:
                print(f"  Current ID: {current_id}")
            errors += 1

    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Files updated: {updated}")
    print(f"Files skipped: {skipped}")
    print(f"Episodes not found on Spotify: {errors}")

    if dry_run:
        print("\nDRY RUN COMPLETE - No files were modified")
        print("Run without --dry-run to apply changes")
    else:
        print("\nUPDATE COMPLETE")


if __name__ == "__main__":
    main()