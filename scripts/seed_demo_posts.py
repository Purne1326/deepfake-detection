from dummy_social_platform.app import create_app
from dummy_social_platform.models import db, Post, User
from datetime import datetime

def seed_posts():
    app = create_app()
    with app.app_context():
        users = {u.username: u for u in User.query.all()}
        
        demo_posts = [
            {'username': 'ananya_v', 'caption': 'Enjoying the sunset! #Peace'},
            {'username': 'priya_v', 'caption': 'New profile picture!'},
            {'username': 'megha_v', 'caption': 'Working on my new project.'},
            {'username': 'sara_v', 'caption': 'Morning coffee is the best.'},
            {'username': 'tanvi_v', 'caption': 'Check out this view!'}
        ]
        
        for p_data in demo_posts:
            user = users.get(p_data['username'])
            if user:
                # Check if already has posts to avoid duplicates
                if Post.query.filter_by(user_id=user.id, caption=p_data['caption']).first():
                    continue
                    
                post = Post(
                    caption=p_data['caption'],
                    image_filename=None, # We'll use UI Avatars in template for missing images
                    author=user
                )
                db.session.add(post)
        
        db.session.commit()
        print("Successfully seeded demo posts for protected users.")

if __name__ == '__main__':
    seed_posts()
