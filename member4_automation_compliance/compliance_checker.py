from typing import Dict, Any

class ComplianceChecker:
    def __init__(self, config: Dict[str, Any]):
        """
        Loads the threshold and compliance definitions from config.yaml
        """
        # Hardcoding the defaults if config isn't populated
        self.auto_takedown_enabled = config.get("takedown", {}).get("auto_takedown_enabled", True)
        self.manual_review_required = config.get("takedown", {}).get("manual_review_required", False)

        self.deepfake_thresh = config.get("detection", {}).get("deepfake_threshold", 0.85)
        self.nudity_thresh = config.get("detection", {}).get("nudity_threshold", 0.70)
        self.confidence_thresh = config.get("detection", {}).get("confidence_threshold", 0.90)

    def evaluate_case(self, case_payload: dict, detection_results: dict) -> dict:
        """
        Determines the appropriate action based on risk thresholds and team policies.
        """
        # Read the raw inputs
        deepfake_score = detection_results.get("deepfake", {}).get("score", 0.0)
        nudity_score = detection_results.get("nudity", {}).get("score", 0.0)
        action_required = detection_results.get("action_required", False)
        match_confidence = case_payload.get("confidence", 0.0)

        decision = {
            "allow_auto_action": False,
            "manual_review_required": False,
            "reason": ""
        }

        # 1. Override flag check
        if self.manual_review_required or case_payload.get("requires_review"):
            decision["manual_review_required"] = True
            decision["reason"] = "Global configuration strictly requires manual review before takedown."
            return decision

        # 2. Insufficient confidence logic
        if match_confidence < self.confidence_thresh:
            decision["manual_review_required"] = True
            decision["reason"] = f"Face match confidence ({match_confidence:.2f}) is below auto-action threshold ({self.confidence_thresh:.2f})."
            return decision
            
        # 3. High Risk Action 
        if action_required and self.auto_takedown_enabled:
            if deepfake_score >= self.deepfake_thresh or nudity_score >= self.nudity_thresh:
                decision["allow_auto_action"] = True
                decision["reason"] = "Confidence and detection scores exceed thresholds for automatic takedowns."
                return decision
            
        # 4. Borderline cases
        decision["manual_review_required"] = True
        decision["reason"] = "Scores in ambiguous borderline ranges. Passing to Member 5 dashboard for review."
        
        return decision
