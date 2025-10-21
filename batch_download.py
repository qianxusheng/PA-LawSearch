import urllib.request
import time
from pathlib import Path
import json

# NOTE：Download data from case.law
#       for each collection, you need to update these variables manually
BASE_URL = "https://static.case.law/pa-commw/" # target URL
OUTPUT_DIR = "data\Pa. Commw" # data path in current project
NUM_VOLUMES = 168  # number of volumes on the target URL

FORMAT = "zip"
PROGRESS_FILE = "download_progress.json"
MAX_RETRIES = 3

Path(OUTPUT_DIR).mkdir(exist_ok=True)

def load_progress():
    """Load download progress"""
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed": [], "failed": []}

def save_progress(progress):
    """Save download progress"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def download_volume(volume_num, retries=MAX_RETRIES):
    """Download a single volume with retry mechanism"""
    url = f"{BASE_URL}{volume_num}.{FORMAT}"
    output_file = f"{OUTPUT_DIR}/{volume_num}.{FORMAT}"

    if Path(output_file).exists():
        print(f"✓ Volume {volume_num} already exists, skipping")
        return True

    for attempt in range(retries):
        try:
            print(f"Downloading volume {volume_num}... (attempt {attempt+1}/{retries})", end=" ", flush=True)

            # Add User-Agent
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            with urllib.request.urlopen(req, timeout=60) as response:
                with open(output_file, 'wb') as out_file:
                    out_file.write(response.read())

            file_size = Path(output_file).stat().st_size / (1024*1024)
            print(f"✓ Done ({file_size:.2f} MB)")
            return True

        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"✗ Not found (404)")
                return False
            print(f"✗ HTTP error {e.code}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print(f"✗ Failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    return False

# Main program
progress = load_progress()
success = len(progress["completed"])

for vol in range(1, NUM_VOLUMES + 1):
    if vol in progress["completed"]:
        print(f"✓ Volume {vol} already completed, skipping")
        continue

    if download_volume(vol):
        progress["completed"].append(vol)
        success += 1
    else:
        if vol not in progress["failed"]:
            progress["failed"].append(vol)

    save_progress(progress)
    time.sleep(0.3)

print(f"\nDownload complete! Success: {success}/{NUM_VOLUMES}")
if progress["failed"]:
    print(f"Failed volumes: {progress['failed']}")
else:
    # Delete progress file if all downloads succeeded
    if Path(PROGRESS_FILE).exists():
        Path(PROGRESS_FILE).unlink()
        print("All downloads successful! Progress file removed.")