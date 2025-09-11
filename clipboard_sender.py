import time
import json
import base64
from io import BytesIO

import pyperclip
import requests
from PIL import ImageGrab, Image

# --- CONFIGURATION ---
# 1. Get this from your Firebase project settings (see README)
FIREBASE_PROJECT_ID = "clipboard-sharer-2d63c"

# 2. Make up a secret channel ID. Use the EXACT same one in the web app.
CHANNEL_ID = "farhan"
# ---------------------

# Base Firestore REST API endpoint for our specific document.
FIRESTORE_BASE_URL = (
    f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/"
    f"databases/(default)/documents/clipboards/{CHANNEL_ID}"
)

def update_firestore(field, value):
    """Sends the provided text or image to the Firestore document."""

    payload = {"fields": {field: {"stringValue": value}, "type": {"stringValue": field}}}

    headers = {"Content-Type": "application/json"}

    url = f"{FIRESTORE_BASE_URL}?updateMask.fieldPaths={field}&updateMask.fieldPaths=type"

    try:
        response = requests.patch(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print(f"[{time.strftime('%H:%M:%S')}] Successfully sent clipboard content.")
    except requests.exceptions.RequestException as e:
        print("Error: Could not connect to Firestore. Check your Project ID and network connection.")
        print(f"Details: {e}")


def read_clipboard():
    """Returns ('text', value) or ('image', base64) if clipboard has content."""
    try:
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image):
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return "image", img_b64
    except Exception:
        pass

    text = pyperclip.paste()
    if text:
        return "text", text

    return None, None

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

    recent = {"text": "", "image": ""}
    try:
        while True:
            # Get the current content of the clipboard.
            field, value = read_clipboard()

            # If the content is new and not empty, send it.
            if field and value and value != recent[field]:
                recent[field] = value
                other = "image" if field == "text" else "text"
                recent[other] = ""
                update_firestore(field, value)

            # Wait for a second before checking again to avoid high CPU usage.
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSender stopped. Goodbye!")

if __name__ == "__main__":
    main()
