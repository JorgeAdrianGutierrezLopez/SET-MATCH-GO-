from datetime import datetime, timezone
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from bson.objectid import ObjectId


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin):
    """Modelo de Usuario para MongoDB."""

    def __init__(self, user_data=None):
        self.user_data = user_data or {}
        self._id = self.user_data.get("_id")
        self.id = str(self._id) if self._id else None
        
        self.nombre = self.user_data.get("nombre")
        self.email = self.user_data.get("email")
        self.password_hash = self.user_data.get("password_hash")
        self.created_at = self.user_data.get("created_at", utcnow())

        # Estado de verificación por correo
        self.is_confirmed = self.user_data.get("is_confirmed", False)

        # Campos opcionales de perfil / preferencias cromáticas
        self.color_ojos = self.user_data.get("color_ojos")
        self.color_cabello = self.user_data.get("color_cabello")
        self.biografia = self.user_data.get("biografia")

    def get_id(self):
        return str(self.id) if self.id else None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def save(self):
        """Guarda o actualiza el usuario en la colección 'users'."""
        users_collection = current_app.db.users
        data = {
            "nombre": self.nombre,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "is_confirmed": self.is_confirmed,
            "color_ojos": self.color_ojos,
            "color_cabello": self.color_cabello,
            "biografia": self.biografia,
        }
        if self._id:
            users_collection.update_one({"_id": self._id}, {"$set": data})
        else:
            result = users_collection.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)

    @staticmethod
    def get_by_id(user_id):
        """Busca un usuario por su ID (ObjectId o string)."""
        try:
            data = current_app.db.users.find_one({"_id": ObjectId(user_id)})
            return User(data) if data else None
        except Exception:
            data = current_app.db.users.find_one({"_id": user_id})
            return User(data) if data else None

    @staticmethod
    def get_by_email(email):
        """Busca un usuario por su correo electrónico."""
        data = current_app.db.users.find_one({"email": email})
        return User(data) if data else None

    @property
    def resultados(self):
        """Equivalente al relationship de TestResult."""
        return list(
            current_app.db.test_results.find({"user_id": str(self.id)}).sort("created_at", -1)
        )

    @property
    def prendas(self):
        """Equivalente al relationship de Guardarropa."""
        return list(
            current_app.db.guardarropa.find({"usuario_id": str(self.id)}).sort("fecha_creacion", -1)
        )


class TestResult:
    """Gestor para los resultados de los tests guardados en MongoDB."""
    
    __test__ = False  # Evita que pytest lo tome como prueba

    @staticmethod
    def create(user_id, respuestas, subtono, estacion):
        data = {
            "user_id": str(user_id),
            "respuestas": respuestas,
            "subtono": subtono,  # calido | frio | neutro
            "estacion": estacion,
            "created_at": utcnow(),
        }
        result = current_app.db.test_results.insert_one(data)
        return result.inserted_id


class Guardarropa:
    """Gestor para los elementos del guardarropa en MongoDB."""

    @staticmethod
    def create(usuario_id, nombre, categoria, imagen):
        data = {
            "usuario_id": str(usuario_id),
            "nombre": nombre,
            "categoria": categoria,
            "imagen": imagen,
            "fecha_creacion": utcnow(),
        }
        result = current_app.db.guardarropa.insert_one(data)
        return result.inserted_id
