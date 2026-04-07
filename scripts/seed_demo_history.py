import sys
import os
import random
from datetime import datetime, timedelta
import uuid
import json

# Adjust paths to import from modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from member4_automation_compliance.audit_logger import AuditLogger, AuditLog, ProtectedPerson

def seed_history():
    # Clear existing audit data
    audit_db_path = "audit.db"
    if os.path.exists(audit_db_path):
        os.remove(audit_db_path)
        print("SEEDER: Existing audit database wiped for clean historical seeding.")

    print("SEEDER: Generating historical data for a realistic dashboard experience...")
    
    auditor = AuditLogger()
    session = auditor.session
    
    # Define some platforms and victims
    platforms = ["Twitter (X)", "Facebook", "Instagram", "WhatsApp", "LinkedIn", "TikTok"]
    victims = [
        {"name": "Ananya V", "handle": "ananya_v"},
        {"name": "Priya V", "handle": "priya_v"}
    ]
    
    # 1. Create historical detections over the last 15 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=14)
    
    for i in range(15):
        day = start_date + timedelta(days=i)
        
        # Number of detections per day (2-7 range to look active but not crazy)
        num_detections = random.randint(2, 7)
        
        for _ in range(num_detections):
            victim = random.choice(victims)
            platform = random.choice(platforms)
            
            # Randomize time within the day
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            timestamp = day.replace(hour=hour, minute=minute)
            
            risk_score = round(random.uniform(0.3, 0.95), 2)
            
            # Determine status: most are COMPLETED or SUCCESS, some are PENDING_REVIEW
            status = "COMPLETED"
            if risk_score > 0.8:
                status = random.choice(["PENDING_REVIEW", "SUCCESS", "COMPLETED"])
            
            # Create the AuditLog entry
            log = AuditLog(
                id=str(uuid.uuid4()).replace('-', '')[:16],
                action_type="DETECTION_RECEIVED",
                platform=platform,
                post_id=f"p_{random.randint(1000, 9999)}",
                url=f"https://{platform.lower().split(' ')[0]}.com/post/{random.randint(100000, 999999)}",
                timestamp=timestamp,
                reason=f"Deepfake detection triggered for {victim['name']} ({victim['handle']})",
                status=status,
                details={
                    "victim_user_id": victim['handle'],
                    "risk_score": risk_score,
                    "platform_origin": platform,
                    "confidence": round(random.uniform(0.85, 0.99), 3),
                    "action_required": "REVIEW" if status == "PENDING_REVIEW" else "NONE",
                    "source": "Forensic Pipeline"
                }
            )
            session.add(log)
            
            # 2. Add some associated TAKEDOWNS for some successful detections
            if status == "SUCCESS" or (status == "COMPLETED" and risk_score > 0.7 and random.random() > 0.5):
                takedown_time = timestamp + timedelta(minutes=random.randint(10, 120))
                tk_log = AuditLog(
                    id=str(uuid.uuid4()).replace('-', '')[:16],
                    action_type="TAKEDOWN_REQUESTED",
                    platform=platform,
                    post_id=log.post_id,
                    url=log.url,
                    timestamp=takedown_time,
                    reason=f"Automated takedown request sent to {platform} API",
                    status="SUCCESS",
                    details={
                        "request_id": f"TK-{random.randint(1000, 9999)}",
                        "response_time_ms": random.randint(150, 450),
                        "platform_confirmation": "URL_REMOVED",
                        "source": "Complianc Manager"
                    }
                )
                session.add(tk_log)

    session.commit()
    print("SUCCESS: Historical data populated. Restart the dashboard to see the magic.")

if __name__ == '__main__':
    seed_history()
