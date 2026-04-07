import requests
from typing import Dict, Any

class DummyTakedownHandler:
    def __init__(self, platform_url="http://localhost:5001"):
        self.platform_url = platform_url

    def report_post(self, post_id: str, url: str, reason: str, evidence: dict) -> Dict[str, Any]:
        """
        Executes a real takedown on the dummy social platform API.
        """
        api_endpoint = f"{self.platform_url}/api/posts/{post_id}/takedown"
        
        payload = {
            "reason": reason,
            "case_id": evidence.get("case_id", "Unknown")
        }
        
        try:
            response = requests.post(api_endpoint, json=payload, headers={"X-API-Key": "dummy_secret_key"})
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "SUCCESS",
                    "takedown_at": data.get("taken_down_at"),
                    "message": "Post was successfully removed via dummy API."
                }
            else:
                return {
                    "status": "ERROR",
                    "message": f"API returned {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Failed to connect to dummy platform: {str(e)}"
            }
