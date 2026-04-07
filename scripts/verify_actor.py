from dummy_social_platform.app import create_app
from dummy_social_platform.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='actor_unknown').first()
    if user:
        print(f"Testing login for {user.username}...")
        is_correct = user.check_password('password123')
        print(f"Password 'password123' is correct: {is_correct}")
    else:
        print("User not found.")
