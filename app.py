import os
from datetime import timedelta
from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
)
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from modelo import db, Usuario, TipoUsuario, Facultad, Bibliotecario, Turno
from crud_routes import crud_bp
from cache_manager import cache
from auth_utils import solo_bibliotecario
from seed_data import seed_database

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configuracion de Base de Datos y Seguridad
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:@localhost:3307/bibliotecaweb"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY", "biblioteca_jwt_secret_key_2026_super_segura"
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

# Inicializar extensiones
db.init_app(app)
jwt = JWTManager(app)

# ============================================================================
# CONFIGURACIÓN SEGURA DE CORS (Cross-Origin Resource Sharing)
# ============================================================================
# 1. Cargar lista blanca de orígenes desde .env o usar valores locales seguros
allowed_origins_env = os.getenv("CORS_ALLOWED_ORIGINS")

if allowed_origins_env:
    allowed_origins = [
        origin.strip() 
        for origin in allowed_origins_env.split(",") 
        if origin.strip()
    ]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite
        "http://127.0.0.1:5173",
        "http://localhost:5500",  # Live Server
        "http://127.0.0.1:5500",
        "http://localhost:5000",  # Swagger y Flask
        "http://127.0.0.1:5000"
    ]

# 2. Aplicar restricciones únicamente sobre las rutas /api/*
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 86400  # 24 horas de caché para preflight OPTIONS
        }
    }
)

# Registrar Blueprint con todos los 19 endpoints CRUD solicitados
app.register_blueprint(crud_bp)

# Intentar crear tablas y poblar datos base si estan vacias
with app.app_context():
    try:
        db.create_all()
        seed_database(app)
    except Exception as e:
        print(f"Advertencia al conectar/crear tablas: {e}")

# Manejadores de error personalizados para JWT
@jwt.unauthorized_loader
def token_faltante_callback(reason):
    return jsonify({
        "error": "Acceso no autorizado",
        "mensaje": "Se requiere un token JWT en el encabezado Authorization (Bearer <token>)"
    }), 401

@jwt.expired_token_loader
def token_expirado_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": "Token expirado",
        "mensaje": "El token ha caducado. Inicie sesion nuevamente"
    }), 401

@jwt.invalid_token_loader
def token_invalido_callback(reason):
    return jsonify({
        "error": "Token invalido",
        "mensaje": "El formato o la firma del token no son validos"
    }), 401


