import sys
import os

# Adjust paths to import from modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dummy_social_platform.app import app
from dummy_social_platform.models import db, User, Post
from datetime import datetime, timedelta
import uuid
from member4_automation_compliance.audit_logger import AuditLogger, AuditLog, ProtectedPerson

def seed_real_environment():
    """
    Seeds only the necessary environment for testing.
    NO historical audit logs are created.
    """
    with app.app_context():
        print("SEEDER: Clearing all databases for a REAL integrated run...")
        db.drop_all()
        db.create_all()
        # Clear Audit Log purely
        audit_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audit.db")
        if os.path.exists(audit_db_path):
            os.remove(audit_db_path)
            print("SEEDER: Audit database wiped clean.")

        print("SEEDER: Setting up social media environment...")
        # Create users for the dummy platform so scrapers have something to find
        users_to_seed = [
            {'username': 'ananya_v', 'email': 'ananya@example.com'},
            {'username': 'priya_v', 'email': 'priya@example.com'},
            {'username': 'bad_actor_99', 'email': 'badactor@example.com'}
        ]

        created_users = {}
        for u_data in users_to_seed:
            user = User(username=u_data['username'], email=u_data['email'])
            user.set_password('password123')
            db.session.add(user)
            created_users[u_data['username']] = user
        
        db.session.commit()

        # Seed some initial posts to be scanned
        posts_to_seed = [
            {'author': 'bad_actor_99', 'caption': 'Deepfake test of Ananya!', 'image': 'demo_1.jpg'},
            {'author': 'ananya_v', 'caption': 'Official post. Verified human.', 'image': 'demo_4.jpg'}
        ]

        for p_data in posts_to_seed:
            author = created_users.get(p_data['author'])
            post = Post(
                user_id=author.id,
                caption=p_data['caption'],
                image_filename=p_data['image'],
                created_at=datetime.utcnow()
            )
            db.session.add(post)
        
        db.session.commit()
        
        # --- SEED PROTECTED PERSONS (THE RECIPIENTS OF THE PROTECTION) ---
        print("SEEDER: Enrolling protected identities for active defense...")
        auditor = AuditLogger()
        session = auditor.session
        
        protected_to_seed = [
            {"name": "Ananya V", "handle": "ananya_v", "risk": "HIGH"},
            {"name": "Priya V", "handle": "priya_v", "risk": "ELEVATED"}
        ]
        
        for p in protected_to_seed:
            person = ProtectedPerson(
                id=str(uuid.uuid4()),
                name=p["name"],
                handle=p["handle"],
                risk_level=p["risk"]
            )
            session.add(person)
        
        session.commit()
        print("SEEDER: ENVIRONMENT READY. DASHBOARD IS CLEAN.")

if __name__ == '__main__':
    seed_real_environment()
