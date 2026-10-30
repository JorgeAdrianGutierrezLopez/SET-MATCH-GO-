import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env si existe localmente
load_dotenv()

class Config:
    """Configuración base de la aplicación Flask para MongoDB."""
    
    # Clave secreta para manejo de sesiones y formularios Flask-WTF
    SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_por_defecto_aqui")
    
    # Obtener la URI de conexión a MongoDB
    # Soporta tanto MONGO_URI como DATABASE_URL para flexibilidad en Render
    MONGO_URI = os.getenv("MONGO_URI") or os.getenv("DATABASE_URL")
    
    if MONGO_URI:
        MONGO_URI = MONGO_URI.strip()
    else:
        # Fallback local en caso de que no esté configurada la variable en desarrollo
        MONGO_URI = "mongodb://localhost:27017/setmatchgo_db"
        
    # Nombre de la base de datos dentro de MongoDB
    MONGO_DBNAME = os.getenv("MONGO_DBNAME", "setmatchgo_db")

    # Configuración opcional para Flask-Mail u otros servicios
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)) if os.getenv("MAIL_PORT") else 587
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ["true", "1", "yes"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


class DevelopmentConfig(Config):
    """Configuración para desarrollo local."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción (Render)."""
    DEBUG = False


# Diccionario para seleccionar el entorno dinámicamente según APP_ENV
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": ProductionConfig
}


def get_config():
    """Retorna la clase de configuración según la variable APP_ENV."""
    env = os.getenv("APP_ENV", "production").lower()
    return config_by_name.get(env, config_by_name["default"])
