#!/usr/bin/env python3
"""
Simple local web server that serves episode data for the browser bookmarklet.
Run this script, then use the bookmarklet to auto-fill Anchor.fm forms.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import click
from typing import Dict, Any
import episode_parser as ep


class EpisodeDataHandler(BaseHTTPRequestHandler):
    """HTTP handler for serving episode data."""

    def do_GET(self):
        """Handle GET requests for episode data."""
        parsed_url = urlparse(self.path)

        # Enable CORS for browser access
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        try:
            if parsed_url.path == '/episode':
                # Get episode number from query parameter
                query_params = parse_qs(parsed_url.query)
                episode_num = query_params.get('number', [None])[0]

                if not episode_num:
                    self.wfile.write(json.dumps({'error': 'Episode number required'}).encode())
                    return

                episode_num = int(episode_num)
                episode_data = self.get_episode_data(episode_num)
                self.wfile.write(json.dumps(episode_data).encode())

            elif parsed_url.path == '/episodes/all':
                # Get all episodes
                all_episodes = self.get_all_episodes()
                self.wfile.write(json.dumps({'episodes': all_episodes}).encode())

            elif parsed_url.path == '/status':
                # Health check endpoint
                self.wfile.write(json.dumps({'status': 'running'}).encode())

            else:
                self.wfile.write(json.dumps({'error': 'Not found'}).encode())

        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def get_episode_data(self, episode_number: int) -> Dict[str, Any]:
        """Extract episode data from markdown files."""
        try:
            # Get basic episode info
            title = ep.extract_title(episode_number)
            description_html = ep.extract_description(episode_number)
            description_text = ep.extract_description_text(episode_number)
            date = ep.extract_date(episode_number)
            name, occupation, company, subtitle = ep.extract_meta_data(episode_number)

            # Create clean text description (no HTML)
            import re
            from html import unescape

            # Remove HTML tags and clean up
            clean_description = re.sub(r'<[^>]+>', '', description_html)
            clean_description = unescape(clean_description)
            clean_description = re.sub(r'\s+', ' ', clean_description).strip()

            return {
                'episode_number': episode_number,
                'title': title,
                'description_html': description_html,
                'description_text': clean_description,
                'summary': description_text.replace('\n', ' '),
                'name': name,
                'occupation': occupation,
                'company': company,
                'subtitle': subtitle,
                'date': date.isoformat() if date else None,
                'author': 'Olle Landin'
            }

        except Exception as e:
            raise Exception(f"Could not read episode {episode_number}: {str(e)}")

    def get_all_episodes(self) -> list:
        """Get all available episodes."""
        import glob
        import os

        # Find all episode markdown files
        episode_files = glob.glob('content/episode/*.md')
        episodes = []

        for file_path in episode_files:
            try:
                # Extract episode number from filename
                filename = os.path.basename(file_path)
                if filename.endswith('.md'):
                    episode_num_str = filename[:-3]  # Remove .md extension

                    # Try to parse as integer
                    try:
                        episode_number = int(episode_num_str)
                    except ValueError:
                        continue  # Skip files that don't have numeric names

                    # Get episode data
                    episode_data = self.get_episode_data(episode_number)
                    episodes.append(episode_data)

            except Exception as e:
                print(f"Warning: Could not load episode from {file_path}: {e}")
                continue

        # Sort by episode number
        episodes.sort(key=lambda ep: ep['episode_number'], reverse=True)

        print(f"Loaded {len(episodes)} episodes")
        return episodes

    def log_message(self, format, *args):
        """Override to reduce log spam."""
        pass


class EpisodeServer:
    """Local server for serving episode data."""

    def __init__(self, port: int = 8765):
        self.port = port
        self.server = None
        self.server_thread = None

    def start(self):
        """Start the server in a background thread."""
        self.server = HTTPServer(('localhost', self.port), EpisodeDataHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"Episode data server running at http://localhost:{self.port}")
        print(f"Test single episode: http://localhost:{self.port}/episode?number=170")
        print(f"Test all episodes: http://localhost:{self.port}/episodes/all")

    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("Server stopped")


@click.command()
@click.option('--port', default=8765, help='Port to run the server on')
@click.option('--test-episode', type=int, help='Test with specific episode number')
def main(port: int, test_episode: int):
    """
    Start a local web server to serve episode data for browser bookmarklets.

    This server provides episode data that can be consumed by browser
    bookmarklets to auto-fill podcast upload forms.
    """
    server = EpisodeServer(port)

    try:
        server.start()

        if test_episode:
            print(f"\nTesting with episode {test_episode}...")
            import requests
            try:
                response = requests.get(f"http://localhost:{port}/episode?number={test_episode}")
                if response.status_code == 200:
                    data = response.json()
                    print("✓ Episode data retrieved successfully:")
                    print(f"  Title: {data.get('title', 'N/A')}")
                    print(f"  Description length: {len(data.get('description_text', ''))}")
                else:
                    print(f"✗ Error: {response.status_code}")
            except Exception as e:
                print(f"✗ Test failed: {e}")

        print(f"\nServer is running. Use Ctrl+C to stop.")
        print(f"Next: Create and use the browser bookmarklet to auto-fill forms.")

        # Keep running until interrupted
        try:
            while True:
                server.server_thread.join(1)
        except KeyboardInterrupt:
            pass

    finally:
        server.stop()


if __name__ == "__main__":
    main()