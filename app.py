import os
from flask import Flask
import config
import db as database


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG

    # VULN: CWE-614 (Sensitive Cookie Without Secure Flag), OWASP A05
    # Session cookies lack Secure and HttpOnly flags.
    app.config["SESSION_COOKIE_HTTPONLY"] = False
    app.config["SESSION_COOKIE_SECURE"] = False

    # Initialize DB if it doesn't exist
    if not os.path.exists(config.DATABASE):
        database.init_db()

    # Register blueprints
    from blueprints import blog, auth, admin, nettools, profile, search, debug, upload, weather

    app.register_blueprint(blog.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(nettools.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(debug.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(weather.bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