# Cabeceras de seguridad HTTP (defensa en profundidad)
@app.after_request
def agregar_cabeceras_seguridad(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# ==============================================================
# ==============================================================
# ENDPOINTS DE AUTENTICACION Y REGISTRO (ESTUDIANTES, DOCENTES Y BIBLIOTECARIOS)
# ==============================================================

@app.route("/api/auth/opciones-registro", methods=["GET"])
def opciones_registro():
    """Retorna las opciones disponibles de tipos de usuario (Estudiante, Docente, etc.), facultades y turnos"""
    tipos = [
        {
            "id": t.ID_Tipo_Usuario,
            "nombre": t.Nombre_Tipo,
            "ID_Tipo_Usuario": t.ID_Tipo_Usuario,
            "Nombre_Tipo": t.Nombre_Tipo,
            "max_libros": 5 if "docente" in t.Nombre_Tipo.lower() else 3
        }
        for t in TipoUsuario.query.all()
    ]
    facultades = [
        {
            "id": f.ID_Facultad,
            "nombre": f.Nombre_Facultad,
            "ID_Facultad": f.ID_Facultad,
            "Nombre_Facultad": f.Nombre_Facultad
        }
        for f in Facultad.query.all()
    ]
    turnos = [
        {
            "id": t.ID_Turno,
            "nombre": t.Nombre_Turno,
            "ID_Turno": t.ID_Turno,
            "Nombre_Turno": t.Nombre_Turno
        }
        for t in Turno.query.all()
    ]
    return jsonify({
        "tipos_usuario": tipos,
        "facultades": facultades,
        "turnos": turnos
    }), 200


@app.route("/api/auth/registro", methods=["POST"])
def registrar_usuario():
    """
    Registra un nuevo estudiante o docente con contrasena encriptada y rol 'usuario'.
    Soporta seleccion por ID o por nombre de Tipo_Usuario ('Estudiante', 'Docente').
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Debe enviar los datos en formato JSON"}), 400

    codigo = datos.get("Codigo_Usuario")
    nombre = datos.get("Nombre_Usuario")
    email = datos.get("Email_Usuario")
    password = datos.get("Password")
    telefono = datos.get("Telefono_Usuario")
    id_tipo = datos.get("ID_Tipo_Usuario")
    tipo_str = datos.get("Tipo_Usuario") or datos.get("rol_solicitado")
    id_facultad = datos.get("ID_Facultad")
    facultad_str = datos.get("Facultad")

    # Validaciones obligatorias
    if not codigo or not nombre or not email or not password:
        return jsonify({
            "error": "Faltan campos obligatorios",
            "detalle": "Codigo_Usuario, Nombre_Usuario, Email_Usuario y Password son requeridos"
        }), 400

    if len(str(password)) < 6:
        return jsonify({"error": "La contrasena debe tener al menos 6 caracteres"}), 400

    codigo_clean = str(codigo).strip()
    email_clean = str(email).strip()

    # Comprobar duplicados
    if Usuario.query.filter_by(Codigo_Usuario=codigo_clean).first():
        return jsonify({"error": f"Ya existe un usuario con el codigo '{codigo_clean}'"}), 400

    if Usuario.query.filter_by(Email_Usuario=email_clean).first():
        return jsonify({"error": f"Ya existe un usuario con el correo '{email_clean}'"}), 400

    # 1. Resolver Tipo de Usuario (Estudiante, Docente, etc.)
    if not id_tipo and tipo_str:
        t = TipoUsuario.query.filter(TipoUsuario.Nombre_Tipo.ilike(str(tipo_str).strip())).first()
        if t:
            id_tipo = t.ID_Tipo_Usuario

    if not id_tipo:
        est_tipo = TipoUsuario.query.filter(TipoUsuario.Nombre_Tipo.ilike("Estudiante")).first() or TipoUsuario.query.first()
        id_tipo = est_tipo.ID_Tipo_Usuario if est_tipo else 1

    # 2. Resolver Facultad
    if not id_facultad and facultad_str:
        f = Facultad.query.filter(Facultad.Nombre_Facultad.ilike(f"%{str(facultad_str).strip()}%")).first()
        if f:
            id_facultad = f.ID_Facultad

    if not id_facultad:
        primer_fac = Facultad.query.first()
        id_facultad = primer_fac.ID_Facultad if primer_fac else 1

    # Determinar limites de prestamos (Docentes 5, Estudiantes 3)
    tipo_obj = db.session.get(TipoUsuario, id_tipo)
    nombre_tipo = tipo_obj.Nombre_Tipo if tipo_obj else "Estudiante"
    limite = 5 if "docente" in nombre_tipo.lower() else 3

    try:
        nuevo_usuario = Usuario(
            Codigo_Usuario=codigo_clean,
            Nombre_Usuario=str(nombre).strip(),
            Email_Usuario=email_clean,
            Telefono_Usuario=telefono,
            ID_Tipo_Usuario=id_tipo,
            ID_Facultad=id_facultad,
            Prestamos_Activos=0,
            Limite_Prestamos=datos.get("Limite_Prestamos", limite),
            Activo=True
        )
        # Hashing seguro de la contrasena
        nuevo_usuario.set_password(str(password))

        db.session.add(nuevo_usuario)
        db.session.commit()

        # Generar token JWT con claims de rol y tipo de usuario
        token = create_access_token(
            identity=nuevo_usuario.Codigo_Usuario,
            additional_claims={
                "rol": "usuario",
                "tipo_usuario": nombre_tipo,
                "nombre": nuevo_usuario.Nombre_Usuario,
                "email": nuevo_usuario.Email_Usuario
            }
        )

        return jsonify({
            "mensaje": f"{nombre_tipo} registrado exitosamente",
            "access_token": token,
            "tipo_token": "Bearer",
            "rol": "usuario",
            "es_admin": False,
            "tipo_usuario": nombre_tipo,
            "usuario": nuevo_usuario.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad referencial en la base de datos"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@app.route("/api/auth/registro-bibliotecario", methods=["POST"])
def registrar_bibliotecario():
    """Registra un nuevo bibliotecario/administrador con contrasena encriptada y rol 'bibliotecario'"""
    # Blindaje de seguridad: si la peticion incluye token de usuario regular, rechazar con 403
    auth_hdr = request.headers.get("Authorization", "")
    if auth_hdr.startswith("Bearer "):
        try:
            from flask_jwt_extended import decode_token
            decoded = decode_token(auth_hdr.split(" ")[1])
            if decoded.get("rol") == "usuario":
                return jsonify({
                    "error": "Acceso denegado (403)",
                    "mensaje": "Los usuarios regulares no tienen autorizacion para crear cuentas administrativas."
                }), 403
        except Exception:
            pass

    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Debe enviar los datos en formato JSON"}), 400

    codigo = datos.get("Codigo_Bibliotecario")
    nombre = datos.get("Nombre_Bibliotecario")
    email = datos.get("Email_Bibliotecario")
    password = datos.get("Password")
    id_turno = datos.get("ID_Turno")
    turno_nombre = datos.get("Turno")

    # Validaciones obligatorias
    if not codigo or not nombre or not email or not password:
        return jsonify({
            "error": "Faltan campos obligatorios",
            "detalle": "Codigo_Bibliotecario, Nombre_Bibliotecario, Email_Bibliotecario y Password son requeridos"
        }), 400

    if len(str(password)) < 6:
        return jsonify({"error": "La contrasena debe tener al menos 6 caracteres"}), 400

    codigo_clean = str(codigo).strip()
    email_clean = str(email).strip()

    if Bibliotecario.query.filter_by(Codigo_Bibliotecario=codigo_clean).first():
        return jsonify({"error": f"Ya existe un bibliotecario con el codigo '{codigo_clean}'"}), 400

    if Bibliotecario.query.filter_by(Email_Bibliotecario=email_clean).first():
        return jsonify({"error": f"Ya existe un bibliotecario con el correo '{email_clean}'"}), 400

    # Resolver turno válido para evitar error de integridad referencial
    turno_valido = None
    if id_turno:
        turno_valido = db.session.get(Turno, id_turno)

    if not turno_valido and turno_nombre:
        turno_valido = Turno.query.filter(Turno.Nombre_Turno.ilike(str(turno_nombre).strip())).first()

    if not turno_valido:
        turno_valido = Turno.query.first()

    id_turno = turno_valido.ID_Turno if turno_valido else None

    try:
        nuevo_biblio = Bibliotecario(
            Codigo_Bibliotecario=codigo_clean,
            Nombre_Bibliotecario=str(nombre).strip(),
            Email_Bibliotecario=email_clean,
            ID_Turno=id_turno,
            Activo=True
        )
        nuevo_biblio.set_password(str(password))

        db.session.add(nuevo_biblio)
        db.session.commit()

        token = create_access_token(
            identity=nuevo_biblio.Codigo_Bibliotecario,
            additional_claims={
                "rol": "bibliotecario",
                "tipo_usuario": "Bibliotecario",
                "nombre": nuevo_biblio.Nombre_Bibliotecario,
                "email": nuevo_biblio.Email_Bibliotecario
            }
        )

        return jsonify({
            "mensaje": "Bibliotecario registrado exitosamente",
            "access_token": token,
            "tipo_token": "Bearer",
            "rol": "bibliotecario",
            "es_admin": True,
            "tipo_usuario": "Bibliotecario",
            "bibliotecario": nuevo_biblio.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad referencial en la base de datos"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Inicia sesion (Estudiante, Docente o Bibliotecario) mediante Email o Codigo y Contrasena"""
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Debe enviar los datos en formato JSON"}), 400

    identificador = (
        datos.get("identificador") or
        datos.get("Email_Usuario") or
        datos.get("Codigo_Usuario") or
        datos.get("Email_Bibliotecario") or
        datos.get("Codigo_Bibliotecario")
    )
    password = datos.get("Password")

    if not identificador or not password:
        return jsonify({
            "error": "Debe proporcionar el identificador (Email o Codigo) y la contrasena (Password)"
        }), 400

    identificador_str = str(identificador).strip()

    # 1. Intentar autenticar como Usuario (Estudiante / Docente)
    usuario = Usuario.query.filter(
        (Usuario.Email_Usuario == identificador_str) | (Usuario.Codigo_Usuario == identificador_str)
    ).first()

    if usuario and usuario.check_password(str(password)):
        tipo_nombre = usuario.tipo.Nombre_Tipo if usuario.tipo else "Estudiante"
        token = create_access_token(
            identity=usuario.Codigo_Usuario,
            additional_claims={
                "rol": "usuario",
                "tipo_usuario": tipo_nombre,
                "nombre": usuario.Nombre_Usuario,
                "email": usuario.Email_Usuario
            }
        )
        return jsonify({
            "mensaje": f"Inicio de sesion exitoso ({tipo_nombre})",
            "access_token": token,
            "tipo_token": "Bearer",
            "rol": "usuario",
            "es_admin": False,
            "tipo_usuario": tipo_nombre,
            "usuario": usuario.to_dict()
        }), 200

    # 2. Intentar autenticar como Bibliotecario
    bibliotecario = Bibliotecario.query.filter(
        (Bibliotecario.Email_Bibliotecario == identificador_str) | (Bibliotecario.Codigo_Bibliotecario == identificador_str)
    ).first()

    if bibliotecario and bibliotecario.check_password(str(password)):
        token = create_access_token(
            identity=bibliotecario.Codigo_Bibliotecario,
            additional_claims={
                "rol": "bibliotecario",
                "tipo_usuario": "Bibliotecario",
                "nombre": bibliotecario.Nombre_Bibliotecario,
                "email": bibliotecario.Email_Bibliotecario
            }
        )
        return jsonify({
            "mensaje": "Inicio de sesion exitoso (Bibliotecario)",
            "access_token": token,
            "tipo_token": "Bearer",
            "rol": "bibliotecario",
            "es_admin": True,
            "tipo_usuario": "Bibliotecario",
            "bibliotecario": bibliotecario.to_dict()
        }), 200

    return jsonify({
        "error": "Credenciales invalidas",
        "mensaje": "El usuario o la contrasena son incorrectos"
    }), 401


@app.route("/api/auth/login-bibliotecario", methods=["POST"])
def login_bibliotecario():
    """Inicio de sesion exclusivo para personal bibliotecario/administrativo"""
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Debe enviar los datos en formato JSON"}), 400

    identificador = (
        datos.get("identificador") or
        datos.get("Email_Bibliotecario") or
        datos.get("Codigo_Bibliotecario")
    )
    password = datos.get("Password")

    if not identificador or not password:
        return jsonify({
            "error": "Debe proporcionar el identificador (Email o Codigo) y la contrasena (Password)"
        }), 400

    identificador_str = str(identificador).strip()
    bibliotecario = Bibliotecario.query.filter(
        (Bibliotecario.Email_Bibliotecario == identificador_str) | (Bibliotecario.Codigo_Bibliotecario == identificador_str)
    ).first()

    if not bibliotecario or not bibliotecario.check_password(str(password)):
        return jsonify({
            "error": "Credenciales invalidas",
            "mensaje": "El bibliotecario o la contrasena son incorrectos"
        }), 401

    token = create_access_token(
        identity=bibliotecario.Codigo_Bibliotecario,
        additional_claims={
            "rol": "bibliotecario",
            "tipo_usuario": "Bibliotecario",
            "nombre": bibliotecario.Nombre_Bibliotecario,
            "email": bibliotecario.Email_Bibliotecario
        }
    )

    return jsonify({
        "mensaje": "Inicio de sesion exitoso (Bibliotecario)",
        "access_token": token,
        "tipo_token": "Bearer",
        "rol": "bibliotecario",
        "es_admin": True,
        "tipo_usuario": "Bibliotecario",
        "bibliotecario": bibliotecario.to_dict()
    }), 200


@app.route("/api/auth/perfil", methods=["GET"])
@jwt_required()
def perfil_actual():
    """Ruta protegida: Obtiene los datos del usuario o bibliotecario autenticado segun el token"""
    identidad = get_jwt_identity()
    claims = get_jwt()
    rol = claims.get("rol", "usuario")

    if rol == "bibliotecario":
        biblio = db.session.get(Bibliotecario, identidad)
        if not biblio:
            return jsonify({"error": "Bibliotecario no encontrado"}), 404
        return jsonify({
            "mensaje": "Perfil autenticado (Bibliotecario)",
            "rol": "bibliotecario",
            "es_admin": True,
            "bibliotecario": biblio.to_dict(),
            "perfil": biblio.to_dict()
        }), 200

    usuario = db.session.get(Usuario, identidad)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "mensaje": "Perfil autenticado",
        "rol": "usuario",
        "es_admin": False,
        "usuario": usuario.to_dict(),
        "perfil": usuario.to_dict()
    }), 200


