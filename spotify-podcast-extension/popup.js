// Popup script for Spotify Podcast Auto-Fill extension

const SERVER_URL = 'http://localhost:8765'; // Change to 8766 if using different port

// DOM elements
const loadDataButton = document.getElementById('loadDataButton');
const episodeSelectGroup = document.getElementById('episodeSelectGroup');
const episodeSelect = document.getElementById('episodeSelect');
const episodeDetails = document.getElementById('episodeDetails');
const episodeDate = document.getElementById('episodeDate');
const episodeGuest = document.getElementById('episodeGuest');
const fillButton = document.getElementById('fillButton');
const statusDiv = document.getElementById('status');
const serverStatusDiv = document.getElementById('serverStatus');
const serverText = document.getElementById('serverText');

// Store all episodes in memory
let allEpisodes = [];

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Check server status
    await checkServerStatus();

    // Check if episodes are already loaded
    const stored = await chrome.storage.local.get(['allEpisodes']);
    if (stored.allEpisodes && stored.allEpisodes.length > 0) {
        allEpisodes = stored.allEpisodes;
        populateEpisodeDropdown();
        episodeSelectGroup.style.display = 'block';
        fillButton.style.display = 'block';

        // Restore last selected episode
        const lastSelected = await chrome.storage.local.get(['lastSelectedEpisode']);
        if (lastSelected.lastSelectedEpisode) {
            episodeSelect.value = lastSelected.lastSelectedEpisode;
            // Show details for the restored selection
            const episode = allEpisodes.find(ep => ep.episode_number == lastSelected.lastSelectedEpisode);
            if (episode) {
                displayEpisodeDetails(episode);
            }
        }
    }

    // Set up event listeners
    loadDataButton.addEventListener('click', handleLoadData);
    fillButton.addEventListener('click', handleFillButton);
    episodeSelect.addEventListener('change', handleEpisodeSelection);
});

async function checkServerStatus() {
    try {
        const response = await fetch(`${SERVER_URL}/status`, {
            method: 'GET',
            signal: AbortSignal.timeout(3000) // 3 second timeout
        });

        if (response.ok) {
            serverStatusDiv.className = 'server-status online';
            serverText.textContent = '✅ Server running (localhost:8765)';
        } else {
            throw new Error('Server responded with error');
        }
    } catch (error) {
        serverStatusDiv.className = 'server-status offline';
        serverText.textContent = '❌ Server offline - run: python3 episode_server.py';
        loadDataButton.disabled = true;
        fillButton.disabled = true;
    }
}

async function handleLoadData() {
    try {
        loadDataButton.disabled = true;
        loadDataButton.textContent = 'Loading...';
        showStatus('Fetching all episodes from server...', 'info');

        // Fetch all episodes
        const response = await fetch(`${SERVER_URL}/episodes/all`, {
            method: 'GET',
            signal: AbortSignal.timeout(10000) // 10 second timeout
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Store episodes in memory and chrome storage
        allEpisodes = data.episodes || [];
        await chrome.storage.local.set({ allEpisodes: allEpisodes });

        // Sort episodes by episode number in descending order
        allEpisodes.sort((a, b) => b.episode_number - a.episode_number);

        // Populate dropdown
        populateEpisodeDropdown();

        // Show dropdown and fill button
        episodeSelectGroup.style.display = 'block';
        fillButton.style.display = 'block';

        showStatus(`✅ Loaded ${allEpisodes.length} episodes!`, 'success');

    } catch (error) {
        console.error('Load error:', error);
        showStatus(`Error: ${error.message}`, 'error');
    } finally {
        loadDataButton.disabled = false;
        loadDataButton.textContent = 'Load All Episodes';
    }
}

function populateEpisodeDropdown() {
    // Clear existing options except the first one
    episodeSelect.innerHTML = '<option value="">-- Select an episode --</option>';

    // Add episodes to dropdown
    allEpisodes.forEach(episode => {
        const option = document.createElement('option');
        option.value = episode.episode_number;
        option.textContent = `${episode.episode_number}: ${episode.title}`;
        episodeSelect.appendChild(option);
    });
}

async function handleEpisodeSelection() {
    const selectedNumber = episodeSelect.value;
    if (selectedNumber) {
        await chrome.storage.local.set({ lastSelectedEpisode: selectedNumber });
        const episode = allEpisodes.find(ep => ep.episode_number == selectedNumber);
        if (episode) {
            // Show episode details
            displayEpisodeDetails(episode);
            showStatus(`Selected: Episode ${episode.episode_number}`, 'info');
        }
    } else {
        // Hide episode details when no episode is selected
        episodeDetails.style.display = 'none';
    }
}

function displayEpisodeDetails(episode) {
    // Format the date nicely
    let formattedDate = '-';
    if (episode.date) {
        try {
            const date = new Date(episode.date);
            formattedDate = date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (e) {
            formattedDate = episode.date; // Fallback to raw date string
        }
    }

    // Format guest information
    let guestInfo = '-';
    if (episode.name) {
        guestInfo = episode.name;
        if (episode.company) {
            guestInfo += ` (${episode.company})`;
        } else if (episode.occupation) {
            guestInfo += ` (${episode.occupation})`;
        }
    }

    // Update the display
    episodeDate.textContent = formattedDate;
    episodeGuest.textContent = guestInfo;

    // Show the episode details section
    episodeDetails.style.display = 'block';
}

async function handleFillButton() {
    const selectedNumber = episodeSelect.value;

    if (!selectedNumber) {
        showStatus('Please select an episode first', 'error');
        return;
    }

    // Find the selected episode data
    const episodeData = allEpisodes.find(ep => ep.episode_number == selectedNumber);

    if (!episodeData) {
        showStatus('Episode data not found', 'error');
        return;
    }

    try {
        fillButton.disabled = true;
        fillButton.textContent = 'Filling...';
        showStatus(`Filling form with Episode ${episodeData.episode_number}...`, 'info');

        // Check if we're on a Spotify page
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab.url.includes('creators.spotify.com') && !tab.url.includes('podcasters.spotify.com')) {
            throw new Error('Please navigate to creators.spotify.com first');
        }

        // Try to send message to content script, inject if needed
        try {
            await chrome.tabs.sendMessage(tab.id, {
                action: 'fillForm',
                data: episodeData
            });
        } catch (error) {
            if (error.message.includes('Could not establish connection')) {
                // Content script not loaded, inject it
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['content.js']
                });

                // Wait a bit for script to load, then try again
                await new Promise(resolve => setTimeout(resolve, 500));

                await chrome.tabs.sendMessage(tab.id, {
                    action: 'fillForm',
                    data: episodeData
                });
            } else {
                throw error;
            }
        }

        showStatus(`✅ Filled form for episode ${episodeData.episode_number}!`, 'success');

    } catch (error) {
        console.error('Fill error:', error);
        showStatus(`Error: ${error.message}`, 'error');
    } finally {
        fillButton.disabled = false;
        fillButton.textContent = 'Auto-Fill Form';
    }
}


function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';

    // Auto-hide success messages
    if (type === 'success') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 3000);
    }
}