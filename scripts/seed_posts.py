import sys
import os

# Adjust paths to import from modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dummy_social_platform.app import create_app
from dummy_social_platform.models import db, User, Post
import os

def seed_posts():
    app = create_app()
    with app.app_context():
        # Clean existing posts if needed for a clean demo
        Post.query.delete()
        
        # Get users
        victim = User.query.filter_by(username='victim_user').first()
        attacker = User.query.filter_by(username='bad_actor_1').first()
        
        if not victim or not attacker:
            print("Users not found. Run seed_accounts.py first.")
            return
            
        # Create some posts
        posts = [
            {
                'user_id': victim.id, 
                'image_filename': 'real_profile.jpg', 
                'caption': 'Having a great day at the office!'
            },
            {
                'user_id': attacker.id, 
                'image_filename': 'deepfake_scam_01.jpg', 
                'caption': 'Check out this totally real investment advice from our CEO!'
            },
            {
                'user_id': attacker.id, 
                'image_filename': 'malicious_content_02.jpg', 
                'caption': 'Unprocessed leaked footage.'
            }
        ]
        
        for p_data in posts:
            post = Post(
                user_id=p_data['user_id'],
                image_filename=p_data['image_filename'],
                caption=p_data['caption']
            )
            db.session.add(post)
            
        db.session.commit()
        print(f"Successfully seeded {len(posts)} posts for the demo.")

if __name__ == '__main__':
    seed_posts()
