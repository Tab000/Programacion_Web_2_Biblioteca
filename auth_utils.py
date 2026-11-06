import os
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity


def seguridad_activa():
    """
    Verifica si la seguridad estricta esta activada en las variables de entorno.
    Por defecto es True. Puede desactivarse configurando JWT_SECURITY_ENFORCED=false.
    """
    enforced = os.getenv("JWT_SECURITY_ENFORCED")
    if enforced is not None:
        return enforced.strip().lower() in ("true", "1", "yes")

    # Retrocompatibilidad con la variable previa si existiera
    req_usr = os.getenv("JWT_REQUIRED_USUARIOS")
    if req_usr is not None:
        return req_usr.strip().lower() in ("true", "1", "yes")

    return True


def requiere_rol(*roles_permitidos):
    """
    Decorador RBAC (Role-Based Access Control).
    1. Exige autenticacion JWT si la seguridad esta activa.
    2. Si se especifican roles_permitidos, comprueba que el claim 'rol' coincida.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not seguridad_activa():
                return fn(*args, **kwargs)

            # Ejecutar validacion JWT estandar
            @jwt_required()
            def jwt_check(*a, **kw):
                if roles_permitidos:
                    claims = get_jwt()
                    rol_actual = claims.get("rol", "usuario")
                    if rol_actual not in roles_permitidos:
                        return jsonify({
                            "error": "Acceso denegado (403)",
                            "mensaje": f"Permisos insuficientes. Requiere rol: {', '.join(roles_permitidos)}. Tu rol actual es '{rol_actual}'."
                        }), 403
                return fn(*a, **kw)

            return jwt_check(*args, **kwargs)
        return wrapper
    return decorator


def solo_bibliotecario():
    """Requiere que el solicitante tenga el rol 'bibliotecario' (o 'admin')"""
    return requiere_rol("bibliotecario", "admin")


def solo_autenticado():
    """Requiere que el solicitante este autenticado con cualquier rol valido"""
    return requiere_rol()


def es_bibliotecario():
    """Retorna True si el usuario autenticado actual tiene rol de bibliotecario o admin"""
    if not seguridad_activa():
        return True
    try:
        claims = get_jwt()
        return claims.get("rol") in ("bibliotecario", "admin")
    except Exception:
        return False


def puede_gestionar_usuario(codigo_usuario):
    """
    Verifica si el usuario autenticado actual tiene permiso sobre un codigo de usuario especifico.
    - Un bibliotecario/admin puede gestionar a cualquier usuario.
    - Un usuario regular solo puede gestionarse a si mismo.
    """
    if not seguridad_activa():
        return True
    if es_bibliotecario():
        return True
    try:
        identidad = get_jwt_identity()
        return str(identidad).strip() == str(codigo_usuario).strip()
    except Exception:
        return False
