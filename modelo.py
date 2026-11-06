import os
from datetime import datetime, date
from decimal import Decimal
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

# Instancia de SQLAlchemy
db = SQLAlchemy()


# ============================================================================
# TABLAS ASOCIATIVAS (MUCHOS A MUCHOS)
# ============================================================================

libro_autor = db.Table(
    'libro_autor',
    db.Column('Codigo_Libro', db.String(50), db.ForeignKey('libro.Codigo_Libro', ondelete='CASCADE'), primary_key=True),
    db.Column('ID_Autor', db.Integer, db.ForeignKey('autor.ID_Autor', ondelete='CASCADE'), primary_key=True)
)

libro_categoria = db.Table(
    'libro_categoria',
    db.Column('Codigo_Libro', db.String(50), db.ForeignKey('libro.Codigo_Libro', ondelete='CASCADE'), primary_key=True),
    db.Column('ID_Categoria', db.Integer, db.ForeignKey('categoria.ID_Categoria', ondelete='CASCADE'), primary_key=True)
)


# ============================================================================
# 1. PAIS
# ============================================================================
class Pais(db.Model):
    __tablename__ = 'pais'

    ID_Pais = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Pais = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "ID_Pais": self.ID_Pais,
            "Nombre_Pais": self.Nombre_Pais
        }


# ============================================================================
# 2. IDIOMA
# ============================================================================
class Idioma(db.Model):
    __tablename__ = 'idioma'

    ID_Idioma = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Idioma = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "ID_Idioma": self.ID_Idioma,
            "Nombre_Idioma": self.Nombre_Idioma
        }


# ============================================================================
# 3. EDITORIAL
# ============================================================================
class Editorial(db.Model):
    __tablename__ = 'editorial'

    ID_Editorial = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Editorial = db.Column(db.String(150), nullable=False)

    def to_dict(self):
        return {
            "ID_Editorial": self.ID_Editorial,
            "Nombre_Editorial": self.Nombre_Editorial
        }


# ============================================================================
# 4. ESTADO_FISICO
# ============================================================================
class EstadoFisico(db.Model):
    __tablename__ = 'estado_fisico'

    ID_Estado_Fisico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Estado = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "ID_Estado_Fisico": self.ID_Estado_Fisico,
            "Nombre_Estado": self.Nombre_Estado
        }


# ============================================================================
# 5. FACULTAD
# ============================================================================
class Facultad(db.Model):
    __tablename__ = 'facultad'

    ID_Facultad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Facultad = db.Column(db.String(150), nullable=False)

    def to_dict(self):
        return {
            "ID_Facultad": self.ID_Facultad,
            "Nombre_Facultad": self.Nombre_Facultad
        }


# ============================================================================
# 6. TIPO_USUARIO
# ============================================================================
class TipoUsuario(db.Model):
    __tablename__ = 'tipo_usuario'

    ID_Tipo_Usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Tipo = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "ID_Tipo_Usuario": self.ID_Tipo_Usuario,
            "Nombre_Tipo": self.Nombre_Tipo
        }


# ============================================================================
# 7. TURNO
# ============================================================================
class Turno(db.Model):
    __tablename__ = 'turno'

    ID_Turno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Turno = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "ID_Turno": self.ID_Turno,
            "Nombre_Turno": self.Nombre_Turno
        }


# ============================================================================
# 8. ESTADO_RESERVA
# ============================================================================
class EstadoReserva(db.Model):
    __tablename__ = 'estado_reserva'

    ID_Estado_Reserva = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Estado = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "ID_Estado_Reserva": self.ID_Estado_Reserva,
            "Nombre_Estado": self.Nombre_Estado
        }


# ============================================================================
# 9. ESTADO_PRESTAMO
# ============================================================================
class EstadoPrestamo(db.Model):
    __tablename__ = 'estado_prestamo'

    ID_Estado_Prestamo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Estado = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "ID_Estado_Prestamo": self.ID_Estado_Prestamo,
            "Nombre_Estado": self.Nombre_Estado
        }


# ============================================================================
# 10. CIUDAD
# ============================================================================
class Ciudad(db.Model):
    __tablename__ = 'ciudad'

    ID_Ciudad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Ciudad = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "ID_Ciudad": self.ID_Ciudad,
            "Nombre_Ciudad": self.Nombre_Ciudad
        }


