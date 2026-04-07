import json
import os
import uuid
from datetime import datetime

class ReportingEngine:
    def __init__(self, reports_dir="reports"):
        self.reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), reports_dir)
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_evidence_packet(self, case_payload: dict, detection_data: dict, decision: dict) -> dict:
        """
        Builds the standardized 'evidence packet' dict from Member 2/3 inputs.
        Strips out all raw image paths and embeddings to comply with policy.
        """
        packet = {
            "case_id": case_payload.get("match_id", str(uuid.uuid4())),
            "timestamp": datetime.utcnow().isoformat(),
            "platform": case_payload.get("platform", "Unknown"),
            "post_id": case_payload.get("post_id", "Unknown"),
            "post_url": case_payload.get("url", "Unknown"),
            "victim_user_id": case_payload.get("user_id", "Unknown"),
            "match_confidence": case_payload.get("confidence", 0.0),
            
            "analysis": {
                "risk_level": detection_data.get("overall_risk_level", "low"),
                "deepfake_score": detection_data.get("deepfake", {}).get("score", 0.0),
                "deepfake_confidence": detection_data.get("deepfake", {}).get("confidence", 0.0),
                "nudity_score": detection_data.get("nudity", {}).get("score", 0.0),
                "nudity_detected": detection_data.get("nudity", {}).get("detected", False),
            },
            
            "compliance_decision": decision,
            "narrative": self._build_narrative(case_payload, detection_data, decision)
        }

        # Persist standard JSON report format for audit
        filename = f"{packet['case_id']}_{packet['platform']}_{packet['post_id']}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(packet, f, indent=4)
            
        print(f"Evidence packet written to {filepath}")
        return packet

    def _build_narrative(self, payload: dict, data: dict, decision: dict) -> str:
        s = f"On {datetime.utcnow().isoformat()}, content published on {payload.get('platform', 'Unknown')} "
        s += f"(Post: {payload.get('post_id')}) was matched to user {payload.get('user_id')} "
        s += f"with {payload.get('confidence', 0):.2f} confidence. "
        s += f"Risk level assessed as {data.get('overall_risk_level', 'UNKNOWN').upper()}. "
        if decision.get("allow_auto_action"):
            s += "Automatic takedown thresholds were met and action initiated."
        elif decision.get("manual_review_required"):
            s += f"Manual review flagged. Reason: {decision.get('reason')}"
        return s
