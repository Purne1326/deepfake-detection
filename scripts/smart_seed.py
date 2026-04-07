import sys
import os

# Adjust paths to import from modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dummy_social_platform.app import app
from dummy_social_platform.models import db, User, Post
from member4_automation_compliance.audit_logger import AuditLogger, ProtectedPerson

def auto_seed():
    with app.app_context():
        # Check if we already have users
        user_count = User.query.count()
        if user_count > 0:
            print("SMART_SEEDER: Data already exists. Skipping auto-seed.")
            return

        print("SMART_SEEDER: Empty database detected! Populating demo data...")
        
        from scripts.seed_demo_data import seed_real_environment
        seed_real_environment()
        print("SMART_SEEDER: Database successfully populated with initial demo data.")

if __name__ == '__main__':
    auto_seed()
