from flask import Flask, jsonify
from config import SECRET_KEY
from controllers.auth import auth_bp
from controllers.admin import admin_bp
from controllers.student import student_bp
from controllers.live_location import live_bp
from controllers.notices import notices_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(live_bp)
    app.register_blueprint(notices_bp)

    @app.route('/')
    def home():
        return "Bus Tracking API is running!", 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