# ============================================================================
# 11. CATEGORIA
# ============================================================================
class Categoria(db.Model):
    __tablename__ = 'categoria'

    ID_Categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Categoria = db.Column(db.String(100), nullable=False)
    Nivel = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "ID_Categoria": self.ID_Categoria,
            "Nombre_Categoria": self.Nombre_Categoria,
            "Nivel": self.Nivel
        }


# ============================================================================
# 12. AUTOR
# ============================================================================
class Autor(db.Model):
    __tablename__ = 'autor'

    ID_Autor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Autor = db.Column(db.String(150), nullable=False)
    Bibliografia = db.Column(db.Text, nullable=True)
    ID_Pais = db.Column(db.Integer, db.ForeignKey('pais.ID_Pais'), nullable=True)

    # Relaciones
    pais = db.relationship('Pais', backref='autores', lazy=True)

    def to_dict(self):
        return {
            "ID_Autor": self.ID_Autor,
            "Nombre_Autor": self.Nombre_Autor,
            "Bibliografia": self.Bibliografia,
            "ID_Pais": self.ID_Pais,
            "Pais": self.pais.Nombre_Pais if self.pais else None
        }


# ============================================================================
# 13. BIBLIOTECARIO
# ============================================================================
class Bibliotecario(db.Model):
    __tablename__ = 'bibliotecario'

    Codigo_Bibliotecario = db.Column(db.String(50), primary_key=True)
    Nombre_Bibliotecario = db.Column(db.String(150), nullable=False)
    Email_Bibliotecario = db.Column(db.String(150), unique=True, nullable=False)
    Password_Hash = db.Column(db.String(255), nullable=False)
    Activo = db.Column(db.Boolean, default=True)
    Fecha_Registro = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    ID_Turno = db.Column(db.Integer, db.ForeignKey('turno.ID_Turno'), nullable=True)

    # Relaciones
    turno = db.relationship('Turno', backref='bibliotecarios', lazy=True)

    def set_password(self, password):
        """Genera el hash seguro de la contrasena"""
        self.Password_Hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contrasena enviada"""
        if not self.Password_Hash:
            return False
        return check_password_hash(self.Password_Hash, password)

    def to_dict(self):
        return {
            "Codigo_Bibliotecario": self.Codigo_Bibliotecario,
            "Nombre_Bibliotecario": self.Nombre_Bibliotecario,
            "Email_Bibliotecario": self.Email_Bibliotecario,
            "Activo": bool(self.Activo) if self.Activo is not None else True,
            "Fecha_Registro": self.Fecha_Registro.isoformat() if self.Fecha_Registro else None,
            "ID_Turno": self.ID_Turno,
            "Turno": self.turno.Nombre_Turno if self.turno else None
        }


# ============================================================================
# 14. LIBRO
# ============================================================================
class Libro(db.Model):
    __tablename__ = 'libro'

    Codigo_Libro = db.Column(db.String(50), primary_key=True)
    Titulo_Libro = db.Column(db.String(255), nullable=False)
    Isbn_Libro = db.Column(db.String(20), unique=True, nullable=True)
    Edicion = db.Column(db.String(50), nullable=True)
    Anio_Publicacion = db.Column(db.Integer, nullable=True)
    Fecha_Ingreso = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    ID_Editorial = db.Column(db.Integer, db.ForeignKey('editorial.ID_Editorial'), nullable=True)
    ID_Idioma = db.Column(db.Integer, db.ForeignKey('idioma.ID_Idioma'), nullable=True)
    ID_Estado_Fisico = db.Column(db.Integer, db.ForeignKey('estado_fisico.ID_Estado_Fisico'), nullable=True)
    Codigo_Bibliotecario = db.Column(db.String(50), db.ForeignKey('bibliotecario.Codigo_Bibliotecario'), nullable=True)

    # Relaciones Muchos a Uno
    editorial = db.relationship('Editorial', backref='libros', lazy=True)
    idioma = db.relationship('Idioma', backref='libros', lazy=True)
    estado_fisico = db.relationship('EstadoFisico', backref='libros', lazy=True)
    bibliotecario = db.relationship('Bibliotecario', backref='libros', lazy=True)

    # Relaciones Muchos a Muchos
    autores = db.relationship('Autor', secondary=libro_autor, backref=db.backref('libros', lazy=True))
    categorias = db.relationship('Categoria', secondary=libro_categoria, backref=db.backref('libros', lazy=True))

    def to_dict(self):
        return {
            "Codigo_Libro": self.Codigo_Libro,
            "Titulo_Libro": self.Titulo_Libro,
            "Isbn_Libro": self.Isbn_Libro,
            "Edicion": self.Edicion,
            "Anio_Publicacion": self.Anio_Publicacion,
            "Fecha_Ingreso": self.Fecha_Ingreso.isoformat() if self.Fecha_Ingreso else None,
            "ID_Editorial": self.ID_Editorial,
            "Editorial": self.editorial.Nombre_Editorial if self.editorial else None,
            "ID_Idioma": self.ID_Idioma,
            "Idioma": self.idioma.Nombre_Idioma if self.idioma else None,
            "ID_Estado_Fisico": self.ID_Estado_Fisico,
            "Estado_Fisico": self.estado_fisico.Nombre_Estado if self.estado_fisico else None,
            "Codigo_Bibliotecario": self.Codigo_Bibliotecario,
            "Bibliotecario": self.bibliotecario.Nombre_Bibliotecario if self.bibliotecario else None,
            "autores": [a.to_dict() for a in self.autores] if self.autores else [],
            "categorias": [c.to_dict() for c in self.categorias] if self.categorias else []
        }


# ============================================================================
# 15. USUARIO
# ============================================================================
class Usuario(db.Model):
    __tablename__ = 'usuario'

    Codigo_Usuario = db.Column(db.String(50), primary_key=True)
    Nombre_Usuario = db.Column(db.String(150), nullable=False)
    Email_Usuario = db.Column(db.String(150), unique=True, nullable=False)
    Password_Hash = db.Column(db.String(255), nullable=False)
    Telefono_Usuario = db.Column(db.String(20), nullable=True)
    Prestamos_Activos = db.Column(db.Integer, default=0, nullable=False)
    Limite_Prestamos = db.Column(db.Integer, default=3, nullable=False)
    Activo = db.Column(db.Boolean, default=True)
    Fecha_Registro = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    ID_Tipo_Usuario = db.Column(db.Integer, db.ForeignKey('tipo_usuario.ID_Tipo_Usuario'), nullable=True)
    ID_Facultad = db.Column(db.Integer, db.ForeignKey('facultad.ID_Facultad'), nullable=True)

    # Relaciones
    tipo = db.relationship('TipoUsuario', backref='usuarios', lazy=True)
    facultad = db.relationship('Facultad', backref='usuarios', lazy=True)

    def set_password(self, password):
        """Genera el hash seguro de la contrasena"""
        self.Password_Hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contrasena enviada coincide con el hash almacenado"""
        if not self.Password_Hash:
            return False
        return check_password_hash(self.Password_Hash, password)

    def to_dict(self):
        """Convierte el objeto Usuario a un diccionario serializable en JSON"""
        return {
            "Codigo_Usuario": self.Codigo_Usuario,
            "Nombre_Usuario": self.Nombre_Usuario,
            "Email_Usuario": self.Email_Usuario,
            "Telefono_Usuario": self.Telefono_Usuario,
            "Prestamos_Activos": self.Prestamos_Activos,
            "Limite_Prestamos": self.Limite_Prestamos,
            "Activo": bool(self.Activo) if self.Activo is not None else True,
            "Fecha_Registro": self.Fecha_Registro.isoformat() if self.Fecha_Registro else None,
            "ID_Tipo_Usuario": self.ID_Tipo_Usuario,
            "Tipo_Usuario": self.tipo.Nombre_Tipo if self.tipo else None,
            "ID_Facultad": self.ID_Facultad,
            "Facultad": self.facultad.Nombre_Facultad if self.facultad else None
        }


