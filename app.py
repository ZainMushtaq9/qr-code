"""QR Code Studio — Flask Application Factory"""
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # --- Configuration ---
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SITE_NAME"] = os.getenv("SITE_NAME", "QR Code Studio")
    app.config["SITE_DOMAIN"] = os.getenv("SITE_DOMAIN", "http://localhost:5000")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB upload limit

    # AdSense
    app.config["ADSENSE_ID"] = os.getenv("ADSENSE_ID", "")
    app.config["ADSENSE_SLOT_BANNER"] = os.getenv("ADSENSE_SLOT_BANNER", "")
    app.config["ADSENSE_SLOT_SIDEBAR"] = os.getenv("ADSENSE_SLOT_SIDEBAR", "")
    app.config["ADSENSE_SLOT_ARTICLE"] = os.getenv("ADSENSE_SLOT_ARTICLE", "")

    # Groq
    app.config["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

    # Uploads folder
    upload_folder = os.path.join(app.static_folder, "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = upload_folder

    # --- Context processor: inject config into all templates ---
    @app.context_processor
    def inject_globals():
        return {
            "site_name": app.config["SITE_NAME"],
            "site_domain": app.config["SITE_DOMAIN"],
            "adsense_id": app.config["ADSENSE_ID"],
            "adsense_slot_banner": app.config["ADSENSE_SLOT_BANNER"],
            "adsense_slot_sidebar": app.config["ADSENSE_SLOT_SIDEBAR"],
            "adsense_slot_article": app.config["ADSENSE_SLOT_ARTICLE"],
        }

    # --- Register Blueprints ---
    from routes.main import main_bp
    from routes.qr import qr_bp
    from routes.seo import seo_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(seo_bp)

    return app
