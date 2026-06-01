import logging
import os
from flask import Flask
from flask import redirect, request, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from app.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
# Quieter local dev: hide per-request werkzeug access logs
logging.getLogger("werkzeug").setLevel(logging.WARNING)
from app.db import ensure_collections
from app.db import get_student_profile
from app.extensions import init_mongo, login_manager
from app.models import User
from flask_login import current_user

# Load environment variables from .env file
load_dotenv()

def create_app(config_class=Config):
    """Application factory for standard Flask app initialization."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__,
                template_folder=os.path.join(app_dir, 'templates'),
                static_folder=os.path.join(app_dir, 'static'))
    app.config.from_object(config_class)
    
    # Apply ProxyFix to support running behind reverse proxies in production
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    login_manager.init_app(app)
    init_mongo(app)
    ensure_collections()
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for("auth.login", next=request.path))

    @app.context_processor
    def inject_nav_context():
        """
        Shared navbar context (safe for all pages).
        """
        profile = {}
        if getattr(current_user, "is_authenticated", False):
            profile = get_student_profile(current_user.id) or {}

        settings = dict(profile.get("settings") or {})
        settings.setdefault("theme", "system")
        settings.setdefault("mentor_fab", True)

        display_name = (
            (profile.get("name") or "").strip()
            or getattr(current_user, "name", None)
            or "Student"
        )
        avatar_url = (profile.get("profile_image_url") or "").strip() or None

        return {
            "nav_settings": settings,
            "nav_profile": {
                "display_name": display_name,
                "avatar_url": avatar_url,
            },
        }

    # Register routes blueprint (existing resume analyzer)
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Register Vidyastra modules
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.quiz.routes import quiz_bp
    from app.recommendation.routes import recommendation_bp
    from app.chatbot.routes import chatbot_bp
    from app.resume.routes import resume_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(resume_bp)
    
    return app
