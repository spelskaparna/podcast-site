# Create New Episode

1. Run `python pending-episodes.py` to see unmatched transcriptions and candidate episodes
2. For the oldest unmatched transcription:
   - Read the .txt transcription file
   - If a candidate episode matches, use that episode number and spotify_episode_id
   - Otherwise, determine the next episode number from existing files
3. Use `content/episode/175.md` as the template example
4. Create the episode file with:
   - TOML frontmatter (date from filename, guest name, subtitle, company, occupation, spotify_episode_id)
   - Brief 2-3 paragraph description based on the transcription
   - A "# Länkar" section with relevant links mentioned
5. Update `.matched_episodes.json` - add `{"TranscriptionBase": episode_number}` (e.g., `{"Spelskaparna_Indo_250903": 172}`)

Keep the description concise - summarize, don't transcribe.
