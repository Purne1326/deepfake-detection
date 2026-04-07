import requests
import json
from typing import List, Dict, Any

import os

class DummyPlatformScraper:
    def __init__(self, platform_url=None):
        # Default to localhost if no ENV is set (for local dev)
        # Use DUMMY_PLATFORM_URL if in the cloud (Render)
        self.platform_url = platform_url or os.environ.get("DUMMY_PLATFORM_URL", "http://localhost:5001")
        self.api_endpoint = f"{self.platform_url}/api/posts"

    def fetch_new_posts(self) -> List[Dict[str, Any]]:
        """
        Polls the dummy platform API for posts that are not yet taken down.
        Realistically, we would keep track of last_seen_id to avoid rescraping everything.
        """
        try:
            response = requests.get(self.api_endpoint)
            if response.status_code == 200:
                data = response.json()
                return data.get('posts', [])
            else:
                print(f"Scraper Error: Received {response.status_code} from {self.api_endpoint}")
                return []
        except Exception as e:
            print(f"Scraper Exception: Unable to connect to Dummy Platform: {e}")
            print("MEMBER 2 [Fallback]: Returning mock payload since backend isn't started yet.")
            return [{
                "post_id": "test_post_001",
                "username": "bad_actor_1",
                "image_url": "/static/uploads/mock_deepfake.jpg"
            }]

    def download_image(self, image_url_path: str) -> bytes:
        """
        Downloads the raw bytes of the image from the dummy platform.
        """
        full_url = f"{self.platform_url}{image_url_path}"
        try:
            res = requests.get(full_url)
            if res.status_code == 200:
                return res.content
        except Exception as e:
            print(f"Failed to download image {full_url}: {e}")
        return None
