from .compliance_checker import ComplianceChecker
from .reporting_engine import ReportingEngine
from .audit_logger import AuditLogger
from .platform_handlers.dummy_takedown import DummyTakedownHandler
import traceback

class TakedownManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.compliance = ComplianceChecker(self.config)
        self.reporting = ReportingEngine()
        self.auditor = AuditLogger()
        self.handlers = {
            "dummy": DummyTakedownHandler()
        }

    def process_case(self, case_payload: dict, detection_results: dict) -> dict:
        """
        Unified handler that runs the case end to end for Member 4.
        """
        try:
            # 1. Run compliance checks over the payload
            decision = self.compliance.evaluate_case(case_payload, detection_results)
            
            # 2. Build standardized evidence packet
            packet = self.reporting.generate_evidence_packet(case_payload, detection_results, decision)
            
            # 3. Log case initialized
            self.auditor.log_detection_case(packet)
            self.auditor.log_report_prepared(packet)
            
            # 4. Routing Action
            platform = case_payload.get("platform", "").lower()
            handler = self.handlers.get(platform)
            
            if not handler:
                 response = {
                     "status": "ERROR",
                     "reason": f"No handler registered for platform '{platform}'",
                     "packet": packet
                 }
                 self.auditor.log_error(platform, case_payload.get("post_id"), response["reason"])
                 return response
                 
            # 5. Handle action
            if decision.get("manual_review_required"):
                response = {
                    "status": "PENDING_REVIEW",
                    "reason": decision.get("reason"),
                    "packet": packet
                }
                print(f"Manager: Halting takedown for {platform}. Placed in manual review queue.")
            elif decision.get("allow_auto_action"):
                # Real API takedown request
                print(f"Manager: Firing official Takedown call to {platform} via API handler.")
                handler_response = handler.report_post(
                    post_id=case_payload.get("post_id"),
                    url=case_payload.get("url"),
                    reason=decision.get("reason"),
                    evidence=packet
                )
                
                response = {
                    "status": handler_response.get("status"),
                    "reason": handler_response.get("message"),
                    "packet": packet
                }
                
                self.auditor.log_takedown_requested(packet, response)
                
            return response
            
        except Exception as e:
            err = traceback.format_exc()
            print(f"CRITICAL ERROR IN M4 PROCESSING: {err}")
            self.auditor.log_error(case_payload.get("platform"), case_payload.get("post_id"), str(err))
            return {
                "status": "ERROR", 
                "reason": "Internal Orchestration Exception"
            }

    def approve_manual_case(self, log_id: str) -> dict:
        """
        Manually approves a case that was stuck in PENDING_REVIEW.
        """
        try:
            # 1. Fetch log from auditor
            log = self.auditor.session.query(self.auditor.AuditLog).filter_by(id=log_id).first()
            if not log:
                return {"status": "ERROR", "message": "Log entry not found"}
            
            if log.status != "PENDING_REVIEW":
                return {"status": "ERROR", "message": f"Case is not in PENDING_REVIEW status (Current: {log.status})"}

            platform = log.platform.lower()
            handler = self.handlers.get(platform)
            
            if not handler:
                return {"status": "ERROR", "message": f"No handler registered for platform '{platform}'"}

            # 2. Execute Takedown
            print(f"Manager: MANUAL APPROVAL received. Firing takedown for {platform}:{log.post_id}.")
            packet = log.details # Reuse stored packet
            
            handler_response = handler.report_post(
                post_id=log.post_id,
                url=log.url,
                reason=f"Manually Approved: {log.reason}",
                evidence=packet
            )
            
            # 3. Update Log Entry
            log.status = handler_response.get("status")
            log.action_type = "TAKEDOWN_REQUESTED"
            log.details = {**log.details, "manual_approval": True, "handler_response": handler_response}
            self.auditor.session.commit()
            
            return {
                "status": log.status,
                "message": handler_response.get("message"),
                "log_id": log_id
            }
            
        except Exception as e:
            err = traceback.format_exc()
            print(f"ERROR IN MANUAL APPROVAL: {err}")
            return {"status": "ERROR", "message": str(e)}
