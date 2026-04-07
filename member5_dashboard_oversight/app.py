from flask import Flask
from member5_dashboard_oversight.dashboard_routes import bp as dashboard_bp
import threading
import time

app = Flask(__name__)
app.secret_key = 'super-secret-key' # Required for flask-login or sessions if used
app.register_blueprint(dashboard_bp)

# Create a mock login user for development purposes
class MockUser:
    def __init__(self, id):
        self.id = id
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        
    def get_id(self):
        return str(self.id)

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return MockUser(user_id)

# Force a test user login before every request
@app.before_request
def mock_login():
    from flask_login import login_user
    login_user(MockUser('admin'))

def start_orchestrator():
    """Runs the orchestrator in a background thread for free deployment."""
    from scripts.orchestrator import run_pipeline
    time.sleep(10) # Give time for web servers to start
    try:
        run_pipeline()
    except Exception as e:
        print(f"Background Orchestrator Error: {e}")

# Start orchestrator thread
threading.Thread(target=start_orchestrator, daemon=True).start()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
