import unittest
from app import app
from cache_manager import cache
from flask_jwt_extended import create_access_token
from modelo import db, Libro, Editorial, Idioma, EstadoFisico, Bibliotecario, Usuario, TipoUsuario, Facultad, Prestamo


class TestSistemaCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

        with app.app_context():
            # Crear bibliotecario para operaciones protegidas
            biblio = db.session.get(Bibliotecario, "BIB_CACHE_01")
            if not biblio:
                biblio = Bibliotecario(
                    Codigo_Bibliotecario="BIB_CACHE_01",
                    Nombre_Bibliotecario="Bibliotecario Cache",
                    Email_Bibliotecario="biblio.cache@test.com",
                    Activo=True
                )
                biblio.set_password("AdminCache123")
                db.session.add(biblio)

            # Crear libro de prueba
            libro = db.session.get(Libro, "LIB_CACHE_01")
            if not libro:
                libro = Libro(
                    Codigo_Libro="LIB_CACHE_01",
                    Titulo_Libro="Sistemas Distribuidos y Cache",
                    Isbn_Libro="978-0123456789"
                )
                db.session.add(libro)

            db.session.commit()

            # Token de bibliotecario
            token_admin = create_access_token(
                identity="BIB_CACHE_01",
                additional_claims={"rol": "bibliotecario"}
            )
            cls.admin_headers = {"Authorization": f"Bearer {token_admin}"}

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            # Limpiar libro y bibliotecario de prueba
            for cod in ["LIB_CACHE_01", "LIB_CACHE_NUEVO"]:
                l = db.session.get(Libro, cod)
                if l:
                    db.session.delete(l)

            b = db.session.get(Bibliotecario, "BIB_CACHE_01")
            if b:
                db.session.delete(b)

            db.session.commit()

    def setUp(self):
        # Limpiar el cache antes de cada test para aislar mediciones
        cache.clear()

    def test_01_cache_hit_and_miss_lifecycle(self):
        """Primera peticion debe ser MISS, segunda HIT, con cabeceras Cache-Control y ETag"""
        # 1. Peticion 1 -> MISS (consulta BD)
        res1 = self.client.get("/api/libros")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.headers.get("X-Cache"), "MISS")
        self.assertIn("public, max-age=300", res1.headers.get("Cache-Control", ""))
        etag = res1.headers.get("ETag")
        self.assertIsNotNone(etag)

        # 2. Peticion 2 -> HIT (recuperado de memoria)
        res2 = self.client.get("/api/libros")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.headers.get("X-Cache"), "HIT")
        self.assertEqual(res2.headers.get("ETag"), etag)
        self.assertEqual(res1.get_json(), res2.get_json())

    def test_02_etag_conditional_request_304(self):
        """Peticion condicional If-None-Match debe retornar 304 Not Modified sin transferir cuerpo"""
        res1 = self.client.get("/api/libros/LIB_CACHE_01")
        self.assertEqual(res1.status_code, 200)
        etag = res1.headers.get("ETag")

        # Peticion enviando If-None-Match con el mismo ETag
        res_304 = self.client.get("/api/libros/LIB_CACHE_01", headers={"If-None-Match": etag})
        self.assertEqual(res_304.status_code, 304)
        self.assertEqual(res_304.get_data(as_text=True), "")
        self.assertEqual(res_304.headers.get("X-Cache"), "HIT")

    def test_03_busqueda_query_params_independientes(self):
        """Las busquedas con diferentes parametros query deben almacenarse en claves distintas"""
        res1 = self.client.get("/api/libros?titulo=Distribuidos")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.headers.get("X-Cache"), "MISS")

        res2 = self.client.get("/api/libros?titulo=Redes")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.headers.get("X-Cache"), "MISS")

        # Re-consultar la primera busqueda -> debe ser HIT
        res1_hit = self.client.get("/api/libros?titulo=Distribuidos")
        self.assertEqual(res1_hit.status_code, 200)
        self.assertEqual(res1_hit.headers.get("X-Cache"), "HIT")

    def test_04_invalidacion_automatica_en_escritura(self):
        """Al crear, modificar o eliminar un libro, el cache de libros debe invalidarse de inmediato"""
        # 1. Calentar cache
        res_init = self.client.get("/api/libros")
        self.assertEqual(res_init.headers.get("X-Cache"), "MISS")
        res_hit = self.client.get("/api/libros")
        self.assertEqual(res_hit.headers.get("X-Cache"), "HIT")

        # 2. Modificar un libro (operacion de escritura)
        res_put = self.client.put(
            "/api/libros/LIB_CACHE_01",
            json={"Titulo_Libro": "Sistemas Distribuidos y Cache (Edicion 2)"},
            headers=self.admin_headers
        )
        self.assertEqual(res_put.status_code, 200)

        # 3. La siguiente consulta debe ser MISS debido a la invalidacion automatica
        res_after = self.client.get("/api/libros")
        self.assertEqual(res_after.headers.get("X-Cache"), "MISS")

    def test_05_disponibilidad_realtime_ttl_corto(self):
        """El endpoint de disponibilidad responde con TTL corto (10s) y datos del estado del ejemplar"""
        res = self.client.get("/api/libros/LIB_CACHE_01/disponibilidad")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("disponible", data)
        self.assertTrue(data["disponible"])
        self.assertIn("max-age=10", res.headers.get("Cache-Control", ""))

    def test_06_rutas_privadas_no_cache(self):
        """Las rutas privadas o de usuario (reservas, prestamos) deben tener directiva no-store"""
        with app.app_context():
            token_usr = create_access_token(
                identity="USR_TEST_TEMP",
                additional_claims={"rol": "usuario"}
            )
        headers = {"Authorization": f"Bearer {token_usr}"}

        res = self.client.get("/api/prestamos", headers=headers)
        self.assertEqual(res.status_code, 200)
        cache_control = res.headers.get("Cache-Control", "")
        self.assertIn("no-store", cache_control)
        self.assertIn("no-cache", cache_control)

    def test_07_endpoints_metricas_y_vaciado_cache(self):
        """GET /api/cache/stats y POST /api/cache/clear gestionan el estado del cache"""
        # Realizar consultas para generar estadisticas
        self.client.get("/api/libros")
        self.client.get("/api/libros")

        stats_res = self.client.get("/api/cache/stats")
        self.assertEqual(stats_res.status_code, 200)
        stats = stats_res.get_json()
        self.assertGreaterEqual(stats["total_consultas"], 2)
        self.assertGreaterEqual(stats["aciertos_hits"], 1)

        # Vaciar cache
        clear_res = self.client.post("/api/cache/clear", headers=self.admin_headers)
        self.assertEqual(clear_res.status_code, 200)
        self.assertEqual(clear_res.get_json()["mensaje"], "Cache del servidor vaciado exitosamente")

        # Verificar que el cache quedó en 0 entradas
        stats2 = self.client.get("/api/cache/stats").get_json()
        self.assertEqual(stats2["entradas_activas"], 0)


if __name__ == "__main__":
    unittest.main()
