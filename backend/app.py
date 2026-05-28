from flask import Flask, request, jsonify, session
from flask_cors import CORS
from backend.models.db_connect import get_connection
from datetime import datetime


from backend.routes.device_routes import device_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.access_logs_routes import access_logs_bp
from backend.routes.shipments import shipments_bp
from backend.routes.payments import payments_bp
from backend.models.db_init import init_db
from backend.routes.payment_methods import payment_methods_bp
from backend.routes.orders import orders_bp
# from backend.routes.users import users_bp   ||   for when we add routes
# from backend.routes.auth import auth_bp

def create_app():
    init_db()

    app = Flask(__name__)

    # From remote repository main branch
    # app.secret_key = "dev-secret-change-me-before-prod"

    CORS(
        app,
        resources={r"/*": {"origins": "http://127.0.0.1:5500"}},
        supports_credentials=True,
        expose_headers=["Content-Type"]
    )

    # Session config
    app.secret_key = "test-secret-key"
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False


    app.register_blueprint(device_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(access_logs_bp)
    app.register_blueprint(shipments_bp, url_prefix="/shipments")
    app.register_blueprint(payments_bp)
    app.register_blueprint(payment_methods_bp)
    app.register_blueprint(orders_bp)
    # app.register_blueprint(users_bp,url_prefix = "/users")    ||   for when we add routes
    # app.register_blueprint(auth_bp,url_prefix = "/auth")

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    return app

app = create_app()
# moved out of below block due to CORS
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8080)
