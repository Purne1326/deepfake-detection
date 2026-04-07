from dummy_social_platform.app import create_app
from dummy_social_platform.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"Total Users: {len(users)}")
    for u in users:
        print(f"User: {u.username}, Password Set: {u.password_hash is not None}")
