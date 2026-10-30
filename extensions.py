from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail

# Inicializar las extensiones sin SQLAlchemy
csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()
