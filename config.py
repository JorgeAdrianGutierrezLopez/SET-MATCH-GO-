import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SECRET = "dev-insecure-change-me"

def _database_url():
    # Lee primero Turso y mantiene compatibilidad con otras bases de datos
    url = os.getenv("TURSO_DATABASE_URL") or os.getenv("DATABASE_URL")
    
    if url:
        if url.startswith("postgres://"):  # Render entrega este formato
            url = url.replace("postgres://", "postgresql://", 1)
        
        # Si es una URL de Turso, extraemos el host limpio
        if "turso.io" in url or "libsql" in url:
            if "://" in url:
                host_part = url.split("://", 1)[1]
            else:
                host_part = url
            
            # Limpiamos cualquier parámetro o credencial previa en la URL
            host_part = host_part.split("@")[-1].split("?")[0]
            
            # Obtenemos el token de autenticación de las variables de entorno
            token = os.getenv("TURSO_AUTH_TOKEN") or os.getenv("LIBSQL_AUTH_TOKEN")
            
            # Construimos la URL con el formato token@host que exige sqlalchemy-libsql
            if token:
                url = f"sqlite+libsql://{token}@{host_part}"
            else:
                url = f"sqlite+libsql://{host_part}"

    return url or "sqlite:///setmatchgo.db"


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET)
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    AUTO_CREATE_DB = False

    # CONFIGURACIÓN SMTP (FLASK-MAIL)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    AUTO_CREATE_DB = True


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False
    AUTO_CREATE_DB = True


class ProductionConfig(BaseConfig):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    AUTO_CREATE_DB = True  # Activado para que cree las tablas automáticamente en el arranque


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