# ============================================================================
# 16. DIRECCION
# ============================================================================
class Direccion(db.Model):
    __tablename__ = 'direccion'

    ID_Direccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Codigo_Usuario = db.Column(db.String(50), db.ForeignKey('usuario.Codigo_Usuario', ondelete='CASCADE'), nullable=True)
    Calle_Avenida = db.Column(db.String(150), nullable=True)
    Numero = db.Column(db.String(50), nullable=True)
    Barrio = db.Column(db.String(100), nullable=True)
    ID_Ciudad = db.Column(db.Integer, db.ForeignKey('ciudad.ID_Ciudad'), nullable=True)

    # Relaciones
    usuario = db.relationship('Usuario', backref='direcciones', lazy=True)
    ciudad = db.relationship('Ciudad', backref='direcciones', lazy=True)

    def to_dict(self):
        return {
            "ID_Direccion": self.ID_Direccion,
            "Codigo_Usuario": self.Codigo_Usuario,
            "Usuario": self.usuario.Nombre_Usuario if self.usuario else None,
            "Calle_Avenida": self.Calle_Avenida,
            "Numero": self.Numero,
            "Barrio": self.Barrio,
            "ID_Ciudad": self.ID_Ciudad,
            "Ciudad": self.ciudad.Nombre_Ciudad if self.ciudad else None
        }


