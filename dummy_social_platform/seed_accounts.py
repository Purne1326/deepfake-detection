from dummy_social_platform.app import create_app
from dummy_social_platform.models import db, User

def seed_users():
    app = create_app()
    with app.app_context():
        # Users based on design scenario
        accounts = [
            {'username': 'ananya_v', 'email': 'ananya@example.com'},
            {'username': 'priya_v', 'email': 'priya@example.com'},
            {'username': 'megha_v', 'email': 'megha@example.com'},
            {'username': 'sara_v', 'email': 'sara@example.com'},
            {'username': 'tanvi_v', 'email': 'tanvi@example.com'},
            {'username': 'actor_unknown', 'email': 'actor@unknown.com'}
        ]
        
        for acc in accounts:
            if not User.query.filter_by(username=acc['username']).first():
                user = User(username=acc['username'], email=acc['email'])
                user.set_password('password123')
                db.session.add(user)
                
        db.session.commit()
        print("Successfully seeded 5 accounts.")

if __name__ == '__main__':
    seed_users()
