# Spotify Podcast Extension for Spelskaparna

A Chrome extension that automatically fills Spotify for Creators upload forms with episode data from your Hugo site.

## Installation

### Step 1: Install the Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Select the `spotify-podcast-extension` folder
5. The extension should now appear in your browser toolbar

### Step 2: Start the Local Server

The extension needs your local episode data server running:

```bash
cd /Users/oloflandin/Programming/podcast-site
python3 episode_server.py
```

Keep this running while you use the extension.

## Usage

1. **Go to Spotify for Creators**: Navigate to your creators.spotify.com dashboard
2. **Start uploading**: Begin creating a new episode or editing an existing one
3. **Click the extension**: Click the microphone icon in your browser toolbar
4. **Enter episode number**: Type the episode number (e.g., 170)
5. **Auto-fill**: Click "Auto-Fill Form" and watch it populate the fields!

## Features

- ✅ **Auto-detects form fields** on Spotify for Creators
- ✅ **Fills title and description** from your Hugo episode files
- ✅ **Shows server status** (online/offline)
- ✅ **Remembers last episode number** for quick re-use
- ✅ **Visual feedback** with success/error notifications
- ✅ **Works on all Spotify for Creators pages** with forms

## Troubleshooting

### Extension not working?
- Make sure you're on a `creators.spotify.com` page
- Check that the local server is running (`python3 episode_server.py`)
- Look for error messages in the extension popup

### Server offline?
```bash
cd /Users/oloflandin/Programming/podcast-site
python3 episode_server.py --test-episode 170
```

### Form not filling?
- Check the browser console (F12) for error messages
- The extension logs detailed information to help debug issues
- Form selectors may need updating if Spotify for Creators changes their interface

## Development

### File Structure
```
spotify-podcast-extension/
├── manifest.json       # Extension configuration
├── popup.html          # Extension popup interface
├── popup.js           # Popup logic
├── content.js         # Form filling logic
├── icon*.png          # Extension icons
└── README.md          # This file
```

### Updating the Extension
After making changes:
1. Go to `chrome://extensions/`
2. Click the refresh button on the extension card
3. The changes will be loaded immediately

## Security Notes

- The extension only works on `creators.spotify.com` and `podcasters.spotify.com` domains
- It only communicates with your local server (`localhost:8765`)
- No data is sent to external servers
- All episode data stays on your computer

## Support

If you encounter issues:
1. Check the browser console for error messages
2. Verify the local server is running and responding
3. Make sure you're using the latest version of the extension