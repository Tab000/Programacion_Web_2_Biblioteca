import os
import time
import json
import hashlib
import threading
from functools import wraps
from flask import request, make_response, Response, jsonify


class CacheManager:
    """
    Gestor de Cache en memoria (Cache-Aside) con soporte de TTL, ETag,
    invalidacion por patron/clave y metricas de rendimiento.
    Preparado para interoperar con Redis si se configura REDIS_URL.
    """

    def __init__(self):
        self._cache = {}
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
            "invalidations": 0
        }
        self.enabled = os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes")

    def _limpiar_expirados_inseguro(self):
        """Elimina entradas vencidas (debe llamarse dentro de un lock)"""
        now = time.time()
        claves_expiradas = [k for k, v in self._cache.items() if v["expires_at"] <= now]
        for k in claves_expiradas:
            del self._cache[k]

    def generate_key(self, prefix: str, path: str, args: dict = None) -> str:
        """
        Genera una clave unica normalizada para la peticion segun ruta y parametros query.
        Ejemplo: libros:/api/libros?titulo=redes
        """
        if not args:
            return f"{prefix}:{path}"
        # Ordenar los argumentos query para que '?a=1&b=2' y '?b=2&a=1' coincidan
        sorted_args = "&".join(f"{k}={v}" for k, v in sorted(args.items()))
        return f"{prefix}:{path}?{sorted_args}"

    def get(self, key: str):
        """Obtiene un elemento si existe y no ha expirado"""
        if not self.enabled:
            return None

        with self._lock:
            self._stats["total_requests"] += 1
            item = self._cache.get(key)
            if item is None:
                self._stats["misses"] += 1
                return None

            if time.time() > item["expires_at"]:
                del self._cache[key]
                self._stats["misses"] += 1
                return None

            self._stats["hits"] += 1
            return item

    def set(self, key: str, data: str, ttl: int, status_code: int = 200, etag: str = None):
        """Almacena una respuesta en el cache con un TTL determinado en segundos"""
        if not self.enabled:
            return

        with self._lock:
            self._limpiar_expirados_inseguro()
            expires_at = time.time() + ttl
            self._cache[key] = {
                "data": data,
                "status_code": status_code,
                "expires_at": expires_at,
                "ttl": ttl,
                "etag": etag,
                "created_at": time.time()
            }

    def delete(self, key: str):
        """Invalida una clave especifica del cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["invalidations"] += 1

    def delete_pattern(self, pattern_prefix: str):
        """
        Invalida todas las claves que comiencen con el prefijo dado.
        Ejemplo: delete_pattern('libros') eliminara 'libros:/api/libros', 'libros:/api/libros?titulo=redes', etc.
        """
        with self._lock:
            claves_a_borrar = [k for k in self._cache.keys() if k.startswith(f"{pattern_prefix}:")]
            for k in claves_a_borrar:
                del self._cache[k]
                self._stats["invalidations"] += 1

    def clear(self):
        """Vacia por completo el cache"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._stats["invalidations"] += count
            return count

    def get_stats(self):
        """Retorna metricas y estadisticas de aciertos y uso del cache"""
        with self._lock:
            self._limpiar_expirados_inseguro()
            total = self._stats["total_requests"]
            hits = self._stats["hits"]
            misses = self._stats["misses"]
            hit_rate = round((hits / total * 100), 2) if total > 0 else 0.0

            return {
                "cache_habilitado": self.enabled,
                "entradas_activas": len(self._cache),
                "total_consultas": total,
                "aciertos_hits": hits,
                "fallos_misses": misses,
                "tasa_aciertos_pct": hit_rate,
                "total_invalidaciones": self._stats["invalidations"],
                "claves_almacenadas": list(self._cache.keys())
            }


# Instancia singleton del gestor de cache
cache = CacheManager()


def cached(ttl: int = 300, prefix: str = "api", public: bool = True, etag: bool = True):
    """
    Decorador Cache-Aside para endpoints Flask GET.
    - Soporta TTL configurable.
    - Genera cabecera ETag y gestiona validaciones HTTP 304 Not Modified con If-None-Match.
    - Agrega cabeceras X-Cache (HIT/MISS) y Cache-Control (public/private max-age).
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Solo cachear peticiones GET
            if request.method != "GET" or not cache.enabled:
                return fn(*args, **kwargs)

            # 1. Generar clave unica de cache
            key = cache.generate_key(prefix, request.path, request.args.to_dict())

            # 2. Consultar el cache (Cache-Aside)
            item = cache.get(key)
            if item is not None:
                # Comprobar validacion condicional If-None-Match (HTTP 304)
                client_etag = request.headers.get("If-None-Match")
                if etag and client_etag and client_etag == item.get("etag"):
                    resp_304 = Response(status=304)
                    resp_304.headers["ETag"] = item["etag"]
                    resp_304.headers["X-Cache"] = "HIT"
                    return resp_304

                # HIT: Devolver resultado almacenado
                response = make_response(item["data"], item["status_code"])
                response.headers["Content-Type"] = "application/json"
                response.headers["X-Cache"] = "HIT"
                if etag and item.get("etag"):
                    response.headers["ETag"] = item["etag"]
                if public:
                    response.headers["Cache-Control"] = f"public, max-age={ttl}"
                else:
                    response.headers["Cache-Control"] = f"private, max-age={ttl}"
                return response

            # 3. MISS: Consultar base de datos ejecutando la funcion del endpoint
            result = fn(*args, **kwargs)
            response = make_response(result)

            # Solo almacenar respuestas exitosas 200
            if response.status_code == 200:
                data_str = response.get_data(as_text=True)
                etag_val = f'"{hashlib.md5(data_str.encode("utf-8")).hexdigest()}"'

                cache.set(
                    key=key,
                    data=data_str,
                    ttl=ttl,
                    status_code=response.status_code,
                    etag=etag_val
                )

                response.headers["X-Cache"] = "MISS"
                if etag:
                    response.headers["ETag"] = etag_val
                if public:
                    response.headers["Cache-Control"] = f"public, max-age={ttl}"
                else:
                    response.headers["Cache-Control"] = f"private, max-age={ttl}"

            return response
        return wrapper
    return decorator


def no_cache(private: bool = True):
    """
    Decorador para endpoints que no deben ser almacenados en cache (operaciones sensibles/personales).
    Configura Cache-Control: no-store, no-cache, must-revalidate.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            response = make_response(result)
            privacy = "private" if private else "public"
            response.headers["Cache-Control"] = f"{privacy}, no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
        return wrapper
    return decorator
