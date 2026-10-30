import os
import click
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError
from bson.objectid import ObjectId
from pymongo import MongoClient

from config import DEFAULT_SECRET, config_by_name
from extensions import csrf, login_manager, mail  # Se elimina 'db' de SQLAlchemy


def create_app(config_name=None):
    config_name = config_name or os.getenv("APP_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Configuración de carpeta para imágenes del guardarropa
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads', 'guardarropa')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite máximo de 16MB por archivo

    if config_name == "production" and app.config.get("SECRET_KEY") == DEFAULT_SECRET:
        raise RuntimeError("Define la variable de entorno SECRET_KEY en producción.")

    # Inicialización del cliente de MongoDB y asignación a app.db
    mongo_uri = app.config.get("MONGO_URI")
    mongo_client = MongoClient(mongo_uri)
    db_name = app.config.get("MONGO_DBNAME", "setmatchgo_db")
    app.db = mongo_client[db_name]

    # Inicialización de extensiones (sin SQLAlchemy)
    csrf.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    login_manager.login_view = "login"
    login_manager.login_message = "Inicia sesión para acceder a esa página."
    login_manager.login_message_category = "warning"

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            # Buscar al usuario en la colección 'users' de MongoDB usando ObjectId
            user_data = app.db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except (TypeError, ValueError, Exception):
            # Fallback por si el ID se guarda como texto plano
            user_data = app.db.users.find_one({"_id": user_id})
            if user_data:
                return User(user_data)
        return None

    @app.errorhandler(CSRFError)
    def csrf_error(e):
        flash("Tu sesión del formulario expiró o el token no es válido. Inténtalo de nuevo.", "error")
        return redirect(request.referrer or url_for("index"))

    # Registro de rutas de la aplicación
    from routes import register_routes
    register_routes(app)

    @app.cli.command("init-db")
    def init_db():
        """MongoDB no requiere inicialización manual de tablas (es schemaless)."""
        click.echo("MongoDB está listo. No es necesario crear tablas manualmente.")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1")
