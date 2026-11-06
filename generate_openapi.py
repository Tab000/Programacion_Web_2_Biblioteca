import yaml

def build_openapi():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "API REST Biblioteca Universitaria",
            "description": (
                "Contrato formal OpenAPI 3.0.3 de la API REST para el Sistema de Biblioteca Universitaria.\n"
                "Documenta exhaustivamente los 19 modulos del sistema (CRUD completo), los servicios de autenticacion\n"
                "con JWT (RBAC: Estudiante/Usuario y Bibliotecario/Administrador), métricas de caché en memoria y disponibilidad."
            ),
            "version": "1.0.0",
            "contact": {
                "name": "Soporte Plataforma Biblioteca",
                "email": "biblioteca@universidad.edu.co"
            }
        },
        "servers": [
            {
                "url": "http://127.0.0.1:5000",
                "description": "Servidor Local (127.0.0.1:5000)"
            },
            {
                "url": "http://localhost:5000",
                "description": "Servidor Local (localhost:5000)"
            },
            {
                "url": "/",
                "description": "Servidor Relativo Actual"
            }
        ],
        "tags": [
            {"name": "Autenticación", "description": "Endpoints para registro, inicio de sesión y gestión de perfil"},
            {"name": "Paises", "description": "Gestión de países de procedencia y nacionalidades"},
            {"name": "Idiomas", "description": "Catálogo de idiomas de los libros"},
            {"name": "Editoriales", "description": "Gestión de editoriales de libros"},
            {"name": "Estados Físicos", "description": "Catálogo de condiciones físicas de libros"},
            {"name": "Facultades", "description": "Facultades y dependencias universitarias"},
            {"name": "Tipos de Usuario", "description": "Roles y clasificaciones de usuarios (estudiante, docente, etc.)"},
            {"name": "Turnos", "description": "Turnos de trabajo de bibliotecarios"},
            {"name": "Estados de Reserva", "description": "Estados del ciclo de vida de reservas"},
            {"name": "Estados de Préstamo", "description": "Estados del ciclo de vida de préstamos"},
            {"name": "Ciudades", "description": "Catálogo de ciudades de residencia"},
            {"name": "Categorías", "description": "Clasificación temática y áreas del conocimiento"},
            {"name": "Autores", "description": "Autores de obras literarias y académicas"},
            {"name": "Bibliotecarios", "description": "Personal administrativo y gestión de accesos"},
            {"name": "Libros", "description": "Catálogo de libros y control de acervo"},
            {"name": "Usuarios", "description": "Gestión de lectores y estudiantes universitarios"},
            {"name": "Direcciones", "description": "Direcciones de residencia de usuarios"},
            {"name": "Historial de Ubicaciones", "description": "Trazabilidad de estanterías y ubicaciones de libros"},
            {"name": "Reservas", "description": "Control de reservas y cola de espera de libros"},
            {"name": "Préstamos", "description": "Control de préstamos, plazos, renovaciones y multas"},
            {"name": "Caché", "description": "Monitoreo y administración de la caché en memoria"}
        ],
        "paths": {},
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Token JWT obtenido en /api/auth/login o /api/auth/registro."
                }
            },
            "schemas": {}
        }
    }

    # Helpers
    def error_ref():
        return {"$ref": "#/components/schemas/ErrorResponse"}

    def std_responses(success_status="200", success_desc="Operación exitosa", schema_ref=None, needs_auth=False, needs_admin=False):
        resp = {}
        content = {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_ref}"}}} if schema_ref else {
            "application/json": {"schema": {"type": "object", "properties": {"mensaje": {"type": "string"}}}}
        }
        resp[str(success_status)] = {
            "description": success_desc,
            "content": content
        }
        resp["400"] = {"description": "Datos inválidos o error de integridad", "content": {"application/json": {"schema": error_ref()}}}
        if needs_auth:
            resp["401"] = {"description": "Token no provisto o inválido", "content": {"application/json": {"schema": error_ref()}}}
        if needs_admin:
            resp["403"] = {"description": "Acceso restringido (requiere rol bibliotecario)", "content": {"application/json": {"schema": error_ref()}}}
        resp["500"] = {"description": "Error interno del servidor", "content": {"application/json": {"schema": error_ref()}}}
        return resp

    # Schemas base
    spec["components"]["schemas"]["ErrorResponse"] = {
        "type": "object",
        "required": ["error"],
        "properties": {
            "error": {"type": "string", "example": "Mensaje de error descriptivo"},
            "detalle": {"type": "string", "example": "Detalle técnico o restricción violada"},
            "mensaje": {"type": "string", "example": "Mensaje informativo"}
        }
    }

    spec["components"]["schemas"]["MensajeRespuesta"] = {
        "type": "object",
        "properties": {
            "mensaje": {"type": "string", "example": "Operación completada exitosamente"}
        }
    }

    # ================= AUTH PATHS & SCHEMAS =================
    spec["paths"]["/api/auth/registro"] = {
        "post": {
            "tags": ["Autenticación"],
            "summary": "Registrar nuevo usuario/estudiante",
            "description": "Crea una nueva cuenta de estudiante/usuario con contraseña cifrada y retorna token JWT.",
            "operationId": "authRegistrarUsuario",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RegistroUsuarioRequest"}}}
            },
            "responses": {
                "201": {"description": "Usuario registrado exitosamente", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthResponse"}}}},
                "400": {"description": "Datos incompletos o usuario ya existente", "content": {"application/json": {"schema": error_ref()}}}
            }
        }
    }

    spec["paths"]["/api/auth/registro-bibliotecario"] = {
        "post": {
            "tags": ["Autenticación"],
            "summary": "Registrar nuevo bibliotecario",
            "description": "Crea un nuevo bibliotecario con privilegios de administración.",
            "operationId": "authRegistrarBibliotecario",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RegistroBibliotecarioRequest"}}}
            },
            "responses": {
                "201": {"description": "Bibliotecario registrado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthResponse"}}}},
                "400": {"description": "Datos inválidos", "content": {"application/json": {"schema": error_ref()}}}
            }
        }
    }

    spec["paths"]["/api/auth/opciones-registro"] = {
        "get": {
            "tags": ["Autenticación"],
            "summary": "Opciones de catálogo para registro",
            "description": "Obtiene listas de tipos de usuario, facultades y turnos para alimentar formularios.",
            "operationId": "authOpcionesRegistro",
            "responses": {
                "200": {"description": "Opciones disponibles", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OpcionesRegistroResponse"}}}}
            }
        }
    }

    spec["paths"]["/api/auth/login"] = {
        "post": {
            "tags": ["Autenticación"],
            "summary": "Iniciar sesión (Estudiante o Bibliotecario)",
            "description": "Valida credenciales por Email o Código y retorna token JWT de acceso.",
            "operationId": "authLogin",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginRequest"}}}
            },
            "responses": {
                "200": {"description": "Login exitoso", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthResponse"}}}},
                "401": {"description": "Credenciales inválidas", "content": {"application/json": {"schema": error_ref()}}}
            }
        }
    }

    spec["paths"]["/api/auth/login-bibliotecario"] = {
        "post": {
            "tags": ["Autenticación"],
            "summary": "Iniciar sesión exclusivo para bibliotecarios",
            "description": "Verifica credenciales asegurando que pertenezcan a la tabla bibliotecario.",
            "operationId": "authLoginBibliotecario",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginRequest"}}}
            },
            "responses": {
                "200": {"description": "Login exitoso", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthResponse"}}}},
                "401": {"description": "Credenciales inválidas o no es bibliotecario", "content": {"application/json": {"schema": error_ref()}}}
            }
        }
    }

    spec["paths"]["/api/auth/perfil"] = {
        "get": {
            "tags": ["Autenticación"],
            "summary": "Consultar perfil del usuario autenticado",
            "description": "Retorna información detallada del usuario o bibliotecario a partir del token JWT.",
            "operationId": "authPerfil",
            "security": [{"BearerAuth": []}],
            "responses": {
                "200": {"description": "Perfil del usuario autenticado"},
                "401": {"description": "No autenticado", "content": {"application/json": {"schema": error_ref()}}}
            }
        }
    }

    # Auth Schemas
    spec["components"]["schemas"]["RegistroUsuarioRequest"] = {
        "type": "object",
        "required": ["Codigo_Usuario", "Nombre_Usuario", "Email_Usuario", "Password"],
        "properties": {
            "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
            "Nombre_Usuario": {"type": "string", "example": "Carlos Gomez"},
            "Email_Usuario": {"type": "string", "format": "email", "example": "carlos.gomez@correo.edu.co"},
            "Password": {"type": "string", "format": "password", "example": "claveSegura123"},
            "Telefono_Usuario": {"type": "string", "example": "3001234567"},
            "ID_Tipo_Usuario": {"type": "integer", "example": 1},
            "ID_Facultad": {"type": "integer", "example": 1}
        }
    }

    spec["components"]["schemas"]["RegistroBibliotecarioRequest"] = {
        "type": "object",
        "required": ["Codigo_Bibliotecario", "Nombre_Bibliotecario", "Email_Bibliotecario", "Password"],
        "properties": {
            "Codigo_Bibliotecario": {"type": "string", "example": "BIB_2026_01"},
            "Nombre_Bibliotecario": {"type": "string", "example": "Laura Restrepo"},
            "Email_Bibliotecario": {"type": "string", "format": "email", "example": "laura.restrepo@correo.edu.co"},
            "Password": {"type": "string", "format": "password", "example": "adminPass123"},
            "ID_Turno": {"type": "integer", "example": 1}
        }
    }

    spec["components"]["schemas"]["LoginRequest"] = {
        "type": "object",
        "required": ["Password"],
        "properties": {
            "identificador": {"type": "string", "example": "carlos.gomez@correo.edu.co"},
            "Email_Usuario": {"type": "string", "example": "carlos.gomez@correo.edu.co"},
            "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
            "Password": {"type": "string", "format": "password", "example": "claveSegura123"}
        }
    }

    spec["components"]["schemas"]["AuthResponse"] = {
        "type": "object",
        "properties": {
            "token": {"type": "string", "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
            "tipo_token": {"type": "string", "example": "Bearer"},
            "rol": {"type": "string", "example": "usuario"},
            "usuario": {"type": "object"},
            "mensaje": {"type": "string", "example": "Autenticación exitosa"}
        }
    }

    spec["components"]["schemas"]["OpcionesRegistroResponse"] = {
        "type": "object",
        "properties": {
            "tipos_usuario": {"type": "array", "items": {"type": "object"}},
            "facultades": {"type": "array", "items": {"type": "object"}},
            "turnos": {"type": "array", "items": {"type": "object"}}
        }
    }

    # ================= CACHE PATHS & SCHEMAS =================
    spec["paths"]["/api/cache/stats"] = {
        "get": {
            "tags": ["Caché"],
            "summary": "Estadísticas y rendimiento del caché",
            "description": "Retorna métricas de aciertos (HIT), fallos (MISS), tasa de efectividad y llaves activas.",
            "operationId": "cacheStats",
            "responses": {
                "200": {"description": "Métricas del caché", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CacheStats"}}}}
            }
        }
    }

    spec["paths"]["/api/cache/clear"] = {
        "post": {
            "tags": ["Caché"],
            "summary": "Vaciar caché en memoria",
            "description": "Invalida todas las claves cacheadas. Requiere rol de bibliotecario.",
            "operationId": "cacheClear",
            "security": [{"BearerAuth": []}],
            "responses": std_responses("200", "Caché vaciado exitosamente", schema_ref="MensajeRespuesta", needs_auth=True, needs_admin=True)
        }
    }

    spec["components"]["schemas"]["CacheStats"] = {
        "type": "object",
        "properties": {
            "cache_habilitado": {"type": "boolean", "example": True},
            "entradas_activas": {"type": "integer", "example": 14},
            "total_consultas": {"type": "integer", "example": 150},
            "aciertos_hits": {"type": "integer", "example": 138},
            "fallos_misses": {"type": "integer", "example": 12},
            "tasa_aciertos_pct": {"type": "number", "example": 92.0},
            "total_invalidaciones": {"type": "integer", "example": 5},
            "claves_almacenadas": {"type": "array", "items": {"type": "string"}}
        }
    }

    # ================= 19 CRUD ENTITIES CONFIG =================
    crud_configs = [
        {
            "tag": "Paises",
            "entity": "pais",
            "plural": "paises",
            "url_base": "/api/paises",
            "pk_name": "id_pais",
            "pk_param": "id_pais",
            "pk_type": "integer",
            "model_schema": "Pais",
            "input_schema": "PaisInput",
            "req_fields": ["Nombre_Pais"],
            "properties": {
                "ID_Pais": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Pais": {"type": "string", "example": "Colombia"}
            },
            "input_properties": {
                "Nombre_Pais": {"type": "string", "example": "Colombia"}
            },
            "admin_write": True
        },
        {
            "tag": "Idiomas",
            "entity": "idioma",
            "plural": "idiomas",
            "url_base": "/api/idiomas",
            "pk_name": "id_idioma",
            "pk_param": "id_idioma",
            "pk_type": "integer",
            "model_schema": "Idioma",
            "input_schema": "IdiomaInput",
            "req_fields": ["Nombre_Idioma"],
            "properties": {
                "ID_Idioma": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Idioma": {"type": "string", "example": "Español"}
            },
            "input_properties": {
                "Nombre_Idioma": {"type": "string", "example": "Español"}
            },
            "admin_write": True
        },
        {
            "tag": "Editoriales",
            "entity": "editorial",
            "plural": "editoriales",
            "url_base": "/api/editoriales",
            "pk_name": "id_editorial",
            "pk_param": "id_editorial",
            "pk_type": "integer",
            "model_schema": "Editorial",
            "input_schema": "EditorialInput",
            "req_fields": ["Nombre_Editorial"],
            "properties": {
                "ID_Editorial": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Editorial": {"type": "string", "example": "Editorial Planeta"}
            },
            "input_properties": {
                "Nombre_Editorial": {"type": "string", "example": "Editorial Planeta"}
            },
            "admin_write": True
        },
        {
            "tag": "Estados Físicos",
            "entity": "estado_fisico",
            "plural": "estados_fisicos",
            "url_base": "/api/estados-fisicos",
            "pk_name": "id_estado_fisico",
            "pk_param": "id_estado_fisico",
            "pk_type": "integer",
            "model_schema": "EstadoFisico",
            "input_schema": "EstadoFisicoInput",
            "req_fields": ["Nombre_Estado"],
            "properties": {
                "ID_Estado_Fisico": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Estado": {"type": "string", "example": "Excelente"}
            },
            "input_properties": {
                "Nombre_Estado": {"type": "string", "example": "Excelente"}
            },
            "admin_write": True
        },
        {
            "tag": "Facultades",
            "entity": "facultad",
            "plural": "facultades",
            "url_base": "/api/facultades",
            "pk_name": "id_facultad",
            "pk_param": "id_facultad",
            "pk_type": "integer",
            "model_schema": "Facultad",
            "input_schema": "FacultadInput",
            "req_fields": ["Nombre_Facultad"],
            "properties": {
                "ID_Facultad": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Facultad": {"type": "string", "example": "Ingeniería"}
            },
            "input_properties": {
                "Nombre_Facultad": {"type": "string", "example": "Ingeniería"}
            },
            "admin_write": True
        },
        {
            "tag": "Tipos de Usuario",
            "entity": "tipo_usuario",
            "plural": "tipos_usuario",
            "url_base": "/api/tipos-usuario",
            "pk_name": "id_tipo_usuario",
            "pk_param": "id_tipo_usuario",
            "pk_type": "integer",
            "model_schema": "TipoUsuario",
            "input_schema": "TipoUsuarioInput",
            "req_fields": ["Nombre_Tipo"],
            "properties": {
                "ID_Tipo_Usuario": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Tipo": {"type": "string", "example": "Estudiante Pregrado"}
            },
            "input_properties": {
                "Nombre_Tipo": {"type": "string", "example": "Estudiante Pregrado"}
            },
            "admin_write": True
        },
        {
            "tag": "Turnos",
            "entity": "turno",
            "plural": "turnos",
            "url_base": "/api/turnos",
            "pk_name": "id_turno",
            "pk_param": "id_turno",
            "pk_type": "integer",
            "model_schema": "Turno",
            "input_schema": "TurnoInput",
            "req_fields": ["Nombre_Turno"],
            "properties": {
                "ID_Turno": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Turno": {"type": "string", "example": "Mañana (07:00 - 15:00)"}
            },
            "input_properties": {
                "Nombre_Turno": {"type": "string", "example": "Mañana (07:00 - 15:00)"}
            },
            "admin_write": True
        },
        {
            "tag": "Estados de Reserva",
            "entity": "estado_reserva",
            "plural": "estados_reserva",
            "url_base": "/api/estados-reserva",
            "pk_name": "id_estado_reserva",
            "pk_param": "id_estado_reserva",
            "pk_type": "integer",
            "model_schema": "EstadoReserva",
            "input_schema": "EstadoReservaInput",
            "req_fields": ["Nombre_Estado"],
            "properties": {
                "ID_Estado_Reserva": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Estado": {"type": "string", "example": "En Cola"}
            },
            "input_properties": {
                "Nombre_Estado": {"type": "string", "example": "En Cola"}
            },
            "admin_write": True
        },
        {
            "tag": "Estados de Préstamo",
            "entity": "estado_prestamo",
            "plural": "estados_prestamo",
            "url_base": "/api/estados-prestamo",
            "pk_name": "id_estado_prestamo",
            "pk_param": "id_estado_prestamo",
            "pk_type": "integer",
            "model_schema": "EstadoPrestamo",
            "input_schema": "EstadoPrestamoInput",
            "req_fields": ["Nombre_Estado"],
            "properties": {
                "ID_Estado_Prestamo": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Estado": {"type": "string", "example": "Activo"}
            },
            "input_properties": {
                "Nombre_Estado": {"type": "string", "example": "Activo"}
            },
            "admin_write": True
        },
        {
            "tag": "Ciudades",
            "entity": "ciudad",
            "plural": "ciudades",
            "url_base": "/api/ciudades",
            "pk_name": "id_ciudad",
            "pk_param": "id_ciudad",
            "pk_type": "integer",
            "model_schema": "Ciudad",
            "input_schema": "CiudadInput",
            "req_fields": ["Nombre_Ciudad"],
            "properties": {
                "ID_Ciudad": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Ciudad": {"type": "string", "example": "Bogotá"}
            },
            "input_properties": {
                "Nombre_Ciudad": {"type": "string", "example": "Bogotá"}
            },
            "admin_write": True
        },
        {
            "tag": "Categorías",
            "entity": "categoria",
            "plural": "categorias",
            "url_base": "/api/categorias",
            "pk_name": "id_categoria",
            "pk_param": "id_categoria",
            "pk_type": "integer",
            "model_schema": "Categoria",
            "input_schema": "CategoriaInput",
            "req_fields": ["Nombre_Categoria"],
            "properties": {
                "ID_Categoria": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Categoria": {"type": "string", "example": "Programación Web"},
                "Nivel": {"type": "integer", "example": 2}
            },
            "input_properties": {
                "Nombre_Categoria": {"type": "string", "example": "Programación Web"},
                "Nivel": {"type": "integer", "example": 2}
            },
            "admin_write": True
        },
        {
            "tag": "Autores",
            "entity": "autor",
            "plural": "autores",
            "url_base": "/api/autores",
            "pk_name": "id_autor",
            "pk_param": "id_autor",
            "pk_type": "integer",
            "model_schema": "Autor",
            "input_schema": "AutorInput",
            "req_fields": ["Nombre_Autor"],
            "properties": {
                "ID_Autor": {"type": "integer", "readOnly": True, "example": 1},
                "Nombre_Autor": {"type": "string", "example": "Gabriel García Márquez"},
                "Bibliografia": {"type": "string", "example": "Premio Nobel de Literatura 1982"},
                "ID_Pais": {"type": "integer", "example": 1},
                "Pais": {"type": "string", "example": "Colombia"}
            },
            "input_properties": {
                "Nombre_Autor": {"type": "string", "example": "Gabriel García Márquez"},
                "Bibliografia": {"type": "string", "example": "Premio Nobel de Literatura 1982"},
                "ID_Pais": {"type": "integer", "example": 1}
            },
            "admin_write": True
        },
        {
            "tag": "Bibliotecarios",
            "entity": "bibliotecario",
            "plural": "bibliotecarios",
            "url_base": "/api/bibliotecarios",
            "pk_name": "codigo_bibliotecario",
            "pk_param": "codigo_bibliotecario",
            "pk_type": "string",
            "model_schema": "Bibliotecario",
            "input_schema": "BibliotecarioInput",
            "req_fields": ["Codigo_Bibliotecario", "Nombre_Bibliotecario", "Email_Bibliotecario", "Password"],
            "properties": {
                "Codigo_Bibliotecario": {"type": "string", "example": "BIB_001"},
                "Nombre_Bibliotecario": {"type": "string", "example": "Ana Morales"},
                "Email_Bibliotecario": {"type": "string", "format": "email", "example": "ana.morales@correo.edu.co"},
                "Activo": {"type": "boolean", "example": True},
                "Fecha_Registro": {"type": "string", "format": "date-time", "example": "2026-01-15T08:00:00"},
                "ID_Turno": {"type": "integer", "example": 1},
                "Turno": {"type": "string", "example": "Mañana"}
            },
            "input_properties": {
                "Codigo_Bibliotecario": {"type": "string", "example": "BIB_001"},
                "Nombre_Bibliotecario": {"type": "string", "example": "Ana Morales"},
                "Email_Bibliotecario": {"type": "string", "format": "email", "example": "ana.morales@correo.edu.co"},
                "Password": {"type": "string", "format": "password", "example": "claveBibliotecario123"},
                "Activo": {"type": "boolean", "example": True},
                "ID_Turno": {"type": "integer", "example": 1}
            },
            "admin_write": True
        },
        {
            "tag": "Libros",
            "entity": "libro",
            "plural": "libros",
            "url_base": "/api/libros",
            "pk_name": "codigo_libro",
            "pk_param": "codigo_libro",
            "pk_type": "string",
            "model_schema": "Libro",
            "input_schema": "LibroInput",
            "req_fields": ["Codigo_Libro", "Titulo_Libro"],
            "properties": {
                "Codigo_Libro": {"type": "string", "example": "LIB_001"},
                "Titulo_Libro": {"type": "string", "example": "Cien Años de Soledad"},
                "Isbn_Libro": {"type": "string", "example": "978-0307474728"},
                "Edicion": {"type": "string", "example": "1ra Edición Conmemorativa"},
                "Anio_Publicacion": {"type": "integer", "example": 1967},
                "Fecha_Ingreso": {"type": "string", "format": "date-time", "example": "2026-02-10T10:00:00"},
                "ID_Editorial": {"type": "integer", "example": 1},
                "Editorial": {"type": "string", "example": "Sudamericana"},
                "ID_Idioma": {"type": "integer", "example": 1},
                "Idioma": {"type": "string", "example": "Español"},
                "ID_Estado_Fisico": {"type": "integer", "example": 1},
                "Estado_Fisico": {"type": "string", "example": "Excelente"},
                "Codigo_Bibliotecario": {"type": "string", "example": "BIB_001"},
                "Bibliotecario": {"type": "string", "example": "Ana Morales"},
                "autores": {"type": "array", "items": {"$ref": "#/components/schemas/Autor"}},
                "categorias": {"type": "array", "items": {"$ref": "#/components/schemas/Categoria"}}
            },
            "input_properties": {
                "Codigo_Libro": {"type": "string", "example": "LIB_001"},
                "Titulo_Libro": {"type": "string", "example": "Cien Años de Soledad"},
                "Isbn_Libro": {"type": "string", "example": "978-0307474728"},
                "Edicion": {"type": "string", "example": "1ra Edición"},
                "Anio_Publicacion": {"type": "integer", "example": 1967},
                "ID_Editorial": {"type": "integer", "example": 1},
                "ID_Idioma": {"type": "integer", "example": 1},
                "ID_Estado_Fisico": {"type": "integer", "example": 1},
                "Codigo_Bibliotecario": {"type": "string", "example": "BIB_001"},
                "autores_ids": {"type": "array", "items": {"type": "integer"}, "example": [1]},
                "categorias_ids": {"type": "array", "items": {"type": "integer"}, "example": [1]}
            },
            "admin_write": True
        },
        {
            "tag": "Usuarios",
            "entity": "usuario",
            "plural": "usuarios",
            "url_base": "/api/usuarios",
            "pk_name": "codigo_usuario",
            "pk_param": "codigo_usuario",
            "pk_type": "string",
            "model_schema": "Usuario",
            "input_schema": "UsuarioInput",
            "req_fields": ["Codigo_Usuario", "Nombre_Usuario", "Email_Usuario", "Password"],
            "properties": {
                "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
                "Nombre_Usuario": {"type": "string", "example": "Carlos Gomez"},
                "Email_Usuario": {"type": "string", "format": "email", "example": "carlos.gomez@correo.edu.co"},
                "Telefono_Usuario": {"type": "string", "example": "3001234567"},
                "Prestamos_Activos": {"type": "integer", "example": 0},
                "Limite_Prestamos": {"type": "integer", "example": 3},
                "Activo": {"type": "boolean", "example": True},
                "Fecha_Registro": {"type": "string", "format": "date-time", "example": "2026-03-01T09:00:00"},
                "ID_Tipo_Usuario": {"type": "integer", "example": 1},
                "Tipo_Usuario": {"type": "string", "example": "Estudiante Pregrado"},
                "ID_Facultad": {"type": "integer", "example": 1},
                "Facultad": {"type": "string", "example": "Ingeniería"}
            },
            "input_properties": {
                "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
                "Nombre_Usuario": {"type": "string", "example": "Carlos Gomez"},
                "Email_Usuario": {"type": "string", "format": "email", "example": "carlos.gomez@correo.edu.co"},
                "Password": {"type": "string", "format": "password", "example": "claveUsuario123"},
                "Telefono_Usuario": {"type": "string", "example": "3001234567"},
                "Limite_Prestamos": {"type": "integer", "example": 3},
                "Activo": {"type": "boolean", "example": True},
                "ID_Tipo_Usuario": {"type": "integer", "example": 1},
                "ID_Facultad": {"type": "integer", "example": 1}
            },
            "admin_write": True
        },
        {
            "tag": "Direcciones",
            "entity": "direccion",
            "plural": "direcciones",
            "url_base": "/api/direcciones",
            "pk_name": "id_direccion",
            "pk_param": "id_direccion",
            "pk_type": "integer",
            "model_schema": "Direccion",
            "input_schema": "DireccionInput",
            "req_fields": ["Codigo_Usuario"],
            "properties": {
                "ID_Direccion": {"type": "integer", "readOnly": True, "example": 1},
                "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
                "Usuario": {"type": "string", "example": "Carlos Gomez"},
                "Calle_Avenida": {"type": "string", "example": "Carrera 45 # 26-85"},
                "Numero": {"type": "string", "example": "Apto 302"},
                "Barrio": {"type": "string", "example": "Ciudad Universitaria"},
                "ID_Ciudad": {"type": "integer", "example": 1},
                "Ciudad": {"type": "string", "example": "Bogotá"}
            },
            "input_properties": {
                "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
                "Calle_Avenida": {"type": "string", "example": "Carrera 45 # 26-85"},
                "Numero": {"type": "string", "example": "Apto 302"},
                "Barrio": {"type": "string", "example": "Ciudad Universitaria"},
                "ID_Ciudad": {"type": "integer", "example": 1}
            },
            "admin_write": False
        },
        {
            "tag": "Historial de Ubicaciones",
            "entity": "historial_ubicacion",
            "plural": "historial_ubicaciones",
            "url_base": "/api/historial-ubicaciones",
            "pk_name": "id_historial",
            "pk_param": "id_historial",
            "pk_type": "integer",
            "model_schema": "HistorialUbicacion",
            "input_schema": "HistorialUbicacionInput",
            "req_fields": ["Codigo_Libro", "Estante_Ubicacion"],
            "properties": {
                "ID_Historial": {"type": "integer", "readOnly": True, "example": 1},
                "Codigo_Libro": {"type": "string", "example": "LIB_001"},
                "Libro": {"type": "string", "example": "Cien Años de Soledad"},
                "Estante_Ubicacion": {"type": "string", "example": "Estante A-3 Nivel 2"},
                "Fecha_Asignacion": {"type": "string", "format": "date", "example": "2026-02-15"}
            },
            "input_properties": {
                "Codigo_Libro": {"type": "string", "example": "LIB_001"},
                "Estante_Ubicacion": {"type": "string", "example": "Estante A-3 Nivel 2"},
                "Fecha_Asignacion": {"type": "string", "format": "date", "example": "2026-02-15"}
            },
            "admin_write": True
        },
        {
            "tag": "Reservas",
            "entity": "reserva",
            "plural": "reservas",
            "url_base": "/api/reservas",
            "pk_name": "codigo_reserva",
            "pk_param": "codigo_reserva",
            "pk_type": "integer",
            "model_schema": "Reserva",
            "input_schema": "ReservaInput",
            "req_fields": ["Codigo_Usuario", "Codigo_Libro"],
            "properties": {
                "Codigo_Reserva": {"type": "integer", "readOnly": True, "example": 1},
                "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
                "Usuario": {"type": "string", "example": "Carlos Gomez"},
                "Codigo_Libro": {"type": "string", "example": "LIB_001"},
                "Libro": {"type": "string", "example": "Cien Años de Soledad"},
                "Fecha_Reserva": {"type": "string", "format": "date-time", "example": "2026-03-05T14:30:00"},
                "Posicion_Cola_Reserva": {"type": "integer", "example": 1},
                "ID_Estado_Reserva": {"type": "integer", "example": 1},
                "Estado_Reserva": {"type": "string", "example": "En Cola"},
                "Codigo_Bibliotecario": {"type": "string", "example": "BIB_001"},
                "Bibliotecario": {"type": "string", "example": "Ana Morales"}
            },
            "input_properties": {
                "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
                "Codigo_Libro": {"type": "string", "example": "LIB_001"},
                "Fecha_Reserva": {"type": "string", "format": "date-time", "example": "2026-03-05T14:30:00"},
                "Posicion_Cola_Reserva": {"type": "integer", "example": 1},
                "ID_Estado_Reserva": {"type": "integer", "example": 1},
                "Codigo_Bibliotecario": {"type": "string", "example": "BIB_001"}
            },
            "admin_write": False
        },
        {
            "tag": "Préstamos",
            "entity": "prestamo",
            "plural": "prestamos",
            "url_base": "/api/prestamos",
            "pk_name": "id_prestamo",
            "pk_param": "id_prestamo",
            "pk_type": "integer",
            "model_schema": "Prestamo",
            "input_schema": "PrestamoInput",
            "req_fields": ["Codigo_Usuario", "Codigo_Libro"],
            "properties": {
                "ID_Prestamo": {"type": "integer", "readOnly": True, "example": 1},
                "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
                "Usuario": {"type": "string", "example": "Carlos Gomez"},
                "Codigo_Libro": {"type": "string", "example": "LIB_001"},
                "Libro": {"type": "string", "example": "Cien Años de Soledad"},
                "Codigo_Bibliotecario": {"type": "string", "example": "BIB_001"},
                "Bibliotecario": {"type": "string", "example": "Ana Morales"},
                "Fecha_Prestamo": {"type": "string", "format": "date", "example": "2026-03-01"},
                "Fecha_Dev_Prevista": {"type": "string", "format": "date", "example": "2026-03-15"},
                "Fecha_Dev_Real": {"type": "string", "format": "date", "nullable": True, "example": None},
                "Dia_Retraso": {"type": "integer", "example": 0},
                "Multa_Calculada": {"type": "number", "format": "float", "example": 0.0},
                "Numero_Renovaciones": {"type": "integer", "example": 0},
                "ID_Estado_Prestamo": {"type": "integer", "example": 1},
                "Estado_Prestamo": {"type": "string", "example": "Activo"}
            },
            "input_properties": {
                "Codigo_Usuario": {"type": "string", "example": "USR_2026_01"},
                "Codigo_Libro": {"type": "string", "example": "LIB_001"},
                "Codigo_Bibliotecario": {"type": "string", "example": "BIB_001"},
                "Fecha_Prestamo": {"type": "string", "format": "date", "example": "2026-03-01"},
                "Fecha_Dev_Prevista": {"type": "string", "format": "date", "example": "2026-03-15"},
                "Fecha_Dev_Real": {"type": "string", "format": "date", "example": "2026-03-14"},
                "Dia_Retraso": {"type": "integer", "example": 0},
                "Multa_Calculada": {"type": "number", "format": "float", "example": 0.0},
                "Numero_Renovaciones": {"type": "integer", "example": 0},
                "ID_Estado_Prestamo": {"type": "integer", "example": 1}
            },
            "admin_write": True
        }
    ]

    # Register Schemas and Paths for each entity
    for c in crud_configs:
        model_name = c["model_schema"]
        input_name = c["input_schema"]
        list_response_name = f"Lista{model_name}Response"
        single_response_name = f"{model_name}Response"

        # Model Schema
        spec["components"]["schemas"][model_name] = {
            "type": "object",
            "properties": c["properties"]
        }

        # Input Schema
        input_schema_obj = {
            "type": "object",
            "properties": c["input_properties"]
        }
        if c.get("req_fields"):
            input_schema_obj["required"] = c["req_fields"]
        spec["components"]["schemas"][input_name] = input_schema_obj

        # List Response Schema
        spec["components"]["schemas"][list_response_name] = {
            "type": "object",
            "properties": {
                "total": {"type": "integer", "example": 10},
                c["plural"]: {"type": "array", "items": {"$ref": f"#/components/schemas/{model_name}"}},
                "datos": {"type": "array", "items": {"$ref": f"#/components/schemas/{model_name}"}}
            }
        }

        # Single Response Schema
        spec["components"]["schemas"][single_response_name] = {
            "type": "object",
            "properties": {
                "mensaje": {"type": "string", "example": f"{c['tag']} procesado correctamente"},
                c["entity"]: {"$ref": f"#/components/schemas/{model_name}"},
                "dato": {"$ref": f"#/components/schemas/{model_name}"}
            }
        }

        # Collection Path: GET & POST
        path_collection = c["url_base"]
        spec["paths"][path_collection] = {
            "get": {
                "tags": [c["tag"]],
                "summary": f"Listar {c['tag']}",
                "description": f"Retorna el catálogo completo de {c['tag']}.",
                "operationId": f"listar_{c['plural']}",
                "responses": {
                    "200": {
                        "description": f"Listado de {c['tag']}",
                        "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{list_response_name}"}}}
                    },
                    "500": {"description": "Error interno del servidor", "content": {"application/json": {"schema": error_ref()}}}
                }
            },
            "post": {
                "tags": [c["tag"]],
                "summary": f"Crear {c['entity'].replace('_', ' ')}",
                "description": f"Registra un nuevo registro en {c['tag']}." + (" Requiere rol de bibliotecario." if c["admin_write"] else " Requiere estar autenticado."),
                "operationId": f"crear_{c['entity']}",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{input_name}"}}}
                },
                "responses": std_responses("201", f"{c['tag']} creado exitosamente", schema_ref=single_response_name, needs_auth=True, needs_admin=c["admin_write"])
            }
        }

        # Item Path: GET, PUT, DELETE
        path_item = f"{c['url_base']}/{{{c['pk_param']}}}"
        spec["paths"][path_item] = {
            "get": {
                "tags": [c["tag"]],
                "summary": f"Obtener {c['entity'].replace('_', ' ')} por identificador",
                "description": f"Consulta los detalles de un registro específico de {c['tag']} mediante su clave primaria.",
                "operationId": f"obtener_{c['entity']}",
                "parameters": [
                    {
                        "name": c["pk_param"],
                        "in": "path",
                        "required": True,
                        "description": f"Identificador ({c['pk_name']}) del registro.",
                        "schema": {"type": c["pk_type"]}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Registro encontrado",
                        "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{single_response_name}"}}}
                    },
                    "404": {"description": "Registro no encontrado", "content": {"application/json": {"schema": error_ref()}}},
                    "500": {"description": "Error interno", "content": {"application/json": {"schema": error_ref()}}}
                }
            },
            "put": {
                "tags": [c["tag"]],
                "summary": f"Actualizar {c['entity'].replace('_', ' ')}",
                "description": f"Actualiza los datos de un registro en {c['tag']}." + (" Requiere rol de bibliotecario." if c["admin_write"] else " Requiere autenticación/permisos."),
                "operationId": f"actualizar_{c['entity']}",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": c["pk_param"],
                        "in": "path",
                        "required": True,
                        "description": f"Identificador ({c['pk_name']}) del registro a actualizar.",
                        "schema": {"type": c["pk_type"]}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{input_name}"}}}
                },
                "responses": std_responses("200", f"{c['tag']} actualizado exitosamente", schema_ref=single_response_name, needs_auth=True, needs_admin=c["admin_write"])
            },
            "delete": {
                "tags": [c["tag"]],
                "summary": f"Eliminar {c['entity'].replace('_', ' ')}",
                "description": f"Elimina el registro de {c['tag']} si no tiene dependencias asociadas." + (" Requiere rol bibliotecario." if c["admin_write"] else " Requiere autenticación."),
                "operationId": f"eliminar_{c['entity']}",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": c["pk_param"],
                        "in": "path",
                        "required": True,
                        "description": f"Identificador ({c['pk_name']}) del registro a eliminar.",
                        "schema": {"type": c["pk_type"]}
                    }
                ],
                "responses": std_responses("200", f"{c['tag']} eliminado exitosamente", schema_ref="MensajeRespuesta", needs_auth=True, needs_admin=c["admin_write"])
            }
        }

    # Additional custom endpoint: Libro Disponibilidad
    spec["paths"]["/api/libros/{codigo_libro}/disponibilidad"] = {
        "get": {
            "tags": ["Libros"],
            "summary": "Consultar disponibilidad en tiempo real de un libro",
            "description": "Verifica si el ejemplar está actualmente prestado, la fecha estimada de retorno y el número de reservas en cola.",
            "operationId": "consultarDisponibilidadLibro",
            "parameters": [
                {
                    "name": "codigo_libro",
                    "in": "path",
                    "required": True,
                    "description": "Código identificador del libro",
                    "schema": {"type": "string", "example": "LIB_001"}
                }
            ],
            "responses": {
                "200": {
                    "description": "Estado de disponibilidad del libro",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "codigo_libro": {"type": "string", "example": "LIB_001"},
                                    "titulo_libro": {"type": "string", "example": "Cien Años de Soledad"},
                                    "disponible": {"type": "boolean", "example": True},
                                    "prestamo_activo": {"type": "object", "nullable": True},
                                    "total_reservas_en_cola": {"type": "integer", "example": 0}
                                }
                            }
                        }
                    }
                },
                "404": {"description": "Libro no encontrado", "content": {"application/json": {"schema": error_ref()}}}
            }
        }
    }

    return spec

if __name__ == "__main__":
    spec = build_openapi()
    with open("openapi.yaml", "w", encoding="utf-8") as f:
        yaml.dump(spec, f, sort_keys=False, allow_unicode=True, indent=2)
    print("openapi.yaml generado exitosamente!")