# ==============================================================
# ENDPOINTS DE CONTROL Y METRICAS DE CACHE
# ==============================================================

@app.route("/api/cache/stats", methods=["GET"])
def obtener_estadisticas_cache():
    """Retorna estadisticas y metricas de rendimiento del cache (hits, misses, hit rate %, etc.)"""
    return jsonify(cache.get_stats()), 200


@app.route("/api/cache/clear", methods=["POST"])
@solo_bibliotecario()
def vaciar_cache():
    """Invalida completamente el cache del servidor (requiere rol bibliotecario)"""
    total = cache.clear()
    return jsonify({
        "mensaje": "Cache del servidor vaciado exitosamente",
        "total_claves_eliminadas": total
    }), 200


# ==============================================================
# CONTRATO Y DOCUMENTACION OPENAPI / SWAGGER
# ==============================================================

@app.route("/openapi.yaml", methods=["GET"])
def obtener_openapi_spec():
    """Sirve la especificacion OpenAPI 3.0.3 en formato YAML"""
    with open("openapi.yaml", "r", encoding="utf-8") as f:
        contenido = f.read()
    return contenido, 200, {"Content-Type": "text/yaml; charset=utf-8"}


@app.route("/api/docs", methods=["GET"])
def documentacion_swagger_ui():
    """Interfaz interactiva Swagger UI para exploracion de contratos y endpoints"""
    html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>API Docs - Biblioteca Universitaria</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
  <style>
    body { margin: 0; padding: 0; background: #fafafa; }
    .topbar { display: none !important; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/openapi.yaml',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis],
        layout: "BaseLayout"
      });
    };
  </script>
</body>
</html>"""
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


# Ruta base y portal web interactivo
@app.route("/", methods=["GET"])
@app.route("/portal", methods=["GET"])
@app.route("/catalogo", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def api_info():
    """Sirve la interfaz web completa o el contrato informativo de la API REST"""
    # Si la petición solicita explícitamente HTML o una ruta web:
    if request.path in ["/portal", "/catalogo", "/index.html"] or (request.accept_mimetypes.accept_html and not request.is_json and request.headers.get("Sec-Fetch-Dest") in ["document", "empty", None]):
        return render_template("index.html")

    return jsonify({
        "nombre": "API REST - Biblioteca Universitaria",
        "version": "1.0.0",
        "documentacion": "/api/docs",
        "openapi": "/openapi.yaml",
        "portal_web": "/portal",
        "estado": "activo"
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)