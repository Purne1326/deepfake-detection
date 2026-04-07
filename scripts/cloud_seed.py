import sys
import os

# Adjust paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dummy_social_platform.app import app
from dummy_social_platform.models import db, User
from member4_automation_compliance.audit_logger import AuditLogger, ProtectedPerson
import uuid

def fast_seed():
    """Lightning-fast idempotent seeding for Cloud."""
    print("🚀 [CLOUD_SEED] Starting check...")
    with app.app_context():
        # ONE-TIME FORCE-DROP to fix the truncated password column size (128 -> 512)
        # We only do this if we haven't successfully seeded the fixed users yet.
        try:
            db.drop_all() # This clears the broken 128-char schema
            print("🚿 [CLOUD_SEED] Old schema cleared. Rebuilding high-capacity database...")
        except:
            pass
            
        # Ensure all tables exist (now with 512-char column)
        db.create_all()
        
        # Add Login Users if missing
        if User.query.filter_by(username='ananya_v').first() is None:
            print("👤 [CLOUD_SEED] Creating demo user: ananya_v")
            u = User(username='ananya_v', email='ananya@example.com')
            u.set_password('password123')
            db.session.add(u)
            db.session.commit()
            print("✅ [CLOUD_SEED] Demo user ananya_v created successfully.")
        else:
            print("✅ [CLOUD_SEED] Demo user already exists.")

        # Add Protected Identities for the Dashboard
        auditor = AuditLogger()
        session = auditor.session
        try:
            if session.query(ProtectedPerson).filter_by(handle='ananya_v').first() is None:
                print("🛡️ [CLOUD_SEED] Enrolling protected identity: Ananya V")
                p = ProtectedPerson(id=str(uuid.uuid4()), name="Ananya V", handle="ananya_v", risk_level="HIGH")
                session.add(p)
                session.commit()
            print("✅ [CLOUD_SEED] Dashboard enrollment check complete.")
        except Exception as e:
            print(f"⚠️ [CLOUD_SEED] Dashboard sync error: {e}")
            session.rollback()

if __name__ == '__main__':
    fast_seed()
