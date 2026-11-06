import os
from functools import wraps
from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from modelo import (
    db, Pais, Idioma, Editorial, EstadoFisico, Facultad,
    TipoUsuario, Turno, EstadoReserva, EstadoPrestamo, Ciudad,
    Categoria, Autor, Bibliotecario, Libro, Usuario, Direccion,
    HistorialUbicacion, Reserva, Prestamo, parse_date, parse_datetime
)

from auth_utils import (
    solo_bibliotecario, solo_autenticado, puede_gestionar_usuario, es_bibliotecario
)
from cache_manager import cache, cached, no_cache

crud_bp = Blueprint("crud_api", __name__, url_prefix="/api")


# ============================================================================
# 1. PAIS (PK: ID_Pais)
# ============================================================================

@crud_bp.route("/paises", methods=["GET"])
@cached(ttl=1800, prefix="paises", public=True)
def listar_paises():
    items = Pais.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "paises": res, "datos": res}), 200

@crud_bp.route("/paises/<int:id_pais>", methods=["GET"])
@cached(ttl=1800, prefix="paises", public=True)
def obtener_pais(id_pais):
    item = db.session.get(Pais, id_pais)
    if not item:
        return jsonify({"error": f"No se encontro ningun pais con ID {id_pais}"}), 404
    return jsonify({"pais": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/paises", methods=["POST"])
@solo_bibliotecario()
def crear_pais():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Pais")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Pais' es obligatorio"}), 400
    try:
        nuevo = Pais(Nombre_Pais=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("paises")
        return jsonify({"mensaje": "Pais creado exitosamente", "pais": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el pais", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/paises/<int:id_pais>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_pais(id_pais):
    item = db.session.get(Pais, id_pais)
    if not item:
        return jsonify({"error": f"No se encontro ningun pais con ID {id_pais}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Pais" in datos:
        item.Nombre_Pais = str(datos["Nombre_Pais"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("paises")
        return jsonify({"mensaje": "Pais actualizado exitosamente", "pais": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el pais", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/paises/<int:id_pais>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_pais(id_pais):
    item = db.session.get(Pais, id_pais)
    if not item:
        return jsonify({"error": f"No se encontro ningun pais con ID {id_pais}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("paises")
        return jsonify({"mensaje": f"Pais con ID {id_pais} eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar el pais porque tiene registros asociados (ej. autores)"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 2. IDIOMA (PK: ID_Idioma)
# ============================================================================

@crud_bp.route("/idiomas", methods=["GET"])
@cached(ttl=1800, prefix="idiomas", public=True)
def listar_idiomas():
    items = Idioma.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "idiomas": res, "datos": res}), 200

@crud_bp.route("/idiomas/<int:id_idioma>", methods=["GET"])
@cached(ttl=1800, prefix="idiomas", public=True)
def obtener_idioma(id_idioma):
    item = db.session.get(Idioma, id_idioma)
    if not item:
        return jsonify({"error": f"No se encontro ningun idioma con ID {id_idioma}"}), 404
    return jsonify({"idioma": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/idiomas", methods=["POST"])
@solo_bibliotecario()
def crear_idioma():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Idioma")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Idioma' es obligatorio"}), 400
    try:
        nuevo = Idioma(Nombre_Idioma=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("idiomas")
        return jsonify({"mensaje": "Idioma creado exitosamente", "idioma": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el idioma", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/idiomas/<int:id_idioma>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_idioma(id_idioma):
    item = db.session.get(Idioma, id_idioma)
    if not item:
        return jsonify({"error": f"No se encontro ningun idioma con ID {id_idioma}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Idioma" in datos:
        item.Nombre_Idioma = str(datos["Nombre_Idioma"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("idiomas")
        return jsonify({"mensaje": "Idioma actualizado exitosamente", "idioma": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el idioma", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/idiomas/<int:id_idioma>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_idioma(id_idioma):
    item = db.session.get(Idioma, id_idioma)
    if not item:
        return jsonify({"error": f"No se encontro ningun idioma con ID {id_idioma}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("idiomas")
        return jsonify({"mensaje": f"Idioma con ID {id_idioma} eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar el idioma porque tiene libros asociados"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 3. EDITORIAL (PK: ID_Editorial)
# ============================================================================

@crud_bp.route("/editoriales", methods=["GET"])
@cached(ttl=1800, prefix="editoriales", public=True)
def listar_editoriales():
    items = Editorial.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "editoriales": res, "datos": res}), 200

@crud_bp.route("/editoriales/<int:id_editorial>", methods=["GET"])
@cached(ttl=1800, prefix="editoriales", public=True)
def obtener_editorial(id_editorial):
    item = db.session.get(Editorial, id_editorial)
    if not item:
        return jsonify({"error": f"No se encontro ninguna editorial con ID {id_editorial}"}), 404
    return jsonify({"editorial": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/editoriales", methods=["POST"])
@solo_bibliotecario()
def crear_editorial():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Editorial")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Editorial' es obligatorio"}), 400
    try:
        nuevo = Editorial(Nombre_Editorial=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("editoriales")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": "Editorial creada exitosamente", "editorial": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear la editorial", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/editoriales/<int:id_editorial>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_editorial(id_editorial):
    item = db.session.get(Editorial, id_editorial)
    if not item:
        return jsonify({"error": f"No se encontro ninguna editorial con ID {id_editorial}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Editorial" in datos:
        item.Nombre_Editorial = str(datos["Nombre_Editorial"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("editoriales")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": "Editorial actualizada exitosamente", "editorial": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar la editorial", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/editoriales/<int:id_editorial>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_editorial(id_editorial):
    item = db.session.get(Editorial, id_editorial)
    if not item:
        return jsonify({"error": f"No se encontro ninguna editorial con ID {id_editorial}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("editoriales")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": f"Editorial con ID {id_editorial} eliminada exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar la editorial porque tiene libros asociados"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 4. ESTADO_FISICO (PK: ID_Estado_Fisico)
# ============================================================================

@crud_bp.route("/estados-fisicos", methods=["GET"])
@cached(ttl=1800, prefix="estados-fisicos", public=True)
def listar_estados_fisicos():
    items = EstadoFisico.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "estados_fisicos": res, "datos": res}), 200

@crud_bp.route("/estados-fisicos/<int:id_estado_fisico>", methods=["GET"])
@cached(ttl=1800, prefix="estados-fisicos", public=True)
def obtener_estado_fisico(id_estado_fisico):
    item = db.session.get(EstadoFisico, id_estado_fisico)
    if not item:
        return jsonify({"error": f"No se encontro ningun estado fisico con ID {id_estado_fisico}"}), 404
    return jsonify({"estado_fisico": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/estados-fisicos", methods=["POST"])
@solo_bibliotecario()
def crear_estado_fisico():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Estado")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Estado' es obligatorio"}), 400
    try:
        nuevo = EstadoFisico(Nombre_Estado=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("estados-fisicos")
        return jsonify({"mensaje": "Estado fisico creado exitosamente", "estado_fisico": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el estado fisico", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/estados-fisicos/<int:id_estado_fisico>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_estado_fisico(id_estado_fisico):
    item = db.session.get(EstadoFisico, id_estado_fisico)
    if not item:
        return jsonify({"error": f"No se encontro ningun estado fisico con ID {id_estado_fisico}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Estado" in datos:
        item.Nombre_Estado = str(datos["Nombre_Estado"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("estados-fisicos")
        return jsonify({"mensaje": "Estado fisico actualizado exitosamente", "estado_fisico": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el estado fisico", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/estados-fisicos/<int:id_estado_fisico>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_estado_fisico(id_estado_fisico):
    item = db.session.get(EstadoFisico, id_estado_fisico)
    if not item:
        return jsonify({"error": f"No se encontro ningun estado fisico con ID {id_estado_fisico}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("estados-fisicos")
        return jsonify({"mensaje": f"Estado fisico con ID {id_estado_fisico} eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar el estado fisico porque tiene libros asociados"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 5. FACULTAD (PK: ID_Facultad)
# ============================================================================

@crud_bp.route("/facultades", methods=["GET"])
@cached(ttl=1800, prefix="facultades", public=True)
def listar_facultades():
    items = Facultad.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "facultades": res, "datos": res}), 200

@crud_bp.route("/facultades/<int:id_facultad>", methods=["GET"])
@cached(ttl=1800, prefix="facultades", public=True)
def obtener_facultad(id_facultad):
    item = db.session.get(Facultad, id_facultad)
    if not item:
        return jsonify({"error": f"No se encontro ninguna facultad con ID {id_facultad}"}), 404
    return jsonify({"facultad": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/facultades", methods=["POST"])
@solo_bibliotecario()
def crear_facultad():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Facultad")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Facultad' es obligatorio"}), 400
    try:
        nuevo = Facultad(Nombre_Facultad=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("facultades")
        return jsonify({"mensaje": "Facultad creada exitosamente", "facultad": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear la facultad", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/facultades/<int:id_facultad>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_facultad(id_facultad):
    item = db.session.get(Facultad, id_facultad)
    if not item:
        return jsonify({"error": f"No se encontro ninguna facultad con ID {id_facultad}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Facultad" in datos:
        item.Nombre_Facultad = str(datos["Nombre_Facultad"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("facultades")
        return jsonify({"mensaje": "Facultad actualizada exitosamente", "facultad": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar la facultad", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/facultades/<int:id_facultad>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_facultad(id_facultad):
    item = db.session.get(Facultad, id_facultad)
    if not item:
        return jsonify({"error": f"No se encontro ninguna facultad con ID {id_facultad}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("facultades")
        return jsonify({"mensaje": f"Facultad con ID {id_facultad} eliminada exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar la facultad porque tiene usuarios asociados"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 6. TIPO_USUARIO (PK: ID_Tipo_Usuario)
# ============================================================================

@crud_bp.route("/tipos-usuario", methods=["GET"])
@cached(ttl=1800, prefix="tipos-usuario", public=True)
def listar_tipos_usuario():
    items = TipoUsuario.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "tipos_usuario": res, "datos": res}), 200

@crud_bp.route("/tipos-usuario/<int:id_tipo_usuario>", methods=["GET"])
@cached(ttl=1800, prefix="tipos-usuario", public=True)
def obtener_tipo_usuario(id_tipo_usuario):
    item = db.session.get(TipoUsuario, id_tipo_usuario)
    if not item:
        return jsonify({"error": f"No se encontro ningun tipo de usuario con ID {id_tipo_usuario}"}), 404
    return jsonify({"tipo_usuario": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/tipos-usuario", methods=["POST"])
@solo_bibliotecario()
def crear_tipo_usuario():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Tipo")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Tipo' es obligatorio"}), 400
    try:
        nuevo = TipoUsuario(Nombre_Tipo=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("tipos-usuario")
        return jsonify({"mensaje": "Tipo de usuario creado exitosamente", "tipo_usuario": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el tipo de usuario", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/tipos-usuario/<int:id_tipo_usuario>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_tipo_usuario(id_tipo_usuario):
    item = db.session.get(TipoUsuario, id_tipo_usuario)
    if not item:
        return jsonify({"error": f"No se encontro ningun tipo de usuario con ID {id_tipo_usuario}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Tipo" in datos:
        item.Nombre_Tipo = str(datos["Nombre_Tipo"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("tipos-usuario")
        return jsonify({"mensaje": "Tipo de usuario actualizado exitosamente", "tipo_usuario": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el tipo de usuario", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/tipos-usuario/<int:id_tipo_usuario>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_tipo_usuario(id_tipo_usuario):
    item = db.session.get(TipoUsuario, id_tipo_usuario)
    if not item:
        return jsonify({"error": f"No se encontro ningun tipo de usuario con ID {id_tipo_usuario}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("tipos-usuario")
        return jsonify({"mensaje": f"Tipo de usuario con ID {id_tipo_usuario} eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar el tipo de usuario porque tiene usuarios asociados"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 7. TURNO (PK: ID_Turno)
# ============================================================================

@crud_bp.route("/turnos", methods=["GET"])
@cached(ttl=1800, prefix="turnos", public=True)
def listar_turnos():
    items = Turno.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "turnos": res, "datos": res}), 200

@crud_bp.route("/turnos/<int:id_turno>", methods=["GET"])
@cached(ttl=1800, prefix="turnos", public=True)
def obtener_turno(id_turno):
    item = db.session.get(Turno, id_turno)
    if not item:
        return jsonify({"error": f"No se encontro ningun turno con ID {id_turno}"}), 404
    return jsonify({"turno": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/turnos", methods=["POST"])
@solo_bibliotecario()
def crear_turno():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Turno")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Turno' es obligatorio"}), 400
    try:
        nuevo = Turno(Nombre_Turno=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("turnos")
        return jsonify({"mensaje": "Turno creado exitosamente", "turno": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el turno", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/turnos/<int:id_turno>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_turno(id_turno):
    item = db.session.get(Turno, id_turno)
    if not item:
        return jsonify({"error": f"No se encontro ningun turno con ID {id_turno}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Turno" in datos:
        item.Nombre_Turno = str(datos["Nombre_Turno"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("turnos")
        return jsonify({"mensaje": "Turno actualizado exitosamente", "turno": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el turno", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/turnos/<int:id_turno>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_turno(id_turno):
    item = db.session.get(Turno, id_turno)
    if not item:
        return jsonify({"error": f"No se encontro ningun turno con ID {id_turno}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("turnos")
        return jsonify({"mensaje": f"Turno con ID {id_turno} eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar el turno porque tiene bibliotecarios asociados"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 8. ESTADO_RESERVA (PK: ID_Estado_Reserva)
# ============================================================================

@crud_bp.route("/estados-reserva", methods=["GET"])
@cached(ttl=1800, prefix="estados-reserva", public=True)
def listar_estados_reserva():
    items = EstadoReserva.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "estados_reserva": res, "datos": res}), 200

@crud_bp.route("/estados-reserva/<int:id_estado_reserva>", methods=["GET"])
@cached(ttl=1800, prefix="estados-reserva", public=True)
def obtener_estado_reserva(id_estado_reserva):
    item = db.session.get(EstadoReserva, id_estado_reserva)
    if not item:
        return jsonify({"error": f"No se encontro ningun estado de reserva con ID {id_estado_reserva}"}), 404
    return jsonify({"estado_reserva": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/estados-reserva", methods=["POST"])
@solo_bibliotecario()
def crear_estado_reserva():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Estado")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Estado' es obligatorio"}), 400
    try:
        nuevo = EstadoReserva(Nombre_Estado=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("estados-reserva")
        return jsonify({"mensaje": "Estado de reserva creado exitosamente", "estado_reserva": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el estado de reserva", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/estados-reserva/<int:id_estado_reserva>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_estado_reserva(id_estado_reserva):
    item = db.session.get(EstadoReserva, id_estado_reserva)
    if not item:
        return jsonify({"error": f"No se encontro ningun estado de reserva con ID {id_estado_reserva}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Estado" in datos:
        item.Nombre_Estado = str(datos["Nombre_Estado"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("estados-reserva")
        return jsonify({"mensaje": "Estado de reserva actualizado exitosamente", "estado_reserva": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el estado de reserva", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/estados-reserva/<int:id_estado_reserva>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_estado_reserva(id_estado_reserva):
    item = db.session.get(EstadoReserva, id_estado_reserva)
    if not item:
        return jsonify({"error": f"No se encontro ningun estado de reserva con ID {id_estado_reserva}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("estados-reserva")
        return jsonify({"mensaje": f"Estado de reserva con ID {id_estado_reserva} eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar el estado de reserva porque tiene reservas asociadas"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 9. ESTADO_PRESTAMO (PK: ID_Estado_Prestamo)
# ============================================================================

@crud_bp.route("/estados-prestamo", methods=["GET"])
@cached(ttl=1800, prefix="estados-prestamo", public=True)
def listar_estados_prestamo():
    items = EstadoPrestamo.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "estados_prestamo": res, "datos": res}), 200

@crud_bp.route("/estados-prestamo/<int:id_estado_prestamo>", methods=["GET"])
@cached(ttl=1800, prefix="estados-prestamo", public=True)
def obtener_estado_prestamo(id_estado_prestamo):
    item = db.session.get(EstadoPrestamo, id_estado_prestamo)
    if not item:
        return jsonify({"error": f"No se encontro ningun estado de prestamo con ID {id_estado_prestamo}"}), 404
    return jsonify({"estado_prestamo": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/estados-prestamo", methods=["POST"])
@solo_bibliotecario()
def crear_estado_prestamo():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Estado")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Estado' es obligatorio"}), 400
    try:
        nuevo = EstadoPrestamo(Nombre_Estado=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("estados-prestamo")
        return jsonify({"mensaje": "Estado de prestamo creado exitosamente", "estado_prestamo": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el estado de prestamo", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/estados-prestamo/<int:id_estado_prestamo>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_estado_prestamo(id_estado_prestamo):
    item = db.session.get(EstadoPrestamo, id_estado_prestamo)
    if not item:
        return jsonify({"error": f"No se encontro ningun estado de prestamo con ID {id_estado_prestamo}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Estado" in datos:
        item.Nombre_Estado = str(datos["Nombre_Estado"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("estados-prestamo")
        return jsonify({"mensaje": "Estado de prestamo actualizado exitosamente", "estado_prestamo": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el estado de prestamo", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/estados-prestamo/<int:id_estado_prestamo>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_estado_prestamo(id_estado_prestamo):
    item = db.session.get(EstadoPrestamo, id_estado_prestamo)
    if not item:
        return jsonify({"error": f"No se encontro ningun estado de prestamo con ID {id_estado_prestamo}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("estados-prestamo")
        return jsonify({"mensaje": f"Estado de prestamo con ID {id_estado_prestamo} eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar el estado de prestamo porque tiene prestamos asociados"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 10. CIUDAD (PK: ID_Ciudad)
# ============================================================================

@crud_bp.route("/ciudades", methods=["GET"])
@cached(ttl=1800, prefix="ciudades", public=True)
def listar_ciudades():
    items = Ciudad.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "ciudades": res, "datos": res}), 200

@crud_bp.route("/ciudades/<int:id_ciudad>", methods=["GET"])
@cached(ttl=1800, prefix="ciudades", public=True)
def obtener_ciudad(id_ciudad):
    item = db.session.get(Ciudad, id_ciudad)
    if not item:
        return jsonify({"error": f"No se encontro ninguna ciudad con ID {id_ciudad}"}), 404
    return jsonify({"ciudad": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/ciudades", methods=["POST"])
@solo_bibliotecario()
def crear_ciudad():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Ciudad")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Ciudad' es obligatorio"}), 400
    try:
        nuevo = Ciudad(Nombre_Ciudad=str(nombre).strip())
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("ciudades")
        return jsonify({"mensaje": "Ciudad creada exitosamente", "ciudad": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear la ciudad", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/ciudades/<int:id_ciudad>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_ciudad(id_ciudad):
    item = db.session.get(Ciudad, id_ciudad)
    if not item:
        return jsonify({"error": f"No se encontro ninguna ciudad con ID {id_ciudad}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Ciudad" in datos:
        item.Nombre_Ciudad = str(datos["Nombre_Ciudad"]).strip()
    try:
        db.session.commit()
        cache.delete_pattern("ciudades")
        return jsonify({"mensaje": "Ciudad actualizada exitosamente", "ciudad": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar la ciudad", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/ciudades/<int:id_ciudad>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_ciudad(id_ciudad):
    item = db.session.get(Ciudad, id_ciudad)
    if not item:
        return jsonify({"error": f"No se encontro ninguna ciudad con ID {id_ciudad}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("ciudades")
        return jsonify({"mensaje": f"Ciudad con ID {id_ciudad} eliminada exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar la ciudad porque tiene direcciones asociadas"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 11. CATEGORIA (PK: ID_Categoria)
# ============================================================================

@crud_bp.route("/categorias", methods=["GET"])
@cached(ttl=1800, prefix="categorias", public=True)
def listar_categorias():
    items = Categoria.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "categorias": res, "datos": res}), 200

@crud_bp.route("/categorias/<int:id_categoria>", methods=["GET"])
@cached(ttl=1800, prefix="categorias", public=True)
def obtener_categoria(id_categoria):
    item = db.session.get(Categoria, id_categoria)
    if not item:
        return jsonify({"error": f"No se encontro ninguna categoria con ID {id_categoria}"}), 404
    return jsonify({"categoria": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/categorias", methods=["POST"])
@solo_bibliotecario()
def crear_categoria():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Categoria")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Categoria' es obligatorio"}), 400
    try:
        nuevo = Categoria(
            Nombre_Categoria=str(nombre).strip(),
            Nivel=datos.get("Nivel")
        )
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("categorias")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": "Categoria creada exitosamente", "categoria": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear la categoria", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/categorias/<int:id_categoria>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_categoria(id_categoria):
    item = db.session.get(Categoria, id_categoria)
    if not item:
        return jsonify({"error": f"No se encontro ninguna categoria con ID {id_categoria}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Categoria" in datos:
        item.Nombre_Categoria = str(datos["Nombre_Categoria"]).strip()
    if "Nivel" in datos:
        item.Nivel = datos["Nivel"]
    try:
        db.session.commit()
        cache.delete_pattern("categorias")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": "Categoria actualizada exitosamente", "categoria": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar la categoria", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/categorias/<int:id_categoria>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_categoria(id_categoria):
    item = db.session.get(Categoria, id_categoria)
    if not item:
        return jsonify({"error": f"No se encontro ninguna categoria con ID {id_categoria}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("categorias")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": f"Categoria con ID {id_categoria} eliminada exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar la categoria porque tiene libros asociados"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 12. AUTOR (PK: ID_Autor)
# ============================================================================

@crud_bp.route("/autores", methods=["GET"])
@cached(ttl=1800, prefix="autores", public=True)
def listar_autores():
    items = Autor.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "autores": res, "datos": res}), 200

@crud_bp.route("/autores/<int:id_autor>", methods=["GET"])
@cached(ttl=1800, prefix="autores", public=True)
def obtener_autor(id_autor):
    item = db.session.get(Autor, id_autor)
    if not item:
        return jsonify({"error": f"No se encontro ningun autor con ID {id_autor}"}), 404
    return jsonify({"autor": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/autores", methods=["POST"])
@solo_bibliotecario()
def crear_autor():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("Nombre_Autor")
    if not nombre or not str(nombre).strip():
        return jsonify({"error": "El campo 'Nombre_Autor' es obligatorio"}), 400
    try:
        nuevo = Autor(
            Nombre_Autor=str(nombre).strip(),
            Bibliografia=datos.get("Bibliografia"),
            ID_Pais=datos.get("ID_Pais")
        )
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("autores")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": "Autor creado exitosamente", "autor": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el autor", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/autores/<int:id_autor>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_autor(id_autor):
    item = db.session.get(Autor, id_autor)
    if not item:
        return jsonify({"error": f"No se encontro ningun autor con ID {id_autor}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Autor" in datos:
        item.Nombre_Autor = str(datos["Nombre_Autor"]).strip()
    if "Bibliografia" in datos:
        item.Bibliografia = datos["Bibliografia"]
    if "ID_Pais" in datos:
        item.ID_Pais = datos["ID_Pais"]
    try:
        db.session.commit()
        cache.delete_pattern("autores")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": "Autor actualizado exitosamente", "autor": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el autor", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/autores/<int:id_autor>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_autor(id_autor):
    item = db.session.get(Autor, id_autor)
    if not item:
        return jsonify({"error": f"No se encontro ningun autor con ID {id_autor}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("autores")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": f"Autor con ID {id_autor} eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "No se puede eliminar el autor porque tiene libros asociados"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 13. BIBLIOTECARIO (PK: Codigo_Bibliotecario)
# ============================================================================

@crud_bp.route("/bibliotecarios", methods=["GET"])
@solo_bibliotecario()
@no_cache(private=True)
def listar_bibliotecarios():
    items = Bibliotecario.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "bibliotecarios": res, "datos": res}), 200

@crud_bp.route("/bibliotecarios/<string:codigo_bibliotecario>", methods=["GET"])
@solo_bibliotecario()
@no_cache(private=True)
def obtener_bibliotecario(codigo_bibliotecario):
    item = db.session.get(Bibliotecario, codigo_bibliotecario)
    if not item:
        return jsonify({"error": f"No se encontro ningun bibliotecario con codigo '{codigo_bibliotecario}'"}), 404
    return jsonify({"bibliotecario": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/bibliotecarios", methods=["POST"])
@solo_bibliotecario()
def crear_bibliotecario():
    datos = request.get_json(silent=True) or {}
    codigo = datos.get("Codigo_Bibliotecario")
    nombre = datos.get("Nombre_Bibliotecario")
    email = datos.get("Email_Bibliotecario")
    password = datos.get("Password") or datos.get("Password_Hash")

    if not codigo or not nombre or not email or not password:
        return jsonify({
            "error": "Faltan campos obligatorios",
            "detalle": "Codigo_Bibliotecario, Nombre_Bibliotecario, Email_Bibliotecario y Password son requeridos"
        }), 400

    if db.session.get(Bibliotecario, codigo):
        return jsonify({"error": f"Ya existe un bibliotecario con el codigo '{codigo}'"}), 400
    if Bibliotecario.query.filter_by(Email_Bibliotecario=email).first():
        return jsonify({"error": f"Ya existe un bibliotecario con el correo '{email}'"}), 400

    try:
        nuevo = Bibliotecario(
            Codigo_Bibliotecario=str(codigo).strip(),
            Nombre_Bibliotecario=str(nombre).strip(),
            Email_Bibliotecario=str(email).strip(),
            Activo=datos.get("Activo", True),
            ID_Turno=datos.get("ID_Turno")
        )
        nuevo.set_password(str(password))
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({
            "mensaje": "Bibliotecario creado exitosamente",
            "bibliotecario": nuevo.to_dict(),
            "dato": nuevo.to_dict()
        }), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el bibliotecario", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/bibliotecarios/<string:codigo_bibliotecario>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_bibliotecario(codigo_bibliotecario):
    item = db.session.get(Bibliotecario, codigo_bibliotecario)
    if not item:
        return jsonify({"error": f"No se encontro ningun bibliotecario con codigo '{codigo_bibliotecario}'"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Bibliotecario" in datos:
        item.Nombre_Bibliotecario = str(datos["Nombre_Bibliotecario"]).strip()
    if "Email_Bibliotecario" in datos:
        item.Email_Bibliotecario = str(datos["Email_Bibliotecario"]).strip()
    if "Activo" in datos:
        item.Activo = bool(datos["Activo"])
    if "ID_Turno" in datos:
        item.ID_Turno = datos["ID_Turno"]
    if "Password" in datos and datos["Password"]:
        item.set_password(str(datos["Password"]))
    try:
        db.session.commit()
        return jsonify({
            "mensaje": "Bibliotecario actualizado exitosamente",
            "bibliotecario": item.to_dict(),
            "dato": item.to_dict()
        }), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el bibliotecario", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/bibliotecarios/<string:codigo_bibliotecario>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_bibliotecario(codigo_bibliotecario):
    item = db.session.get(Bibliotecario, codigo_bibliotecario)
    if not item:
        return jsonify({"error": f"No se encontro ningun bibliotecario con codigo '{codigo_bibliotecario}'"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"mensaje": f"Bibliotecario '{codigo_bibliotecario}' eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "No se puede eliminar el bibliotecario porque tiene registros asociados (libros, prestamos o reservas)"
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 14. LIBRO (PK: Codigo_Libro)
# ============================================================================

@crud_bp.route("/libros", methods=["GET"])
@cached(ttl=300, prefix="libros", public=True)
def listar_libros():
    """Consulta y busqueda de catalogo de libros con cache (Cache-Aside, TTL 5 min)"""
    query = Libro.query
    titulo = request.args.get("titulo")
    if titulo:
        query = query.filter(Libro.Titulo_Libro.ilike(f"%{titulo.strip()}%"))
    isbn = request.args.get("isbn")
    if isbn:
        query = query.filter(Libro.Isbn_Libro == isbn.strip())
    id_editorial = request.args.get("id_editorial")
    if id_editorial:
        query = query.filter(Libro.ID_Editorial == id_editorial)
    id_idioma = request.args.get("id_idioma")
    if id_idioma:
        query = query.filter(Libro.ID_Idioma == id_idioma)
    
    items = query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "libros": res, "datos": res}), 200

@crud_bp.route("/libros/<string:codigo_libro>", methods=["GET"])
@cached(ttl=300, prefix="libros", public=True)
def obtener_libro(codigo_libro):
    """Consulta individual de un libro con cache (TTL 5 min)"""
    item = db.session.get(Libro, codigo_libro)
    if not item:
        return jsonify({"error": f"No se encontro ningun libro con codigo '{codigo_libro}'"}), 404
    return jsonify({"libro": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/libros/<string:codigo_libro>/disponibilidad", methods=["GET"])
@cached(ttl=10, prefix="disponibilidad", public=True)
def consultar_disponibilidad_libro(codigo_libro):
    """
    Consulta la disponibilidad de ejemplar en tiempo real con TTL corto (10s)
    para evitar inconsistencias en prestamos y reservas concurrentes.
    """
    item = db.session.get(Libro, codigo_libro)
    if not item:
        return jsonify({"error": f"No se encontro ningun libro con codigo '{codigo_libro}'"}), 404
    
    # Comprobar si existe un prestamo activo sin fecha de devolucion real
    prestamo_activo = Prestamo.query.filter(
        Prestamo.Codigo_Libro == codigo_libro,
        Prestamo.Fecha_Dev_Real.is_(None)
    ).first()
    
    reservas_activas = Reserva.query.filter_by(Codigo_Libro=codigo_libro).count()
    disponible = prestamo_activo is None

    return jsonify({
        "codigo_libro": codigo_libro,
        "titulo": item.Titulo_Libro,
        "disponible": disponible,
        "prestamo_activo": prestamo_activo.to_dict() if prestamo_activo else None,
        "total_reservas_en_cola": reservas_activas
    }), 200

@crud_bp.route("/libros", methods=["POST"])
@solo_bibliotecario()
def crear_libro():
    datos = request.get_json(silent=True) or {}
    codigo = datos.get("Codigo_Libro")
    titulo = datos.get("Titulo_Libro")

    if not codigo or not titulo:
        return jsonify({
            "error": "Faltan campos obligatorios",
            "detalle": "Codigo_Libro y Titulo_Libro son obligatorios"
        }), 400

    if db.session.get(Libro, codigo):
        return jsonify({"error": f"Ya existe un libro con el codigo '{codigo}'"}), 400

    try:
        nuevo = Libro(
            Codigo_Libro=str(codigo).strip(),
            Titulo_Libro=str(titulo).strip(),
            Isbn_Libro=datos.get("Isbn_Libro"),
            Edicion=datos.get("Edicion"),
            Anio_Publicacion=datos.get("Anio_Publicacion"),
            ID_Editorial=datos.get("ID_Editorial"),
            ID_Idioma=datos.get("ID_Idioma"),
            ID_Estado_Fisico=datos.get("ID_Estado_Fisico"),
            Codigo_Bibliotecario=datos.get("Codigo_Bibliotecario")
        )
        db.session.add(nuevo)

        # Relacionar autores si se envian IDs
        if "autores" in datos and isinstance(datos["autores"], list):
            for autor_id in datos["autores"]:
                a = db.session.get(Autor, autor_id)
                if a:
                    nuevo.autores.append(a)

        # Relacionar categorias si se envian IDs
        if "categorias" in datos and isinstance(datos["categorias"], list):
            for cat_id in datos["categorias"]:
                c = db.session.get(Categoria, cat_id)
                if c:
                    nuevo.categorias.append(c)

        db.session.commit()
        cache.delete_pattern("libros")
        cache.delete_pattern("disponibilidad")
        return jsonify({"mensaje": "Libro creado exitosamente", "libro": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el libro", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/libros/<string:codigo_libro>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_libro(codigo_libro):
    item = db.session.get(Libro, codigo_libro)
    if not item:
        return jsonify({"error": f"No se encontro ningun libro con codigo '{codigo_libro}'"}), 404
    datos = request.get_json(silent=True) or {}
    if "Titulo_Libro" in datos:
        item.Titulo_Libro = str(datos["Titulo_Libro"]).strip()
    if "Isbn_Libro" in datos:
        item.Isbn_Libro = datos["Isbn_Libro"]
    if "Edicion" in datos:
        item.Edicion = datos["Edicion"]
    if "Anio_Publicacion" in datos:
        item.Anio_Publicacion = datos["Anio_Publicacion"]
    if "ID_Editorial" in datos:
        item.ID_Editorial = datos["ID_Editorial"]
    if "ID_Idioma" in datos:
        item.ID_Idioma = datos["ID_Idioma"]
    if "ID_Estado_Fisico" in datos:
        item.ID_Estado_Fisico = datos["ID_Estado_Fisico"]
    if "Codigo_Bibliotecario" in datos:
        item.Codigo_Bibliotecario = datos["Codigo_Bibliotecario"]

    # Sincronizar autores si se envia la lista
    if "autores" in datos and isinstance(datos["autores"], list):
        item.autores = []
        for autor_id in datos["autores"]:
            a = db.session.get(Autor, autor_id)
            if a:
                item.autores.append(a)

    # Sincronizar categorias si se envia la lista
    if "categorias" in datos and isinstance(datos["categorias"], list):
        item.categorias = []
        for cat_id in datos["categorias"]:
            c = db.session.get(Categoria, cat_id)
            if c:
                item.categorias.append(c)

    try:
        db.session.commit()
        cache.delete_pattern("libros")
        cache.delete_pattern("disponibilidad")
        return jsonify({"mensaje": "Libro actualizado exitosamente", "libro": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el libro", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/libros/<string:codigo_libro>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_libro(codigo_libro):
    item = db.session.get(Libro, codigo_libro)
    if not item:
        return jsonify({"error": f"No se encontro ningun libro con codigo '{codigo_libro}'"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("libros")
        cache.delete_pattern("disponibilidad")
        return jsonify({"mensaje": f"Libro '{codigo_libro}' eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "No se puede eliminar el libro porque tiene registros asociados (prestamos o reservas)"
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 15. USUARIO (PK: Codigo_Usuario)
# ============================================================================

@crud_bp.route("/usuarios", methods=["GET"])
@solo_bibliotecario()
@no_cache(private=True)
def listar_usuarios():
    items = Usuario.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "usuarios": res, "datos": res}), 200

@crud_bp.route("/usuarios/<string:codigo_usuario>", methods=["GET"])
@solo_autenticado()
@no_cache(private=True)
def obtener_usuario(codigo_usuario):
    if not puede_gestionar_usuario(codigo_usuario):
        return jsonify({
            "error": "Acceso denegado (403)",
            "mensaje": "No tienes permiso para consultar el perfil de otro usuario"
        }), 403
    item = db.session.get(Usuario, codigo_usuario)
    if not item:
        return jsonify({"error": f"No se encontro ningun usuario con codigo '{codigo_usuario}'"}), 404
    return jsonify({"usuario": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/usuarios", methods=["POST"])
@solo_bibliotecario()
def crear_usuario():
    datos = request.get_json(silent=True) or {}
    codigo = datos.get("Codigo_Usuario")
    nombre = datos.get("Nombre_Usuario")
    email = datos.get("Email_Usuario")
    password = datos.get("Password") or datos.get("Password_Hash") or "123456"

    if not codigo or not nombre or not email:
        return jsonify({
            "error": "Faltan campos obligatorios",
            "detalle": "Codigo_Usuario, Nombre_Usuario y Email_Usuario son requeridos"
        }), 400

    if db.session.get(Usuario, codigo):
        return jsonify({"error": f"Ya existe un usuario con el codigo '{codigo}'"}), 400
    if Usuario.query.filter_by(Email_Usuario=email).first():
        return jsonify({"error": f"Ya existe un usuario con el correo '{email}'"}), 400

    try:
        nuevo = Usuario(
            Codigo_Usuario=str(codigo).strip(),
            Nombre_Usuario=str(nombre).strip(),
            Email_Usuario=str(email).strip(),
            Telefono_Usuario=datos.get("Telefono_Usuario"),
            Prestamos_Activos=datos.get("Prestamos_Activos", 0),
            Limite_Prestamos=datos.get("Limite_Prestamos", 3),
            Activo=datos.get("Activo", True),
            ID_Tipo_Usuario=datos.get("ID_Tipo_Usuario"),
            ID_Facultad=datos.get("ID_Facultad")
        )
        nuevo.set_password(str(password))
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Usuario creado exitosamente", "usuario": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el usuario", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/usuarios/<string:codigo_usuario>", methods=["PUT"])
@solo_autenticado()
def actualizar_usuario(codigo_usuario):
    if not puede_gestionar_usuario(codigo_usuario):
        return jsonify({
            "error": "Acceso denegado (403)",
            "mensaje": "No tienes permiso para modificar a otro usuario"
        }), 403
    item = db.session.get(Usuario, codigo_usuario)
    if not item:
        return jsonify({"error": f"No se encontro ningun usuario con codigo '{codigo_usuario}'"}), 404
    datos = request.get_json(silent=True) or {}
    if "Nombre_Usuario" in datos:
        item.Nombre_Usuario = str(datos["Nombre_Usuario"]).strip()
    if "Email_Usuario" in datos:
        item.Email_Usuario = str(datos["Email_Usuario"]).strip()
    if "Telefono_Usuario" in datos:
        item.Telefono_Usuario = datos["Telefono_Usuario"]
    if "Prestamos_Activos" in datos:
        item.Prestamos_Activos = datos["Prestamos_Activos"]
    if "Limite_Prestamos" in datos:
        item.Limite_Prestamos = datos["Limite_Prestamos"]
    if "Activo" in datos:
        item.Activo = bool(datos["Activo"])
    if "ID_Tipo_Usuario" in datos:
        item.ID_Tipo_Usuario = datos["ID_Tipo_Usuario"]
    if "ID_Facultad" in datos:
        item.ID_Facultad = datos["ID_Facultad"]
    if "Password" in datos and datos["Password"]:
        if len(str(datos["Password"])) < 6:
            return jsonify({"error": "La nueva contrasena debe tener al menos 6 caracteres"}), 400
        item.set_password(str(datos["Password"]))
    try:
        db.session.commit()
        return jsonify({"mensaje": "Usuario actualizado exitosamente", "usuario": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el usuario", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/usuarios/<string:codigo_usuario>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_usuario(codigo_usuario):
    item = db.session.get(Usuario, codigo_usuario)
    if not item:
        return jsonify({"error": f"No se encontro ningun usuario con codigo '{codigo_usuario}'"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"mensaje": f"Usuario '{codigo_usuario}' eliminado exitosamente"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "No se puede eliminar el usuario porque tiene registros asociados (prestamos, reservas o direcciones)"
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 16. DIRECCION (PK: ID_Direccion)
# ============================================================================

@crud_bp.route("/direcciones", methods=["GET"])
@solo_autenticado()
@no_cache(private=True)
def listar_direcciones():
    items = Direccion.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "direcciones": res, "datos": res}), 200

@crud_bp.route("/direcciones/<int:id_direccion>", methods=["GET"])
@solo_autenticado()
@no_cache(private=True)
def obtener_direccion(id_direccion):
    item = db.session.get(Direccion, id_direccion)
    if not item:
        return jsonify({"error": f"No se encontro ninguna direccion con ID {id_direccion}"}), 404
    return jsonify({"direccion": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/direcciones", methods=["POST"])
@solo_autenticado()
def crear_direccion():
    datos = request.get_json(silent=True) or {}
    try:
        nuevo = Direccion(
            Codigo_Usuario=datos.get("Codigo_Usuario"),
            Calle_Avenida=datos.get("Calle_Avenida"),
            Numero=datos.get("Numero"),
            Barrio=datos.get("Barrio"),
            ID_Ciudad=datos.get("ID_Ciudad")
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Direccion creada exitosamente", "direccion": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear la direccion", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/direcciones/<int:id_direccion>", methods=["PUT"])
@solo_autenticado()
def actualizar_direccion(id_direccion):
    item = db.session.get(Direccion, id_direccion)
    if not item:
        return jsonify({"error": f"No se encontro ninguna direccion con ID {id_direccion}"}), 404
    datos = request.get_json(silent=True) or {}
    if "Codigo_Usuario" in datos:
        item.Codigo_Usuario = datos["Codigo_Usuario"]
    if "Calle_Avenida" in datos:
        item.Calle_Avenida = datos["Calle_Avenida"]
    if "Numero" in datos:
        item.Numero = datos["Numero"]
    if "Barrio" in datos:
        item.Barrio = datos["Barrio"]
    if "ID_Ciudad" in datos:
        item.ID_Ciudad = datos["ID_Ciudad"]
    try:
        db.session.commit()
        return jsonify({"mensaje": "Direccion actualizada exitosamente", "direccion": item.to_dict(), "dato": item.to_dict()}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar la direccion", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/direcciones/<int:id_direccion>", methods=["DELETE"])
@solo_autenticado()
def eliminar_direccion(id_direccion):
    item = db.session.get(Direccion, id_direccion)
    if not item:
        return jsonify({"error": f"No se encontro ninguna direccion con ID {id_direccion}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"mensaje": f"Direccion con ID {id_direccion} eliminada exitosamente"}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al eliminar la direccion", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 17. HISTORIAL_UBICACION (PK: ID_Historial)
# ============================================================================

@crud_bp.route("/historial-ubicaciones", methods=["GET"])
@cached(ttl=600, prefix="historial-ubicaciones", public=True)
def listar_historial_ubicaciones():
    items = HistorialUbicacion.query.all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "historial_ubicaciones": res, "datos": res}), 200

@crud_bp.route("/historial-ubicaciones/<int:id_historial>", methods=["GET"])
@cached(ttl=600, prefix="historial-ubicaciones", public=True)
def obtener_historial_ubicacion(id_historial):
    item = db.session.get(HistorialUbicacion, id_historial)
    if not item:
        return jsonify({"error": f"No se encontro ningun registro de historial de ubicacion con ID {id_historial}"}), 404
    return jsonify({"historial_ubicacion": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/historial-ubicaciones", methods=["POST"])
@solo_bibliotecario()
def crear_historial_ubicacion():
    datos = request.get_json(silent=True) or {}
    try:
        fecha = parse_date(datos.get("Fecha_Asignacion")) or date.today()
        nuevo = HistorialUbicacion(
            Codigo_Libro=datos.get("Codigo_Libro"),
            Estante_Ubicacion=datos.get("Estante_Ubicacion"),
            Fecha_Asignacion=fecha
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({
            "mensaje": "Historial de ubicacion creado exitosamente",
            "historial_ubicacion": nuevo.to_dict(),
            "dato": nuevo.to_dict()
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el historial de ubicacion", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/historial-ubicaciones/<int:id_historial>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_historial_ubicacion(id_historial):
    item = db.session.get(HistorialUbicacion, id_historial)
    if not item:
        return jsonify({"error": f"No se encontro ningun registro de historial de ubicacion con ID {id_historial}"}), 404
    datos = request.get_json(silent=True) or {}
    try:
        if "Codigo_Libro" in datos:
            item.Codigo_Libro = datos["Codigo_Libro"]
        if "Estante_Ubicacion" in datos:
            item.Estante_Ubicacion = datos["Estante_Ubicacion"]
        if "Fecha_Asignacion" in datos:
            item.Fecha_Asignacion = parse_date(datos["Fecha_Asignacion"])
        db.session.commit()
        return jsonify({
            "mensaje": "Historial de ubicacion actualizado exitosamente",
            "historial_ubicacion": item.to_dict(),
            "dato": item.to_dict()
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el historial de ubicacion", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/historial-ubicaciones/<int:id_historial>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_historial_ubicacion(id_historial):
    item = db.session.get(HistorialUbicacion, id_historial)
    if not item:
        return jsonify({"error": f"No se encontro ningun registro de historial de ubicacion con ID {id_historial}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("historial-ubicaciones")
        return jsonify({"mensaje": f"Historial de ubicacion con ID {id_historial} eliminado exitosamente"}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al eliminar el historial", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 18. RESERVA (PK: Codigo_Reserva)
# ============================================================================

@crud_bp.route("/reservas", methods=["GET"])
@solo_autenticado()
@no_cache(private=True)
def listar_reservas():
    if es_bibliotecario():
        items = Reserva.query.all()
    else:
        identidad = get_jwt_identity()
        items = Reserva.query.filter_by(Codigo_Usuario=identidad).all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "reservas": res, "datos": res}), 200

@crud_bp.route("/reservas/<int:codigo_reserva>", methods=["GET"])
@solo_autenticado()
@no_cache(private=True)
def obtener_reserva(codigo_reserva):
    item = db.session.get(Reserva, codigo_reserva)
    if not item:
        return jsonify({"error": f"No se encontro ninguna reserva con codigo {codigo_reserva}"}), 404
    if not es_bibliotecario() and item.Codigo_Usuario != get_jwt_identity():
        return jsonify({"error": "Acceso denegado (403)", "mensaje": "No tienes permiso para ver reservas de otro usuario"}), 403
    return jsonify({"reserva": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/reservas", methods=["POST"])
@solo_autenticado()
def crear_reserva():
    datos = request.get_json(silent=True) or {}
    try:
        fecha = parse_datetime(datos.get("Fecha_Reserva")) if "Fecha_Reserva" in datos else datetime.now()
        nuevo = Reserva(
            Codigo_Usuario=datos.get("Codigo_Usuario"),
            Codigo_Libro=datos.get("Codigo_Libro"),
            Fecha_Reserva=fecha,
            Posicion_Cola_Reserva=datos.get("Posicion_Cola_Reserva"),
            ID_Estado_Reserva=datos.get("ID_Estado_Reserva"),
            Codigo_Bibliotecario=datos.get("Codigo_Bibliotecario")
        )
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("disponibilidad")
        return jsonify({"mensaje": "Reserva creada exitosamente", "reserva": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear la reserva", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/reservas/<int:codigo_reserva>", methods=["PUT"])
@solo_autenticado()
def actualizar_reserva(codigo_reserva):
    item = db.session.get(Reserva, codigo_reserva)
    if not item:
        return jsonify({"error": f"No se encontro ninguna reserva con codigo {codigo_reserva}"}), 404
    datos = request.get_json(silent=True) or {}
    try:
        if "Codigo_Usuario" in datos:
            item.Codigo_Usuario = datos["Codigo_Usuario"]
        if "Codigo_Libro" in datos:
            item.Codigo_Libro = datos["Codigo_Libro"]
        if "Fecha_Reserva" in datos:
            item.Fecha_Reserva = parse_datetime(datos["Fecha_Reserva"])
        if "Posicion_Cola_Reserva" in datos:
            item.Posicion_Cola_Reserva = datos["Posicion_Cola_Reserva"]
        if "ID_Estado_Reserva" in datos:
            item.ID_Estado_Reserva = datos["ID_Estado_Reserva"]
        if "Codigo_Bibliotecario" in datos:
            item.Codigo_Bibliotecario = datos["Codigo_Bibliotecario"]
        db.session.commit()
        cache.delete_pattern("disponibilidad")
        return jsonify({"mensaje": "Reserva actualizada exitosamente", "reserva": item.to_dict(), "dato": item.to_dict()}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar la reserva", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/reservas/<int:codigo_reserva>", methods=["DELETE"])
@solo_autenticado()
def eliminar_reserva(codigo_reserva):
    item = db.session.get(Reserva, codigo_reserva)
    if not item:
        return jsonify({"error": f"No se encontro ninguna reserva con codigo {codigo_reserva}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("disponibilidad")
        return jsonify({"mensaje": f"Reserva con codigo {codigo_reserva} eliminada exitosamente"}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al eliminar la reserva", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ============================================================================
# 19. PRESTAMO (PK: ID_Prestamo)
# ============================================================================

@crud_bp.route("/prestamos", methods=["GET"])
@solo_autenticado()
@no_cache(private=True)
def listar_prestamos():
    if es_bibliotecario():
        items = Prestamo.query.all()
    else:
        identidad = get_jwt_identity()
        items = Prestamo.query.filter_by(Codigo_Usuario=identidad).all()
    res = [item.to_dict() for item in items]
    return jsonify({"total": len(res), "prestamos": res, "datos": res}), 200

@crud_bp.route("/prestamos/<int:id_prestamo>", methods=["GET"])
@solo_autenticado()
@no_cache(private=True)
def obtener_prestamo(id_prestamo):
    item = db.session.get(Prestamo, id_prestamo)
    if not item:
        return jsonify({"error": f"No se encontro ningun prestamo con ID {id_prestamo}"}), 404
    if not es_bibliotecario() and item.Codigo_Usuario != get_jwt_identity():
        return jsonify({"error": "Acceso denegado (403)", "mensaje": "No tienes permiso para ver prestamos de otro usuario"}), 403
    return jsonify({"prestamo": item.to_dict(), "dato": item.to_dict()}), 200

@crud_bp.route("/prestamos", methods=["POST"])
@solo_bibliotecario()
def crear_prestamo():
    datos = request.get_json(silent=True) or {}
    try:
        fecha_p = parse_date(datos.get("Fecha_Prestamo")) or date.today()
        fecha_prev = parse_date(datos.get("Fecha_Dev_Prevista")) or (fecha_p + timedelta(days=14))
        fecha_real = parse_date(datos.get("Fecha_Dev_Real")) if datos.get("Fecha_Dev_Real") else None

        nuevo = Prestamo(
            Codigo_Usuario=datos.get("Codigo_Usuario"),
            Codigo_Libro=datos.get("Codigo_Libro"),
            Codigo_Bibliotecario=datos.get("Codigo_Bibliotecario"),
            Fecha_Prestamo=fecha_p,
            Fecha_Dev_Prevista=fecha_prev,
            Fecha_Dev_Real=fecha_real,
            Dia_Retraso=datos.get("Dia_Retraso", 0),
            Multa_Calculada=datos.get("Multa_Calculada", 0.00),
            Numero_Renovaciones=datos.get("Numero_Renovaciones", 0),
            ID_Estado_Prestamo=datos.get("ID_Estado_Prestamo")
        )
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_pattern("disponibilidad")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": "Prestamo creado exitosamente", "prestamo": nuevo.to_dict(), "dato": nuevo.to_dict()}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al crear el prestamo", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/prestamos/<int:id_prestamo>", methods=["PUT"])
@solo_bibliotecario()
def actualizar_prestamo(id_prestamo):
    item = db.session.get(Prestamo, id_prestamo)
    if not item:
        return jsonify({"error": f"No se encontro ningun prestamo con ID {id_prestamo}"}), 404
    datos = request.get_json(silent=True) or {}
    try:
        if "Codigo_Usuario" in datos:
            item.Codigo_Usuario = datos["Codigo_Usuario"]
        if "Codigo_Libro" in datos:
            item.Codigo_Libro = datos["Codigo_Libro"]
        if "Codigo_Bibliotecario" in datos:
            item.Codigo_Bibliotecario = datos["Codigo_Bibliotecario"]
        if "Fecha_Prestamo" in datos:
            item.Fecha_Prestamo = parse_date(datos["Fecha_Prestamo"])
        if "Fecha_Dev_Prevista" in datos:
            item.Fecha_Dev_Prevista = parse_date(datos["Fecha_Dev_Prevista"])
        if "Fecha_Dev_Real" in datos:
            item.Fecha_Dev_Real = parse_date(datos["Fecha_Dev_Real"]) if datos["Fecha_Dev_Real"] else None
        if "Dia_Retraso" in datos:
            item.Dia_Retraso = datos["Dia_Retraso"]
        if "Multa_Calculada" in datos:
            item.Multa_Calculada = datos["Multa_Calculada"]
        if "Numero_Renovaciones" in datos:
            item.Numero_Renovaciones = datos["Numero_Renovaciones"]
        if "ID_Estado_Prestamo" in datos:
            item.ID_Estado_Prestamo = datos["ID_Estado_Prestamo"]
        db.session.commit()
        cache.delete_pattern("disponibilidad")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": "Prestamo actualizado exitosamente", "prestamo": item.to_dict(), "dato": item.to_dict()}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al actualizar el prestamo", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@crud_bp.route("/prestamos/<int:id_prestamo>", methods=["DELETE"])
@solo_bibliotecario()
def eliminar_prestamo(id_prestamo):
    item = db.session.get(Prestamo, id_prestamo)
    if not item:
        return jsonify({"error": f"No se encontro ningun prestamo con ID {id_prestamo}"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete_pattern("disponibilidad")
        cache.delete_pattern("libros")
        return jsonify({"mensaje": f"Prestamo con ID {id_prestamo} eliminado exitosamente"}), 200
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Error de integridad al eliminar el prestamo", "detalle": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
