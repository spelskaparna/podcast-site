// Content script for Spotify for Creators Auto-Fill extension
// Runs on creators.spotify.com pages to handle form filling

console.log('[Spelskaparna Auto-Fill] Content script loaded for Spotify for Creators - Version 2.0');

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('[Spelskaparna Auto-Fill] Message received:', request);

    if (request.action === 'fillForm') {
        try {
            // Since this is a React SPA, we might need to wait for elements to load
            setTimeout(() => {
                try {
                    const result = fillSpotifyForm(request.data);
                    sendResponse({ success: true, result });
                } catch (error) {
                    console.error('[Spelskaparna Auto-Fill] Error:', error);
                    sendResponse({ success: false, error: error.message });
                }
            }, 1000); // Wait 1 second for React to render
        } catch (error) {
            console.error('[Spelskaparna Auto-Fill] Error:', error);
            sendResponse({ success: false, error: error.message });
        }
    }

    return true; // Keep the message channel open for async response
});

function fillSpotifyForm(episodeData) {
    console.log('[Spelskaparna Auto-Fill] Filling Spotify form with data:', episodeData);

    // Show status notification
    showNotification('Finding form fields on Spotify for Creators...', 'info');

    // Find form fields with selectors specific to Spotify for Creators
    const fields = findSpotifyFormFields();
    console.log('[Spelskaparna Auto-Fill] Found fields:', fields);

    if (Object.keys(fields).length === 0) {
        throw new Error('No form fields found. Make sure you\'re on a Spotify for Creators episode edit/upload page.');
    }

    let filledCount = 0;

    // Fill title field
    if (fields.title && episodeData.title) {
        const success = fillReactField(fields.title, episodeData.title, 'title');
        if (success) filledCount++;
    }

    // Fill description field - prefer HTML if available, fallback to text
    if (fields.description && (episodeData.description_html || episodeData.description_text)) {
        const descriptionContent = episodeData.description_html || episodeData.description_text;
        const success = fillReactField(fields.description, descriptionContent, 'description', episodeData.description_html ? 'html' : 'text');
        if (success) filledCount++;
    }

    if (filledCount > 0) {
        showNotification(`✅ Filled ${filledCount} fields successfully!`, 'success');

        // Log summary to console
        console.group('[Spelskaparna Auto-Fill] Episode Summary');
        console.log('Episode:', episodeData.episode_number);
        console.log('Title:', episodeData.title);
        console.log('Guest:', episodeData.name);
        console.log('Subtitle:', episodeData.subtitle);
        console.log('Description length:', episodeData.description_text?.length || 0);
        console.groupEnd();

        return {
            filledCount,
            fields: Object.keys(fields),
            episodeNumber: episodeData.episode_number
        };
    } else {
        throw new Error('No fields were filled. The Spotify form structure may have changed.');
    }
}

