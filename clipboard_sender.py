import time
import pyperclip
import requests
import json

# --- CONFIGURATION ---
# 1. Get this from your Firebase project settings (see README)
FIREBASE_PROJECT_ID = "clipboard-sharer-2d63c"

# 2. Make up a secret channel ID. Use the EXACT same one in the web app.
CHANNEL_ID = "farhan"
# ---------------------

# Firestore REST API endpoint for our specific document.
# The `?updateMask.fieldPaths=text` part ensures we only update the 'text' field.
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/clipboards/{CHANNEL_ID}?updateMask.fieldPaths=text"

def update_firestore(text):
    """Sends the provided text to the Firestore document."""

    # The data needs to be in a specific format for the Firestore REST API.
    payload = {
        "fields": {
            "text": {
                "stringValue": text
            }
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # We use PATCH to create the document or update it if it already exists.
        response = requests.patch(FIRESTORE_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print(f"[{time.strftime('%H:%M:%S')}] Successfully sent clipboard content.")
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to Firestore. Check your Project ID and network connection.")
        print(f"Details: {e}")

def main():
    """Main loop to monitor the clipboard."""
    if FIREBASE_PROJECT_ID == "your-firebase-project-id" or CHANNEL_ID == "your-secret-channel-name":
        print("!!! IMPORTANT !!!")
        print("Please open this script (clipboard_sender.py) and set your FIREBASE_PROJECT_ID and CHANNEL_ID.")
        return

    print("Clipboard sender is running...")
    print(f"Project ID: {FIREBASE_PROJECT_ID}")
    print(f"Channel ID: {CHANNEL_ID}")
    print("Press Ctrl+C to stop.")

    recent_value = ""
    try:
        while True:
            # Get the current content of the clipboard.
            clipboard_value = pyperclip.paste()

            # If the content is new and not empty, send it.
            if clipboard_value and clipboard_value != recent_value:
                recent_value = clipboard_value
                update_firestore(clipboard_value)

            # Wait for a second before checking again to avoid high CPU usage.
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSender stopped. Goodbye!")

if __name__ == "__main__":
    main()