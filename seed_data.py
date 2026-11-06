from modelo import (
    db, TipoUsuario, Facultad, Turno, EstadoFisico, EstadoPrestamo,
    EstadoReserva, Pais, Idioma, Editorial, Categoria, Autor, Libro,
    Usuario, Bibliotecario
)


def seed_database(app):
    """Inicializa catalogos basicos, cuentas demo y libros si la base de datos esta vacia"""
    with app.app_context():
        # 1. TIPOS DE USUARIO (Estudiante, Docente, Investigador)
        tipos_map = {}
        if TipoUsuario.query.count() == 0:
            for nombre in ["Estudiante", "Docente", "Investigador"]:
                t = TipoUsuario(Nombre_Tipo=nombre)
                db.session.add(t)
            db.session.commit()
            print("Tipos de usuario inicializados.")
        for t in TipoUsuario.query.all():
            tipos_map[t.Nombre_Tipo] = t.ID_Tipo_Usuario

        # 2. FACULTADES
        fac_map = {}
        if Facultad.query.count() == 0:
            facultades = [
                "Ingenieria y Ciencias Basicas",
                "Ciencias de la Salud",
                "Ciencias Economicas y Administrativas",
                "Ciencias Juridicas y Politicas",
                "Ciencias Sociales y Humanas"
            ]
            for f_nom in facultades:
                db.session.add(Facultad(Nombre_Facultad=f_nom))
            db.session.commit()
            print("Facultades inicializadas.")
        for f in Facultad.query.all():
            fac_map[f.Nombre_Facultad] = f.ID_Facultad

        # 3. TURNOS
        turno_map = {}
        if Turno.query.count() == 0:
            for t_nom in ["Manana", "Tarde", "Noche"]:
                db.session.add(Turno(Nombre_Turno=t_nom))
            db.session.commit()
            print("Turnos inicializados.")
        for t in Turno.query.all():
            turno_map[t.Nombre_Turno] = t.ID_Turno

        # 4. ESTADOS FISICOS
        if EstadoFisico.query.count() == 0:
            for ef in ["Excelente", "Bueno", "Regular", "Danado"]:
                db.session.add(EstadoFisico(Nombre_Estado=ef))
            db.session.commit()

        # 5. ESTADOS DE PRESTAMO
        if EstadoPrestamo.query.count() == 0:
            for ep in ["Activo", "Devuelto", "Vencido"]:
                db.session.add(EstadoPrestamo(Nombre_Estado=ep))
            db.session.commit()

        # 6. ESTADOS DE RESERVA
        if EstadoReserva.query.count() == 0:
            for er in ["Pendiente", "Completada", "Cancelada"]:
                db.session.add(EstadoReserva(Nombre_Estado=er))
            db.session.commit()

        # 7. PAISES E IDIOMAS
        if Pais.query.count() == 0:
            for p in ["Colombia", "Espana", "Mexico", "Estados Unidos"]:
                db.session.add(Pais(Nombre_Pais=p))
            db.session.commit()

        if Idioma.query.count() == 0:
            for i in ["Espanol", "Ingles", "Frances"]:
                db.session.add(Idioma(Nombre_Idioma=i))
            db.session.commit()

        # 8. EDITORIALES Y CATEGORIAS
        ed_map = {}
        if Editorial.query.count() == 0:
            for ed in ["Pearson Educacion", "McGraw-Hill", "O'Reilly Media", "Planeta"]:
                db.session.add(Editorial(Nombre_Editorial=ed))
            db.session.commit()
        for ed in Editorial.query.all():
            ed_map[ed.Nombre_Editorial] = ed.ID_Editorial

        cat_map = {}
        if Categoria.query.count() == 0:
            for cat in ["Ingenieria de Software", "Bases de Datos", "Redes y Telecomunicaciones", "Inteligencia Artificial", "Literatura"]:
                db.session.add(Categoria(Nombre_Categoria=cat))
            db.session.commit()
        for cat in Categoria.query.all():
            cat_map[cat.Nombre_Categoria] = cat.ID_Categoria

        # 9. USUARIOS DEMO (Estudiante y Docente)
        id_est = tipos_map.get("Estudiante", 1)
        id_doc = tipos_map.get("Docente", 2)
        id_fac_ing = list(fac_map.values())[0] if fac_map else None

        # Estudiante
        if not Usuario.query.filter_by(Email_Usuario="estudiante@universidad.edu.co").first():
            est = Usuario(
                Codigo_Usuario="EST001",
                Nombre_Usuario="Carlos Andres Gomez",
                Email_Usuario="estudiante@universidad.edu.co",
                Telefono_Usuario="3101234567",
                ID_Tipo_Usuario=id_est,
                ID_Facultad=id_fac_ing,
                Prestamos_Activos=0,
                Limite_Prestamos=3,
                Activo=True
            )
            est.set_password("Password123")
            db.session.add(est)

        # Docente
        if not Usuario.query.filter_by(Email_Usuario="docente@universidad.edu.co").first():
            doc = Usuario(
                Codigo_Usuario="DOC001",
                Nombre_Usuario="Dra. Elena Ramos",
                Email_Usuario="docente@universidad.edu.co",
                Telefono_Usuario="3207654321",
                ID_Tipo_Usuario=id_doc,
                ID_Facultad=id_fac_ing,
                Prestamos_Activos=0,
                Limite_Prestamos=5,
                Activo=True
            )
            doc.set_password("Password123")
            db.session.add(doc)

        # 10. BIBLIOTECARIO DEMO (Admin)
        id_turno_manana = list(turno_map.values())[0] if turno_map else None
        if not Bibliotecario.query.filter_by(Email_Bibliotecario="bibliotecario@universidad.edu.co").first():
            bib = Bibliotecario(
                Codigo_Bibliotecario="BIB001",
                Nombre_Bibliotecario="Lic. Mateo Cardona",
                Email_Bibliotecario="bibliotecario@universidad.edu.co",
                ID_Turno=id_turno_manana,
                Activo=True
            )
            bib.set_password("AdminPassword123")
            db.session.add(bib)

        # Cuentas para pruebas automatizadas (Cypress y Seguridad)
        if not Bibliotecario.query.filter_by(Codigo_Bibliotecario="BIB_SEC_01").first():
            bib_sec = Bibliotecario(
                Codigo_Bibliotecario="BIB_SEC_01",
                Nombre_Bibliotecario="Bibliotecario Seguridad",
                Email_Bibliotecario="biblio.seguridad@test.com",
                ID_Turno=id_turno_manana or 1,
                Activo=True
            )
            bib_sec.set_password("AdminPass123")
            db.session.add(bib_sec)

        if not Usuario.query.filter_by(Codigo_Usuario="USR_SEC_A").first():
            usr_sec_a = Usuario(
                Codigo_Usuario="USR_SEC_A",
                Nombre_Usuario="Usuario A",
                Email_Usuario="usuario.a@test.com",
                ID_Tipo_Usuario=id_est,
                ID_Facultad=id_fac_ing,
                Prestamos_Activos=0,
                Limite_Prestamos=3,
                Activo=True
            )
            usr_sec_a.set_password("UserPass123")
            db.session.add(usr_sec_a)

        if not Usuario.query.filter_by(Codigo_Usuario="USR_SEC_B").first():
            usr_sec_b = Usuario(
                Codigo_Usuario="USR_SEC_B",
                Nombre_Usuario="Usuario B",
                Email_Usuario="usuario.b@test.com",
                ID_Tipo_Usuario=id_est,
                ID_Facultad=id_fac_ing,
                Prestamos_Activos=0,
                Limite_Prestamos=3,
                Activo=True
            )
            usr_sec_b.set_password("UserPass123")
            db.session.add(usr_sec_b)

        db.session.commit()
        print("Usuarios y bibliotecarios demo inicializados.")

        # 11. LIBROS DE EJEMPLO
        if Libro.query.count() == 0:
            id_ed = list(ed_map.values())[0] if ed_map else None
            primer_idioma = Idioma.query.first()
            id_idm = primer_idioma.ID_Idioma if primer_idioma else None
            primer_estado = EstadoFisico.query.first()
            id_ef = primer_estado.ID_Estado_Fisico if primer_estado else None

            libros_iniciales = [
                ("LIB001", "Fundamentos de Bases de Datos", "978-0133970777", "7ma Edicion", 2023),
                ("LIB002", "Redes de Computadores: Enfoque Descendente", "978-0132126953", "8va Edicion", 2024),
                ("LIB003", "Ingenieria de Software: Un Enfoque Practico", "978-6071503145", "9na Edicion", 2022),
                ("LIB004", "Inteligencia Artificial: Un Enfoque Moderno", "978-0134610993", "4ta Edicion", 2024),
                ("LIB005", "Sistemas Distribuidos: Principios y Paradigmas", "978-1530281756", "3ra Edicion", 2023)
            ]

            for cod, tit, isbn, edic, anio in libros_iniciales:
                l = Libro(
                    Codigo_Libro=cod,
                    Titulo_Libro=tit,
                    Isbn_Libro=isbn,
                    Edicion=edic,
                    Anio_Publicacion=anio,
                    ID_Editorial=id_ed,
                    ID_Idioma=id_idm,
                    ID_Estado_Fisico=id_ef,
                    Codigo_Bibliotecario="BIB001"
                )
                db.session.add(l)

            db.session.commit()
            print("Catalogo inicial de libros creado.")


if __name__ == "__main__":
    from app import app
    seed_database(app)
    print("Base de datos inicializada exitosamente con datos y usuarios demo!")