function findSpotifyFormFields() {
    const fields = {};

    // Comprehensive selectors for Spotify for Creators
    const fieldSelectors = {
        title: [
            // Common React form patterns
            'input[placeholder*="title" i]',
            'input[placeholder*="episode" i]',
            'input[name*="title" i]',
            'input[name*="episodeTitle" i]',
            'input[aria-label*="title" i]',
            'input[aria-label*="episode" i]',

            // Spotify-specific selectors (these might change)
            'input[data-testid*="title"]',
            'input[data-testid*="episode"]',
            '[data-testid*="title"] input',
            '[data-testid*="episode"] input',

            // Generic selectors as fallback
            'form input[type="text"]:first-of-type',
            'input[type="text"]',

            // By CSS classes (might be obfuscated)
            '[class*="title" i] input',
            '[class*="episode" i] input',

            // Broader React patterns
            'div[role="textbox"]',
            '[contenteditable="true"]'
        ],

        description: [
            // Description/summary field selectors
            'textarea[placeholder*="description" i]',
            'textarea[placeholder*="summary" i]',
            'textarea[placeholder*="episode" i]',
            'textarea[name*="description" i]',
            'textarea[name*="summary" i]',
            'textarea[aria-label*="description" i]',
            'textarea[aria-label*="summary" i]',

            // Spotify-specific selectors
            'textarea[data-testid*="description"]',
            'textarea[data-testid*="summary"]',
            '[data-testid*="description"] textarea',
            '[data-testid*="summary"] textarea',

            // Rich text editors common in React apps
            '[contenteditable="true"]',
            'div[role="textbox"]',
            '.ql-editor', // Quill editor
            '.tox-edit-area', // TinyMCE
            '.DraftEditor-root', // Draft.js
            '[data-slate-editor="true"]', // Slate.js

            // Generic textarea fallback
            'textarea',

            // By CSS classes
            '[class*="description" i] textarea',
            '[class*="summary" i] textarea',
            '[class*="episode" i] textarea'
        ]
    };

    // Try to find each field type
    for (const [fieldName, selectors] of Object.entries(fieldSelectors)) {
        for (const selector of selectors) {
            try {
                const element = document.querySelector(selector);
                if (element && isVisible(element) && isInteractable(element)) {
                    // Skip radio buttons and checkboxes for date/time fields
                    if (element.tagName === 'INPUT' && (element.type === 'radio' || element.type === 'checkbox')) {
                        console.debug(`[Spelskaparna Auto-Fill] Skipping ${element.type} input for ${fieldName}`);
                        continue;
                    }
                    fields[fieldName] = element;
                    console.log(`[Spelskaparna Auto-Fill] Found ${fieldName} field:`, selector, `(type: ${element.type || 'text'})`);
                    break;
                }
            } catch (e) {
                // Continue to next selector
                console.debug(`[Spelskaparna Auto-Fill] Selector failed: ${selector}`, e);
            }
        }
    }

    return fields;
}

function isVisible(element) {
    if (!element) return false;

    const style = window.getComputedStyle(element);
    return style.display !== 'none' &&
           style.visibility !== 'hidden' &&
           style.opacity !== '0' &&
           element.offsetWidth > 0 &&
           element.offsetHeight > 0;
}

function isInteractable(element) {
    if (!element) return false;

    // Check if element is disabled
    if (element.disabled) return false;

    // Check if element is readonly
    if (element.readOnly) return false;

    // Check if element is inside a form or contenteditable
    return element.tagName === 'INPUT' ||
           element.tagName === 'TEXTAREA' ||
           element.contentEditable === 'true' ||
           element.getAttribute('role') === 'textbox';
}