# ============================================================================
# 17. HISTORIAL_UBICACION
# ============================================================================
class HistorialUbicacion(db.Model):
    __tablename__ = 'historial_ubicacion'

    ID_Historial = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Codigo_Libro = db.Column(db.String(50), db.ForeignKey('libro.Codigo_Libro', ondelete='CASCADE'), nullable=True)
    Estante_Ubicacion = db.Column(db.String(50), nullable=True)
    Fecha_Asignacion = db.Column(db.Date, nullable=True)

    # Relaciones
    libro = db.relationship('Libro', backref='historial_ubicaciones', lazy=True)

    def to_dict(self):
        return {
            "ID_Historial": self.ID_Historial,
            "Codigo_Libro": self.Codigo_Libro,
            "Libro": self.libro.Titulo_Libro if self.libro else None,
            "Estante_Ubicacion": self.Estante_Ubicacion,
            "Fecha_Asignacion": self.Fecha_Asignacion.isoformat() if self.Fecha_Asignacion else None
        }


# ============================================================================
# 18. RESERVA
# ============================================================================
class Reserva(db.Model):
    __tablename__ = 'reserva'

    Codigo_Reserva = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Codigo_Usuario = db.Column(db.String(50), db.ForeignKey('usuario.Codigo_Usuario'), nullable=True)
    Codigo_Libro = db.Column(db.String(50), db.ForeignKey('libro.Codigo_Libro'), nullable=True)
    Fecha_Reserva = db.Column(db.DateTime, server_default=func.now(), nullable=True)
    Posicion_Cola_Reserva = db.Column(db.Integer, nullable=True)
    ID_Estado_Reserva = db.Column(db.Integer, db.ForeignKey('estado_reserva.ID_Estado_Reserva'), nullable=True)
    Codigo_Bibliotecario = db.Column(db.String(50), db.ForeignKey('bibliotecario.Codigo_Bibliotecario'), nullable=True)

    # Relaciones
    usuario = db.relationship('Usuario', backref='reservas', lazy=True)
    libro = db.relationship('Libro', backref='reservas', lazy=True)
    estado_reserva = db.relationship('EstadoReserva', backref='reservas', lazy=True)
    bibliotecario = db.relationship('Bibliotecario', backref='reservas', lazy=True)

    def to_dict(self):
        return {
            "Codigo_Reserva": self.Codigo_Reserva,
            "Codigo_Usuario": self.Codigo_Usuario,
            "Usuario": self.usuario.Nombre_Usuario if self.usuario else None,
            "Codigo_Libro": self.Codigo_Libro,
            "Libro": self.libro.Titulo_Libro if self.libro else None,
            "Fecha_Reserva": self.Fecha_Reserva.isoformat() if self.Fecha_Reserva else None,
            "Posicion_Cola_Reserva": self.Posicion_Cola_Reserva,
            "ID_Estado_Reserva": self.ID_Estado_Reserva,
            "Estado_Reserva": self.estado_reserva.Nombre_Estado if self.estado_reserva else None,
            "Codigo_Bibliotecario": self.Codigo_Bibliotecario,
            "Bibliotecario": self.bibliotecario.Nombre_Bibliotecario if self.bibliotecario else None
        }


