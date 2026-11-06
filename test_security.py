import unittest
import json
from app import app
from modelo import db, Usuario, Bibliotecario, TipoUsuario, Facultad, Turno
from flask_jwt_extended import create_access_token


class TestSeguridadAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

        # Crear dependencias previas necesarias si no existen
        with app.app_context():
            # Facultad
            facultad = db.session.get(Facultad, 9999)
            if not facultad:
                facultad = Facultad(ID_Facultad=9999, Nombre_Facultad="Facultad Pruebas Seguridad")
                db.session.add(facultad)

            # Tipo Usuario
            tipo_u = db.session.get(TipoUsuario, 9999)
            if not tipo_u:
                tipo_u = TipoUsuario(ID_Tipo_Usuario=9999, Nombre_Tipo="Estudiante Seguridad")
                db.session.add(tipo_u)

            # Turno
            turno = db.session.get(Turno, 9999)
            if not turno:
                turno = Turno(ID_Turno=9999, Nombre_Turno="Turno Seguridad")
                db.session.add(turno)

            # Bibliotecario de prueba
            biblio = db.session.get(Bibliotecario, "BIB_SEC_01")
            if not biblio:
                biblio = Bibliotecario(
                    Codigo_Bibliotecario="BIB_SEC_01",
                    Nombre_Bibliotecario="Bibliotecario Seguridad",
                    Email_Bibliotecario="biblio.seguridad@test.com",
                    ID_Turno=9999,
                    Activo=True
                )
                biblio.set_password("AdminPass123")
                db.session.add(biblio)

            # Usuario regular de prueba A
            usr_a = db.session.get(Usuario, "USR_SEC_A")
            if not usr_a:
                usr_a = Usuario(
                    Codigo_Usuario="USR_SEC_A",
                    Nombre_Usuario="Usuario A",
                    Email_Usuario="usuario.a@test.com",
                    ID_Tipo_Usuario=9999,
                    ID_Facultad=9999,
                    Activo=True
                )
                usr_a.set_password("UserPass123")
                db.session.add(usr_a)

            # Usuario regular de prueba B
            usr_b = db.session.get(Usuario, "USR_SEC_B")
            if not usr_b:
                usr_b = Usuario(
                    Codigo_Usuario="USR_SEC_B",
                    Nombre_Usuario="Usuario B",
                    Email_Usuario="usuario.b@test.com",
                    ID_Tipo_Usuario=9999,
                    ID_Facultad=9999,
                    Activo=True
                )
                usr_b.set_password("UserPass456")
                db.session.add(usr_b)

            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            # Limpiar usuarios y bibliotecarios de prueba
            for cod in ["USR_SEC_A", "USR_SEC_B", "USR_REG_NUEVO", "USR_DOC_TEST"]:
                u = db.session.get(Usuario, cod)
                if u:
                    db.session.delete(u)

            for cod_b in ["BIB_SEC_01", "BIB_REG_NUEVO"]:
                b = db.session.get(Bibliotecario, cod_b)
                if b:
                    db.session.delete(b)

            for model, id_val in [(Facultad, 9999), (TipoUsuario, 9999), (Turno, 9999)]:
                item = db.session.get(model, id_val)
                if item:
                    db.session.delete(item)

            db.session.commit()

    def test_01_rutas_publicas_sin_token(self):
        """El catalogo de libros y paises debe ser publico (GET sin token)"""
        res = self.client.get("/api/libros")
        self.assertEqual(res.status_code, 200)

        res2 = self.client.get("/api/paises")
        self.assertEqual(res2.status_code, 200)

    def test_02_rutas_protegidas_rechazan_sin_token(self):
        """Operaciones de creacion/modificacion deben retornar 401 Unauthorized sin token"""
        res = self.client.post("/api/paises", json={"Nombre_Pais": "Pais No Autorizado"})
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertIn("error", data)

        res_prestamo = self.client.post("/api/prestamos", json={"Codigo_Libro": "LIB1"})
        self.assertEqual(res_prestamo.status_code, 401)

    def test_03_usuario_regular_rechazado_en_rutas_admin(self):
        """Un usuario regular con token debe recibir 403 Forbidden al intentar operaciones de bibliotecario"""
        with app.app_context():
            token_usuario = create_access_token(
                identity="USR_SEC_A",
                additional_claims={"rol": "usuario", "nombre": "Usuario A"}
            )

        headers = {"Authorization": f"Bearer {token_usuario}"}

        # Intentar crear un pais (solo bibliotecario)
        res = self.client.post("/api/paises", json={"Nombre_Pais": "Pais Prohibido"}, headers=headers)
        self.assertEqual(res.status_code, 403)
        self.assertIn("Permisos insuficientes", res.get_json()["mensaje"])

        # Intentar listar todos los bibliotecarios
        res_b = self.client.get("/api/bibliotecarios", headers=headers)
        self.assertEqual(res_b.status_code, 403)

    def test_04_registro_de_usuario_genera_jwt_valido(self):
        """El registro exitoso crea el usuario y devuelve token JWT con rol 'usuario'"""
        payload = {
            "Codigo_Usuario": "USR_REG_NUEVO",
            "Nombre_Usuario": "Nuevo Registrado",
            "Email_Usuario": "nuevo.reg@test.com",
            "Password": "MiPasswordSeguro123",
            "ID_Tipo_Usuario": 9999,
            "ID_Facultad": 9999
        }
        res = self.client.post("/api/auth/registro", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn("access_token", data)
        self.assertEqual(data.get("rol"), "usuario")

    def test_05_login_usuario_y_credenciales_incorrectas(self):
        """Login con credenciales correctas e incorrectas"""
        # Credenciales correctas
        res = self.client.post("/api/auth/login", json={
            "identificador": "usuario.a@test.com",
            "Password": "UserPass123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("access_token", data)
        self.assertEqual(data["rol"], "usuario")

        # Contrasena incorrecta
        res_fail = self.client.post("/api/auth/login", json={
            "identificador": "usuario.a@test.com",
            "Password": "PasswordIncorrecto"
        })
        self.assertEqual(res_fail.status_code, 401)
        self.assertEqual(res_fail.get_json()["error"], "Credenciales invalidas")

    def test_06_login_bibliotecario(self):
        """Login de bibliotecario devuelve token con rol 'bibliotecario'"""
        # A traves del endpoint unificado /api/auth/login
        res = self.client.post("/api/auth/login", json={
            "identificador": "biblio.seguridad@test.com",
            "Password": "AdminPass123"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["rol"], "bibliotecario")

        # A traves del endpoint dedicado /api/auth/login-bibliotecario
        res2 = self.client.post("/api/auth/login-bibliotecario", json={
            "identificador": "BIB_SEC_01",
            "Password": "AdminPass123"
        })
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.get_json()["rol"], "bibliotecario")

    def test_07_aislamiento_de_usuarios(self):
        """El Usuario A NO debe poder consultar ni modificar la cuenta del Usuario B (403)"""
        with app.app_context():
            token_usr_a = create_access_token(
                identity="USR_SEC_A",
                additional_claims={"rol": "usuario"}
            )
            token_admin = create_access_token(
                identity="BIB_SEC_01",
                additional_claims={"rol": "bibliotecario"}
            )

        headers_a = {"Authorization": f"Bearer {token_usr_a}"}
        headers_admin = {"Authorization": f"Bearer {token_admin}"}

        # Usuario A consulta su propio perfil -> 200 OK
        res_own = self.client.get("/api/usuarios/USR_SEC_A", headers=headers_a)
        self.assertEqual(res_own.status_code, 200)

        # Usuario A intenta consultar perfil del Usuario B -> 403 Forbidden
        res_other = self.client.get("/api/usuarios/USR_SEC_B", headers=headers_a)
        self.assertEqual(res_other.status_code, 403)

        # Bibliotecario consulta perfil del Usuario B -> 200 OK (administrador si puede)
        res_admin = self.client.get("/api/usuarios/USR_SEC_B", headers=headers_admin)
        self.assertEqual(res_admin.status_code, 200)

    def test_08_cabeceras_de_seguridad_http(self):
        """Las respuestas HTTP deben incluir cabeceras de proteccion contra sniffing, clickjacking y XSS"""
        res = self.client.get("/api/libros")
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(res.headers.get("X-XSS-Protection"), "1; mode=block")

    def test_09_registro_docente_y_resolucion_perfil(self):
        """Registro de Docente con resolucion por nombre de tipo de usuario y facultad"""
        payload = {
            "Codigo_Usuario": "USR_DOC_TEST",
            "Nombre_Usuario": "Profesor Seguridad",
            "Email_Usuario": "profesor.seguridad@test.com",
            "Password": "DocentePassword123",
            "Tipo_Usuario": "Docente",
            "Facultad": "Facultad de Ingenieria"
        }
        res = self.client.post("/api/auth/registro", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn("access_token", data)
        self.assertEqual(data.get("tipo_usuario"), "Docente")
        self.assertEqual(data.get("rol"), "usuario")

        # Probar login con el docente registrado
        res_login = self.client.post("/api/auth/login", json={
            "identificador": "profesor.seguridad@test.com",
            "Password": "DocentePassword123"
        })
        self.assertEqual(res_login.status_code, 200)
        login_data = res_login.get_json()
        self.assertEqual(login_data.get("tipo_usuario"), "Docente")

    def test_10_registro_bibliotecario(self):
        """Registro de nuevo personal bibliotecario/administrador"""
        payload = {
            "Codigo_Bibliotecario": "BIB_REG_NUEVO",
            "Nombre_Bibliotecario": "Nuevo Bibliotecario Test",
            "Email_Bibliotecario": "nuevo.biblio@test.com",
            "Password": "AdminPassword123",
            "Turno": "Tarde"
        }
        res = self.client.post("/api/auth/registro-bibliotecario", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn("access_token", data)
        self.assertEqual(data.get("rol"), "bibliotecario")
        self.assertEqual(data.get("tipo_usuario"), "Bibliotecario")

        # Probar login con el bibliotecario registrado
        res_login = self.client.post("/api/auth/login", json={
            "identificador": "BIB_REG_NUEVO",
            "Password": "AdminPassword123"
        })
        self.assertEqual(res_login.status_code, 200)
        login_data = res_login.get_json()
        self.assertEqual(login_data.get("rol"), "bibliotecario")

    def test_11_opciones_registro_publicas(self):
        """El endpoint de opciones de registro debe ser publico y retornar tipos, facultades y turnos"""
        res = self.client.get("/api/auth/opciones-registro")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("tipos_usuario", data)
        self.assertIn("facultades", data)
        self.assertIn("turnos", data)
        self.assertGreater(len(data["tipos_usuario"]), 0)


if __name__ == "__main__":
    unittest.main()