function fillReactField(element, value, fieldType, contentType = 'text') {
    try {
        console.log(`[Spelskaparna Auto-Fill] Filling ${fieldType} field with ${contentType}:`, value.substring(0, 100) + '...');

        // Focus the element first
        element.focus();
        element.click(); // Also trigger click to ensure React recognizes interaction

        // For React apps, we need to trigger events properly
        if (element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'textarea') {
            // First, trigger focus events
            element.dispatchEvent(new FocusEvent('focusin', { bubbles: true }));
            element.dispatchEvent(new FocusEvent('focus', { bubbles: true }));

            // Clear existing value first (only for text-like inputs)
            if (element.type !== 'radio' && element.type !== 'checkbox' && element.type !== 'button') {
                if (element.select) element.select();
                if (element.setSelectionRange && element.value) {
                    try {
                        element.setSelectionRange(0, element.value.length);
                    } catch (e) {
                        // Some input types don't support selection
                        console.debug('[Spelskaparna Auto-Fill] Selection not supported for this input type');
                    }
                }
            }

            // Set the value using React-compatible method
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLTextAreaElement.prototype, 'value'
            ).set;

            if (element.tagName.toLowerCase() === 'input') {
                nativeInputValueSetter.call(element, value);
            } else {
                nativeTextAreaValueSetter.call(element, value);
            }

            // Trigger comprehensive React events
            const events = [
                new KeyboardEvent('keydown', { bubbles: true, key: 'a', keyCode: 65 }),
                new KeyboardEvent('keypress', { bubbles: true, key: 'a', keyCode: 65 }),
                new Event('input', { bubbles: true, inputType: 'insertText' }),
                new KeyboardEvent('keyup', { bubbles: true, key: 'a', keyCode: 65 }),
                new Event('change', { bubbles: true }),
                new FocusEvent('blur', { bubbles: true })
            ];

            // Dispatch events with small delays to mimic human interaction
            events.forEach((event, index) => {
                setTimeout(() => {
                    element.dispatchEvent(event);
                }, index * 10);
            });

            // Also trigger React-specific events with different approaches
            setTimeout(() => {
                const reactEvent = new Event('input', { bubbles: true });
                reactEvent.simulated = true;
                element.dispatchEvent(reactEvent);

                // Try triggering on React fiber
                const reactFiber = element._reactInternalFiber || element._reactInternalInstance;
                if (reactFiber) {
                    const onChange = reactFiber.memoizedProps?.onChange;
                    if (onChange) {
                        onChange({ target: element, currentTarget: element });
                    }
                }
            }, 50);

        } else if (element.contentEditable === 'true' || element.getAttribute('role') === 'textbox') {
            // Handle contentEditable elements (rich text editors)
            element.focus();
            element.click();

            // Clear existing content
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(element);
            selection.removeAllRanges();
            selection.addRange(range);

            // Clear content
            if (element.innerHTML) {
                element.innerHTML = '';
            }

            // Set new content based on type
            if (contentType === 'html' && fieldType === 'description') {
                element.innerHTML = value;
            } else {
                element.textContent = value;
            }

            // Trigger comprehensive events for contentEditable
            const events = [
                new KeyboardEvent('keydown', { bubbles: true, key: 'a', keyCode: 65 }),
                new Event('input', { bubbles: true, inputType: 'insertText' }),
                new Event('change', { bubbles: true }),
                new KeyboardEvent('keyup', { bubbles: true, key: 'a', keyCode: 65 }),
                new FocusEvent('blur', { bubbles: true })
            ];

            events.forEach((event, index) => {
                setTimeout(() => {
                    element.dispatchEvent(event);
                }, index * 10);
            });
        }

        // Wait a bit for React to process, then verify
        setTimeout(() => {
            const currentValue = element.value || element.textContent || element.innerHTML;
            const success = currentValue && currentValue.includes(value.substring(0, 50));

            if (success) {
                console.log(`[Spelskaparna Auto-Fill] Successfully filled ${fieldType} field - Visual update confirmed`);
            } else {
                console.warn(`[Spelskaparna Auto-Fill] Visual update may not have occurred for ${fieldType} field. Current value:`, currentValue);
                // Try one more approach - direct manipulation
                if (element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'textarea') {
                    element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        }, 200);

        return true;

    } catch (error) {
        console.error(`[Spelskaparna Auto-Fill] Error filling ${fieldType} field:`, error);
        return false;
    }
}

function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.getElementById('spelskaparna-notification');
    if (existing) {
        existing.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'spelskaparna-notification';
    notification.textContent = message;

    // Style the notification with Spotify colors
    const colors = {
        success: { bg: '#1db954', text: 'white' },
        error: { bg: '#e22134', text: 'white' },
        info: { bg: '#1e3264', text: 'white' }
    };

    const color = colors[type] || colors.info;

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999999;
        background: ${color.bg};
        color: ${color.text};
        padding: 12px 16px;
        border-radius: 8px;
        font-family: 'Spotify Circular', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 16px rgba(0,0,0,0.24);
        max-width: 300px;
        word-wrap: break-word;
        transition: all 0.3s ease;
        border: none;
    `;

    document.body.appendChild(notification);

    // Auto-remove after delay
    setTimeout(() => {
        if (notification && notification.parentNode) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }, type === 'success' ? 4000 : 6000);
}

// Debug: Verify all functions are loaded
console.log('[Spelskaparna Auto-Fill] All functions loaded:', {
    fillSpotifyForm: typeof fillSpotifyForm,
    findSpotifyFormFields: typeof findSpotifyFormFields,
    fillReactField: typeof fillReactField,
    isVisible: typeof isVisible,
    isInteractable: typeof isInteractable,
    showNotification: typeof showNotification
});