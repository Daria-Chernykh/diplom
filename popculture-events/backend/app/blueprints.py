from flask import Blueprint, jsonify

from app.auth.routes import auth_bp
from app.complaints.routes import complaints_bp
from app.events.routes import events_bp
from app.favorites.routes import favorites_bp
from app.files.routes import files_bp
from app.legal.routes import legal_bp
from app.notifications.routes import notifications_bp
from app.organizers.routes import organizers_bp
from app.registrations.routes import registrations_bp
from app.reviews.routes import reviews_bp
from app.users.routes import users_bp


api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health():
    return jsonify(
        {
            "success": True,
            "message": "Backend PopCulture Events работает.",
        }
    )


def register_blueprints(app):
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(legal_bp, url_prefix="/api/legal")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(organizers_bp, url_prefix="/api/organizers")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(favorites_bp, url_prefix="/api/favorites")
    app.register_blueprint(registrations_bp, url_prefix="/api/registrations")
    app.register_blueprint(complaints_bp, url_prefix="/api/complaints")
    app.register_blueprint(reviews_bp, url_prefix="/api/reviews")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(files_bp, url_prefix="/api/files")