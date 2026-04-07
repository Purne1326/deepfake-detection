import os
from flask import Flask
from dummy_social_platform.config import Config
from dummy_social_platform.models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Needs a context to configure DB
    with app.app_context():
        db.create_all()

    # Import routes
    from dummy_social_platform.routes.api_routes import bp as api_bp
    from dummy_social_platform.routes.auth_routes import bp as auth_bp
    from dummy_social_platform.routes.post_routes import bp as post_bp
    from dummy_social_platform.routes.feed_routes import bp as feed_bp
    from dummy_social_platform.routes.protection_routes import bp as protection_bp
    
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(protection_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5001, debug=True)
