import sys
import os

# Adjust paths to import from modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dummy_social_platform.app import app
from dummy_social_platform.models import db, User, Post
from member4_automation_compliance.audit_logger import AuditLogger, AuditLog, ProtectedPerson
import uuid

def fast_seed():
    with app.app_context():
        # 1. Ensure tables exist (fast)
        db.create_all()

        # 2. Add users if missing
        if User.query.count() == 0:
            print("FAST_SEED: Adding demo users...")
            u = User(username='ananya_v', email='ananya@example.com')
            u.set_password('password123')
            db.session.add(u)
            
            u2 = User(username='bad_actor_99', email='bad@example.com')
            u2.set_password('password123')
            db.session.add(u2)
            db.session.commit()

        # 3. Add protected identities to audit log if missing
        auditor = AuditLogger()
        session = auditor.session
        try:
            if session.query(ProtectedPerson).count() == 0:
                print("FAST_SEED: Adding protected identities...")
                p = ProtectedPerson(id=str(uuid.uuid4()), name="Ananya V", handle="ananya_v", risk_level="HIGH")
                session.add(p)
                session.commit()
        except:
            session.rollback()
        
        print("FAST_SEED: Cloud environment ready.")

if __name__ == '__main__':
    fast_seed()
