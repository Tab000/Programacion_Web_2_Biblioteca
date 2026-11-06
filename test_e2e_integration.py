import unittest
import json
from app import app
from cache_manager import cache
from flask_jwt_extended import create_access_token
from modelo import db, Libro, Usuario, Bibliotecario, Prestamo, Reserva, TipoUsuario, Facultad, Turno


class TestE2EIntegracionBiblioteca(unittest.TestCase):
    """
    Suite de Pruebas de Integracion y Recorridos E2E para la Biblioteca Universitaria.
    Cubre los 4 flujos principales descritos en la estrategia de pruebas automatizadas:
    3.1 Búsqueda y Catálogo
    3.2 Préstamos, Devoluciones y Reservas
    3.3 Inicio de Sesión y Permisos
    3.4 Administración del Catálogo y Contratos OpenAPI
    """

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

        with app.app_context():
            # Datos base de soporte
            facultad = db.session.get(Facultad, 8888)
            if not facultad:
                facultad = Facultad(ID_Facultad=8888, Nombre_Facultad="Ingenieria de Sistemas E2E")
                db.session.add(facultad)

            tipo_u = db.session.get(TipoUsuario, 8888)
            if not tipo_u:
                tipo_u = TipoUsuario(ID_Tipo_Usuario=8888, Nombre_Tipo="Estudiante Regular E2E")
                db.session.add(tipo_u)

            turno = db.session.get(Turno, 8888)
            if not turno:
                turno = Turno(ID_Turno=8888, Nombre_Turno="Turno Completo E2E")
                db.session.add(turno)

            # Bibliotecario administrativo
            biblio = db.session.get(Bibliotecario, "BIB_E2E_01")
            if not biblio:
                biblio = Bibliotecario(
                    Codigo_Bibliotecario="BIB_E2E_01",
                    Nombre_Bibliotecario="Bibliotecario Administrador E2E",
                    Email_Bibliotecario="admin.e2e@universidad.edu.co",
                    ID_Turno=8888,
                    Activo=True
                )
                biblio.set_password("AdminPassE2E2026")
                db.session.add(biblio)

            # Estudiante A
            estudiante_a = db.session.get(Usuario, "USR_E2E_01")
            if not estudiante_a:
                estudiante_a = Usuario(
                    Codigo_Usuario="USR_E2E_01",
                    Nombre_Usuario="Estudiante E2E Uno",
                    Email_Usuario="estudiante.e2e@universidad.edu.co",
                    ID_Tipo_Usuario=8888,
                    ID_Facultad=8888,
                    Activo=True
                )
                estudiante_a.set_password("EstudiantePass2026")
                db.session.add(estudiante_a)

            # Estudiante B
            estudiante_b = db.session.get(Usuario, "USR_E2E_02")
            if not estudiante_b:
                estudiante_b = Usuario(
                    Codigo_Usuario="USR_E2E_02",
                    Nombre_Usuario="Estudiante E2E Dos",
                    Email_Usuario="estudiante2.e2e@universidad.edu.co",
                    ID_Tipo_Usuario=8888,
                    ID_Facultad=8888,
                    Activo=True
                )
                estudiante_b.set_password("EstudiantePass2026")
                db.session.add(estudiante_b)

            # Libro base
            libro = db.session.get(Libro, "LIB_E2E_BASE")
            if not libro:
                libro = Libro(
                    Codigo_Libro="LIB_E2E_BASE",
                    Titulo_Libro="Patrones de Diseno y Pruebas Unitarias",
                    Isbn_Libro="978-0201633610"
                )
                db.session.add(libro)

            db.session.commit()

            # Tokens
            token_admin = create_access_token(
                identity="BIB_E2E_01",
                additional_claims={"rol": "bibliotecario"}
            )
            token_estudiante = create_access_token(
                identity="USR_E2E_01",
                additional_claims={"rol": "usuario"}
            )
            cls.admin_headers = {"Authorization": f"Bearer {token_admin}"}
            cls.estudiante_headers = {"Authorization": f"Bearer {token_estudiante}"}

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            # Limpiar prestamos y reservas
            for p in Prestamo.query.filter(Prestamo.Codigo_Libro.in_(["LIB_E2E_BASE", "LIB_E2E_NUEVO"])).all():
                db.session.delete(p)
            for r in Reserva.query.filter(Reserva.Codigo_Libro.in_(["LIB_E2E_BASE", "LIB_E2E_NUEVO"])).all():
                db.session.delete(r)

            # Limpiar usuarios, bibliotecarios y libros
            for cod in ["USR_E2E_01", "USR_E2E_02", "USR_E2E_REG"]:
                u = db.session.get(Usuario, cod)
                if u:
                    db.session.delete(u)

            b = db.session.get(Bibliotecario, "BIB_E2E_01")
            if b:
                db.session.delete(b)

            for cod_l in ["LIB_E2E_BASE", "LIB_E2E_NUEVO"]:
                l = db.session.get(Libro, cod_l)
                if l:
                    db.session.delete(l)

            for model, id_val in [(Facultad, 8888), (TipoUsuario, 8888), (Turno, 8888)]:
                item = db.session.get(model, id_val)
                if item:
                    db.session.delete(item)

            db.session.commit()

    def setUp(self):
        cache.clear()

    # =========================================================================
    # RECORRIDO 3.1: BUSQUEDA Y CATALOGO DE LIBROS
    # =========================================================================
    def test_01_flujo_busqueda_catalogo_y_cache(self):
        """Flujo de busqueda de libros: existentes, inexistentes, detalle y cache ETag"""
        # 1. Consulta general
        res_cat = self.client.get("/api/libros")
        self.assertEqual(res_cat.status_code, 200)
        self.assertGreaterEqual(res_cat.get_json()["total"], 1)

        # 2. Busqueda por titulo existente
        res_search = self.client.get("/api/libros?titulo=Patrones")
        self.assertEqual(res_search.status_code, 200)
        libros = res_search.get_json()["libros"]
        self.assertTrue(any("Patrones" in l["Titulo_Libro"] for l in libros))

        # 3. Busqueda de libro inexistente
        res_none = self.client.get("/api/libros?titulo=LibroQueNuncaExistio123456")
        self.assertEqual(res_none.status_code, 200)
        self.assertEqual(res_none.get_json()["total"], 0)

        # 4. Detalle individual
        res_detail = self.client.get("/api/libros/LIB_E2E_BASE")
        self.assertEqual(res_detail.status_code, 200)
        self.assertEqual(res_detail.get_json()["libro"]["Codigo_Libro"], "LIB_E2E_BASE")

        # 5. Comprobar cabecera ETag y 304 Not Modified
        etag = res_detail.headers.get("ETag")
        self.assertIsNotNone(etag)
        res_304 = self.client.get("/api/libros/LIB_E2E_BASE", headers={"If-None-Match": etag})
        self.assertEqual(res_304.status_code, 304)

    # =========================================================================
    # RECORRIDO 3.2: PRESTAMOS, DEVOLUCIONES Y RESERVAS
    # =========================================================================
    def test_02_flujo_completo_prestamo_devolucion_y_disponibilidad(self):
        """
        Recorrido de negocio E2E:
        1. Verificar ejemplar disponible (disponible: true).
        2. Bibliotecario registra prestamo a estudiante (201 Created).
        3. Comprobar que disponibilidad pasa a false.
        4. Estudiante B intenta reservar el ejemplar prestado (201 Created).
        5. Bibliotecario registra la devolucion del ejemplar (200 OK).
        6. Disponibilidad se actualiza de inmediato a true.
        """
        codigo_libro = "LIB_E2E_BASE"

        # 1. Disponibilidad inicial
        res_disp1 = self.client.get(f"/api/libros/{codigo_libro}/disponibilidad")
        self.assertEqual(res_disp1.status_code, 200)
        self.assertTrue(res_disp1.get_json()["disponible"])

        # 2. Registrar prestamo
        payload_prestamo = {
            "Codigo_Usuario": "USR_E2E_01",
            "Codigo_Libro": codigo_libro,
            "Codigo_Bibliotecario": "BIB_E2E_01",
            "Fecha_Prestamo": "2026-10-16",
            "Fecha_Dev_Prevista": "2026-10-30"
        }
        res_p = self.client.post("/api/prestamos", json=payload_prestamo, headers=self.admin_headers)
        self.assertEqual(res_p.status_code, 201)
        prestamo_id = res_p.get_json()["prestamo"]["ID_Prestamo"]

        # 3. Disponibilidad ahora debe ser False
        res_disp2 = self.client.get(f"/api/libros/{codigo_libro}/disponibilidad")
        self.assertEqual(res_disp2.status_code, 200)
        self.assertFalse(res_disp2.get_json()["disponible"])

        # 4. Estudiante B reserva el libro
        payload_reserva = {
            "Codigo_Usuario": "USR_E2E_02",
            "Codigo_Libro": codigo_libro,
            "Posicion_Cola_Reserva": 1
        }
        res_r = self.client.post("/api/reservas", json=payload_reserva, headers=self.estudiante_headers)
        self.assertEqual(res_r.status_code, 201)
        reserva_id = res_r.get_json()["reserva"]["Codigo_Reserva"]

        # 5. Registrar devolucion (PUT)
        res_dev = self.client.put(
            f"/api/prestamos/{prestamo_id}",
            json={"Fecha_Dev_Real": "2026-10-22"},
            headers=self.admin_headers
        )
        self.assertEqual(res_dev.status_code, 200)

        # 6. Disponibilidad vuelve a ser True
        res_disp3 = self.client.get(f"/api/libros/{codigo_libro}/disponibilidad")
        self.assertEqual(res_disp3.status_code, 200)
        self.assertTrue(res_disp3.get_json()["disponible"])

        # Limpiar registros creados
        self.client.delete(f"/api/reservas/{reserva_id}", headers=self.admin_headers)
        self.client.delete(f"/api/prestamos/{prestamo_id}", headers=self.admin_headers)

    # =========================================================================
    # RECORRIDO 3.3: INICIO DE SESION Y PERMISOS RBAC
    # =========================================================================
    def test_03_flujo_autenticacion_roles_y_aislamiento(self):
        """Validacion de inicio de sesion, emision de JWT, claims y aislamiento"""
        # 1. Login exitoso
        login_res = self.client.post("/api/auth/login", json={
            "identificador": "estudiante.e2e@universidad.edu.co",
            "Password": "EstudiantePass2026"
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.get_json()["access_token"]
        self.assertEqual(login_res.get_json()["rol"], "usuario")

        # 2. Credenciales incorrectas
        bad_login = self.client.post("/api/auth/login", json={
            "identificador": "estudiante.e2e@universidad.edu.co",
            "Password": "ContrasenaEquivocada"
        })
        self.assertEqual(bad_login.status_code, 401)

        # 3. Acceso a perfil
        perfil_res = self.client.get("/api/auth/perfil", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(perfil_res.status_code, 200)
        self.assertEqual(perfil_res.get_json()["usuario"]["Codigo_Usuario"], "USR_E2E_01")

        # 4. Estudiante intentando acceder a perfil de otro estudiante (403)
        res_other = self.client.get("/api/usuarios/USR_E2E_02", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_other.status_code, 403)

        # 5. Estudiante intentando operacion administrativa de creacion de libro (403)
        res_unauth = self.client.post(
            "/api/libros",
            json={"Codigo_Libro": "LIB_FAIL", "Titulo_Libro": "No Permitido"},
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res_unauth.status_code, 403)

    # =========================================================================
    # RECORRIDO 3.4: ADMINISTRACION DEL CATALOGO Y CONTRATOS OPENAPI
    # =========================================================================
    def test_04_flujo_administracion_catalogo_y_contrato_openapi(self):
        """Operaciones CRUD de catalogo por bibliotecario y validacion de contrato OpenAPI"""
        codigo_nuevo = "LIB_E2E_NUEVO"

        # 1. Registro de libro
        create_res = self.client.post("/api/libros", json={
            "Codigo_Libro": codigo_nuevo,
            "Titulo_Libro": "Ingenieria de Software y Pruebas E2E",
            "Isbn_Libro": "978-1122334455"
        }, headers=self.admin_headers)
        self.assertEqual(create_res.status_code, 201)

        # 2. Modificar informacion
        update_res = self.client.put(f"/api/libros/{codigo_nuevo}", json={
            "Titulo_Libro": "Ingenieria de Software y Pruebas E2E (2da Edicion)"
        }, headers=self.admin_headers)
        self.assertEqual(update_res.status_code, 200)

        # 3. Eliminar libro
        del_res = self.client.delete(f"/api/libros/{codigo_nuevo}", headers=self.admin_headers)
        self.assertEqual(del_res.status_code, 200)

        # 4. Verificar contrato OpenAPI disponible
        res_yaml = self.client.get("/openapi.yaml")
        self.assertEqual(res_yaml.status_code, 200)
        self.assertIn("openapi: 3.0.3", res_yaml.get_data(as_text=True))

        # 5. Verificar interfaz Swagger UI disponible
        res_ui = self.client.get("/api/docs")
        self.assertEqual(res_ui.status_code, 200)
        self.assertIn("swagger-ui", res_ui.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