# ============================================================================
# 19. PRESTAMO
# ============================================================================
class Prestamo(db.Model):
    __tablename__ = 'prestamo'

    ID_Prestamo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Codigo_Usuario = db.Column(db.String(50), db.ForeignKey('usuario.Codigo_Usuario'), nullable=True)
    Codigo_Libro = db.Column(db.String(50), db.ForeignKey('libro.Codigo_Libro'), nullable=True)
    Codigo_Bibliotecario = db.Column(db.String(50), db.ForeignKey('bibliotecario.Codigo_Bibliotecario'), nullable=True)
    Fecha_Prestamo = db.Column(db.Date, nullable=False)
    Fecha_Dev_Prevista = db.Column(db.Date, nullable=False)
    Fecha_Dev_Real = db.Column(db.Date, nullable=True)
    Dia_Retraso = db.Column(db.Integer, default=0)
    Multa_Calculada = db.Column(db.Numeric(10, 2), default=0.00)
    Numero_Renovaciones = db.Column(db.Integer, default=0)
    ID_Estado_Prestamo = db.Column(db.Integer, db.ForeignKey('estado_prestamo.ID_Estado_Prestamo'), nullable=True)

    # Relaciones
    usuario = db.relationship('Usuario', backref='prestamos', lazy=True)
    libro = db.relationship('Libro', backref='prestamos', lazy=True)
    bibliotecario = db.relationship('Bibliotecario', backref='prestamos', lazy=True)
    estado_prestamo = db.relationship('EstadoPrestamo', backref='prestamos', lazy=True)

    def to_dict(self):
        return {
            "ID_Prestamo": self.ID_Prestamo,
            "Codigo_Usuario": self.Codigo_Usuario,
            "Usuario": self.usuario.Nombre_Usuario if self.usuario else None,
            "Codigo_Libro": self.Codigo_Libro,
            "Libro": self.libro.Titulo_Libro if self.libro else None,
            "Codigo_Bibliotecario": self.Codigo_Bibliotecario,
            "Bibliotecario": self.bibliotecario.Nombre_Bibliotecario if self.bibliotecario else None,
            "Fecha_Prestamo": self.Fecha_Prestamo.isoformat() if self.Fecha_Prestamo else None,
            "Fecha_Dev_Prevista": self.Fecha_Dev_Prevista.isoformat() if self.Fecha_Dev_Prevista else None,
            "Fecha_Dev_Real": self.Fecha_Dev_Real.isoformat() if self.Fecha_Dev_Real else None,
            "Dia_Retraso": self.Dia_Retraso,
            "Multa_Calculada": float(self.Multa_Calculada) if self.Multa_Calculada is not None else 0.0,
            "Numero_Renovaciones": self.Numero_Renovaciones,
            "ID_Estado_Prestamo": self.ID_Estado_Prestamo,
            "Estado_Prestamo": self.estado_prestamo.Nombre_Estado if self.estado_prestamo else None
        }


# ============================================================================
# FUNCIONES AUXILIARES PARA PARSEO DE FECHAS
# ============================================================================
def parse_date(value):
    """Parsea una fecha desde string o datetime/date"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    val_str = str(value).strip()
    if not val_str:
        return None
    try:
        return datetime.fromisoformat(val_str).date()
    except Exception:
        pass
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(val_str, fmt).date()
        except Exception:
            continue
    raise ValueError(f"Formato de fecha invalido: '{val_str}'. Use 'YYYY-MM-DD'")


def parse_datetime(value):
    """Parsea una fecha y hora desde string o datetime"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    val_str = str(value).strip().replace("Z", "+00:00")
    if not val_str:
        return None
    try:
        return datetime.fromisoformat(val_str)
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(val_str, fmt)
        except Exception:
            continue
    raise ValueError(f"Formato de fecha y hora invalido: '{val_str}'. Use 'YYYY-MM-DD HH:MM:SS'")


if __name__ == "__main__":
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3307/bibliotecaweb"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("Base de datos y tablas verificadas/creadas correctamente.")
