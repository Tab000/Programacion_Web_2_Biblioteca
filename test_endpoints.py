import unittest
import json
from app import app
from modelo import db

class TestEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from flask_jwt_extended import create_access_token
        cls.client = app.test_client()
        with app.app_context():
            token = create_access_token(
                identity="BIB_ADMIN_TEST",
                additional_claims={"rol": "bibliotecario", "nombre": "Admin Test"}
            )
        cls.client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"

    def test_01_pais(self):
        # 1. POST
        res = self.client.post("/api/paises", json={"Nombre_Pais": "Colombia"})
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        id_pais = data["pais"]["ID_Pais"]

        # 2. GET all
        res = self.client.get("/api/paises")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.get_json()["total"], 1)

        # 3. GET one
        res = self.client.get(f"/api/paises/{id_pais}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["pais"]["Nombre_Pais"], "Colombia")

        # 4. PUT
        res = self.client.put(f"/api/paises/{id_pais}", json={"Nombre_Pais": "Colombia Actualizada"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["pais"]["Nombre_Pais"], "Colombia Actualizada")

        # 5. DELETE
        res = self.client.delete(f"/api/paises/{id_pais}")
        self.assertEqual(res.status_code, 200)

        # 6. Verify 404
        res = self.client.get(f"/api/paises/{id_pais}")
        self.assertEqual(res.status_code, 404)

    def test_02_idioma(self):
        # POST
        res = self.client.post("/api/idiomas", json={"Nombre_Idioma": "Espanol"})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["idioma"]["ID_Idioma"]

        # GET all & one
        res = self.client.get("/api/idiomas")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/idiomas/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/idiomas/{id_item}", json={"Nombre_Idioma": "Castellano"})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/idiomas/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/idiomas/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_03_editorial(self):
        # POST
        res = self.client.post("/api/editoriales", json={"Nombre_Editorial": "Planeta"})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["editorial"]["ID_Editorial"]

        # GET all & one
        res = self.client.get("/api/editoriales")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/editoriales/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/editoriales/{id_item}", json={"Nombre_Editorial": "Editorial Planeta Editores"})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/editoriales/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/editoriales/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_04_estado_fisico(self):
        # POST
        res = self.client.post("/api/estados-fisicos", json={"Nombre_Estado": "Excelente"})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["estado_fisico"]["ID_Estado_Fisico"]

        # GET all & one
        res = self.client.get("/api/estados-fisicos")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/estados-fisicos/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/estados-fisicos/{id_item}", json={"Nombre_Estado": "Bueno"})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/estados-fisicos/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/estados-fisicos/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_05_facultad(self):
        # POST
        res = self.client.post("/api/facultades", json={"Nombre_Facultad": "Ingenieria"})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["facultad"]["ID_Facultad"]

        # GET all & one
        res = self.client.get("/api/facultades")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/facultades/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/facultades/{id_item}", json={"Nombre_Facultad": "Facultad de Ingenieria"})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/facultades/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/facultades/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_06_tipo_usuario(self):
        # POST
        res = self.client.post("/api/tipos-usuario", json={"Nombre_Tipo": "Estudiante"})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["tipo_usuario"]["ID_Tipo_Usuario"]

        # GET all & one
        res = self.client.get("/api/tipos-usuario")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/tipos-usuario/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/tipos-usuario/{id_item}", json={"Nombre_Tipo": "Docente"})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/tipos-usuario/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/tipos-usuario/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_07_turno(self):
        # POST
        res = self.client.post("/api/turnos", json={"Nombre_Turno": "Manana"})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["turno"]["ID_Turno"]

        # GET all & one
        res = self.client.get("/api/turnos")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/turnos/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/turnos/{id_item}", json={"Nombre_Turno": "Tarde"})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/turnos/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/turnos/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_08_estado_reserva(self):
        # POST
        res = self.client.post("/api/estados-reserva", json={"Nombre_Estado": "Pendiente"})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["estado_reserva"]["ID_Estado_Reserva"]

        # GET all & one
        res = self.client.get("/api/estados-reserva")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/estados-reserva/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/estados-reserva/{id_item}", json={"Nombre_Estado": "Confirmada"})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/estados-reserva/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/estados-reserva/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_09_estado_prestamo(self):
        # POST
        res = self.client.post("/api/estados-prestamo", json={"Nombre_Estado": "Activo"})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["estado_prestamo"]["ID_Estado_Prestamo"]

        # GET all & one
        res = self.client.get("/api/estados-prestamo")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/estados-prestamo/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/estados-prestamo/{id_item}", json={"Nombre_Estado": "Devuelto"})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/estados-prestamo/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/estados-prestamo/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_10_ciudad(self):
        # POST
        res = self.client.post("/api/ciudades", json={"Nombre_Ciudad": "Medellin"})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["ciudad"]["ID_Ciudad"]

        # GET all & one
        res = self.client.get("/api/ciudades")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/ciudades/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/ciudades/{id_item}", json={"Nombre_Ciudad": "Bogota"})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/ciudades/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/ciudades/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_11_categoria(self):
        # POST
        res = self.client.post("/api/categorias", json={"Nombre_Categoria": "Sistemas", "Nivel": 1})
        self.assertEqual(res.status_code, 201)
        id_item = res.get_json()["categoria"]["ID_Categoria"]

        # GET all & one
        res = self.client.get("/api/categorias")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/categorias/{id_item}")
        self.assertEqual(res.status_code, 200)

        # PUT
        res = self.client.put(f"/api/categorias/{id_item}", json={"Nombre_Categoria": "Ciencias de la Computacion", "Nivel": 2})
        self.assertEqual(res.status_code, 200)

        # DELETE
        res = self.client.delete(f"/api/categorias/{id_item}")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/categorias/{id_item}")
        self.assertEqual(res.status_code, 404)

    def test_12_relational_flow_autores_libros_usuarios_etc(self):
        # Setup lookup items
        pais_res = self.client.post("/api/paises", json={"Nombre_Pais": "Chile"})
        pais_id = pais_res.get_json()["pais"]["ID_Pais"]

        turno_res = self.client.post("/api/turnos", json={"Nombre_Turno": "Completo"})
        turno_id = turno_res.get_json()["turno"]["ID_Turno"]

        tipo_u_res = self.client.post("/api/tipos-usuario", json={"Nombre_Tipo": "Investigador"})
        tipo_u_id = tipo_u_res.get_json()["tipo_usuario"]["ID_Tipo_Usuario"]

        facultad_res = self.client.post("/api/facultades", json={"Nombre_Facultad": "Ciencias"})
        facultad_id = facultad_res.get_json()["facultad"]["ID_Facultad"]

        ciudad_res = self.client.post("/api/ciudades", json={"Nombre_Ciudad": "Cali"})
        ciudad_id = ciudad_res.get_json()["ciudad"]["ID_Ciudad"]

        editorial_res = self.client.post("/api/editoriales", json={"Nombre_Editorial": "Norma"})
        editorial_id = editorial_res.get_json()["editorial"]["ID_Editorial"]

        idioma_res = self.client.post("/api/idiomas", json={"Nombre_Idioma": "Ingles"})
        idioma_id = idioma_res.get_json()["idioma"]["ID_Idioma"]

        estado_f_res = self.client.post("/api/estados-fisicos", json={"Nombre_Estado": "Regular"})
        estado_f_id = estado_f_res.get_json()["estado_fisico"]["ID_Estado_Fisico"]

        categoria_res = self.client.post("/api/categorias", json={"Nombre_Categoria": "Literatura", "Nivel": 1})
        categoria_id = categoria_res.get_json()["categoria"]["ID_Categoria"]

        estado_p_res = self.client.post("/api/estados-prestamo", json={"Nombre_Estado": "Prestado"})
        estado_p_id = estado_p_res.get_json()["estado_prestamo"]["ID_Estado_Prestamo"]

        estado_r_res = self.client.post("/api/estados-reserva", json={"Nombre_Estado": "En Espera"})
        estado_r_id = estado_r_res.get_json()["estado_reserva"]["ID_Estado_Reserva"]

        # 12. AUTOR
        autor_res = self.client.post("/api/autores", json={
            "Nombre_Autor": "Pablo Neruda",
            "Bibliografia": "Poeta chileno, premio Nobel",
            "ID_Pais": pais_id
        })
        self.assertEqual(autor_res.status_code, 201)
        autor_id = autor_res.get_json()["autor"]["ID_Autor"]

        res = self.client.get(f"/api/autores/{autor_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["autor"]["Pais"], "Chile")

        res = self.client.put(f"/api/autores/{autor_id}", json={"Nombre_Autor": "Ricardo Eliécer Neftalí Reyes Basoalto"})
        self.assertEqual(res.status_code, 200)

        # 13. BIBLIOTECARIO
        bib_res = self.client.post("/api/bibliotecarios", json={
            "Codigo_Bibliotecario": "BIB_TEST_01",
            "Nombre_Bibliotecario": "Maria Auxiliadora",
            "Email_Bibliotecario": "maria.bib@test.com",
            "Password": "password123",
            "ID_Turno": turno_id
        })
        self.assertEqual(bib_res.status_code, 201)
        res = self.client.get("/api/bibliotecarios/BIB_TEST_01")
        self.assertEqual(res.status_code, 200)

        res = self.client.put("/api/bibliotecarios/BIB_TEST_01", json={"Nombre_Bibliotecario": "Maria Auxiliadora Gomez"})
        self.assertEqual(res.status_code, 200)

        # 14. LIBRO
        libro_res = self.client.post("/api/libros", json={
            "Codigo_Libro": "LIB_TEST_01",
            "Titulo_Libro": "Veinte poemas de amor y una cancion desesperada",
            "Isbn_Libro": "978-0143039969",
            "Edicion": "1ra",
            "Anio_Publicacion": 1924,
            "ID_Editorial": editorial_id,
            "ID_Idioma": idioma_id,
            "ID_Estado_Fisico": estado_f_id,
            "Codigo_Bibliotecario": "BIB_TEST_01",
            "autores": [autor_id],
            "categorias": [categoria_id]
        })
        self.assertEqual(libro_res.status_code, 201)
        res = self.client.get("/api/libros/LIB_TEST_01")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()["libro"]["autores"]), 1)
        self.assertEqual(len(res.get_json()["libro"]["categorias"]), 1)

        res = self.client.put("/api/libros/LIB_TEST_01", json={"Edicion": "2da Edicion"})
        self.assertEqual(res.status_code, 200)

        # 15. USUARIO
        usuario_res = self.client.post("/api/usuarios", json={
            "Codigo_Usuario": "USR_TEST_01",
            "Nombre_Usuario": "Carlos Andres Gomez",
            "Email_Usuario": "carlos.gomez@test.com",
            "Password": "password123",
            "Telefono_Usuario": "3111234567",
            "ID_Tipo_Usuario": tipo_u_id,
            "ID_Facultad": facultad_id
        })
        self.assertEqual(usuario_res.status_code, 201)
        res = self.client.get("/api/usuarios/USR_TEST_01")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["usuario"]["Nombre_Usuario"], "Carlos Andres Gomez")

        res = self.client.put("/api/usuarios/USR_TEST_01", json={"Telefono_Usuario": "3009876543"})
        self.assertEqual(res.status_code, 200)

        # 16. DIRECCION
        dir_res = self.client.post("/api/direcciones", json={
            "Codigo_Usuario": "USR_TEST_01",
            "Calle_Avenida": "Carrera 45",
            "Numero": "#12-34",
            "Barrio": "El Poblado",
            "ID_Ciudad": ciudad_id
        })
        self.assertEqual(dir_res.status_code, 201)
        dir_id = dir_res.get_json()["direccion"]["ID_Direccion"]
        res = self.client.get(f"/api/direcciones/{dir_id}")
        self.assertEqual(res.status_code, 200)

        res = self.client.put(f"/api/direcciones/{dir_id}", json={"Barrio": "Laureles"})
        self.assertEqual(res.status_code, 200)

        # 17. HISTORIAL_UBICACION
        hist_res = self.client.post("/api/historial-ubicaciones", json={
            "Codigo_Libro": "LIB_TEST_01",
            "Estante_Ubicacion": "Estante B-12",
            "Fecha_Asignacion": "2026-10-16"
        })
        self.assertEqual(hist_res.status_code, 201)
        hist_id = hist_res.get_json()["historial_ubicacion"]["ID_Historial"]
        res = self.client.get(f"/api/historial-ubicaciones/{hist_id}")
        self.assertEqual(res.status_code, 200)

        res = self.client.put(f"/api/historial-ubicaciones/{hist_id}", json={"Estante_Ubicacion": "Estante C-01"})
        self.assertEqual(res.status_code, 200)

        # 18. RESERVA
        res_res = self.client.post("/api/reservas", json={
            "Codigo_Usuario": "USR_TEST_01",
            "Codigo_Libro": "LIB_TEST_01",
            "Posicion_Cola_Reserva": 1,
            "ID_Estado_Reserva": estado_r_id,
            "Codigo_Bibliotecario": "BIB_TEST_01"
        })
        self.assertEqual(res_res.status_code, 201)
        res_id = res_res.get_json()["reserva"]["Codigo_Reserva"]
        res = self.client.get(f"/api/reservas/{res_id}")
        self.assertEqual(res.status_code, 200)

        res = self.client.put(f"/api/reservas/{res_id}", json={"Posicion_Cola_Reserva": 2})
        self.assertEqual(res.status_code, 200)

        # 19. PRESTAMO
        prest_res = self.client.post("/api/prestamos", json={
            "Codigo_Usuario": "USR_TEST_01",
            "Codigo_Libro": "LIB_TEST_01",
            "Codigo_Bibliotecario": "BIB_TEST_01",
            "Fecha_Prestamo": "2026-10-16",
            "Fecha_Dev_Prevista": "2026-10-30",
            "ID_Estado_Prestamo": estado_p_id
        })
        self.assertEqual(prest_res.status_code, 201)
        prest_id = prest_res.get_json()["prestamo"]["ID_Prestamo"]
        res = self.client.get(f"/api/prestamos/{prest_id}")
        self.assertEqual(res.status_code, 200)

        res = self.client.put(f"/api/prestamos/{prest_id}", json={"Dia_Retraso": 2, "Multa_Calculada": 4000.0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["prestamo"]["Dia_Retraso"], 2)

        # CLEANUP IN REVERSE ORDER TO RESPECT FOREIGN KEYS
        self.assertEqual(self.client.delete(f"/api/prestamos/{prest_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/reservas/{res_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/historial-ubicaciones/{hist_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/direcciones/{dir_id}").status_code, 200)
        self.assertEqual(self.client.delete("/api/usuarios/USR_TEST_01").status_code, 200)
        self.assertEqual(self.client.delete("/api/libros/LIB_TEST_01").status_code, 200)
        self.assertEqual(self.client.delete("/api/bibliotecarios/BIB_TEST_01").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/autores/{autor_id}").status_code, 200)

        self.assertEqual(self.client.delete(f"/api/estados-reserva/{estado_r_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/estados-prestamo/{estado_p_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/categorias/{categoria_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/estados-fisicos/{estado_f_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/idiomas/{idioma_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/editoriales/{editorial_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/ciudades/{ciudad_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/facultades/{facultad_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/tipos-usuario/{tipo_u_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/turnos/{turno_id}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/paises/{pais_id}").status_code, 200)

if __name__ == "__main__":
    unittest.main()
