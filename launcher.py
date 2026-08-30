import os
import threading
import time
import webview

from waitress import serve
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Force desktop mode
os.environ["APP_MODE"] = "desktop"

from jeevanyaan.wsgi import application


def start_server():
    serve(application, host='127.0.0.1', port=8000)


# Start Django server in background
t = threading.Thread(target=start_server)
t.daemon = True
t.start()

# Small delay to ensure server starts
time.sleep(2)

# Open desktop window
webview.create_window(
    "JeevanYaan AI Assistant",
    "http://127.0.0.1:8000",
    width=1400,
    height=900,
    resizable=True
)

webview.start()