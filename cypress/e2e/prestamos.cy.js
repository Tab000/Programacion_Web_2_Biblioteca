describe('3.2. Préstamos, Devoluciones y Reservas', () => {

  it('1. Debe rechazar registrar un prestamo sin token de autenticacion (401 Unauthorized)', () => {
    cy.request({
      method: 'POST',
      url: '/api/prestamos',
      body: {
        Codigo_Libro: 'LIB_TEST',
        Codigo_Usuario: 'USR_TEST'
      },
      failOnStatusCode: false
    }).then((res) => {
      expect(res.status).to.eq(401);
      expect(res.body).to.have.property('error');
    });
  });

  it('2. Debe rechazar registrar prestamo a un estudiante sin rol de bibliotecario (403 Forbidden)', () => {
    cy.loginUsuario().then((tokenUsuario) => {
      cy.request({
        method: 'POST',
        url: '/api/prestamos',
        headers: {
          Authorization: `Bearer ${tokenUsuario}`
        },
        body: {
          Codigo_Libro: 'LIB_001',
          Codigo_Usuario: 'usuario.a@test.com'
        },
        failOnStatusCode: false
      }).then((res) => {
        expect(res.status).to.eq(403);
        expect(res.body.mensaje).to.include('Permisos insuficientes');
      });
    });
  });

  it('3. Debe registrar un prestamo valido con rol de bibliotecario (201 Created) e invalidar disponibilidad', () => {
    cy.loginBibliotecario().then((tokenAdmin) => {
      // 1. Crear usuario y libro temporales para la prueba
      const codigoLibro = 'LIB_CY_PRESTAMO';
      const codigoUsuario = 'USR_CY_PRESTAMO';

      cy.request({
        method: 'POST',
        url: '/api/usuarios',
        headers: { Authorization: `Bearer ${tokenAdmin}` },
        body: {
          Codigo_Usuario: codigoUsuario,
          Nombre_Usuario: 'Usuario Cypress Prestamos',
          Email_Usuario: 'usr.cy.prestamo@test.com',
          Password: 'Password123'
        },
        failOnStatusCode: false
      });

      cy.request({
        method: 'POST',
        url: '/api/libros',
        headers: { Authorization: `Bearer ${tokenAdmin}` },
        body: {
          Codigo_Libro: codigoLibro,
          Titulo_Libro: 'Libro de Prueba Cypress Prestamos'
        },
        failOnStatusCode: false
      });

      // 2. Registrar el prestamo
      cy.request({
        method: 'POST',
        url: '/api/prestamos',
        headers: { Authorization: `Bearer ${tokenAdmin}` },
        body: {
          Codigo_Usuario: codigoUsuario,
          Codigo_Libro: codigoLibro,
          Codigo_Bibliotecario: 'BIB_SEC_01',
          Fecha_Prestamo: '2026-10-16',
          Fecha_Dev_Prevista: '2026-10-30'
        }
      }).then((prestamoRes) => {
        expect(prestamoRes.status).to.eq(201);
        expect(prestamoRes.body).to.have.property('prestamo');
        const idPrestamo = prestamoRes.body.prestamo.ID_Prestamo;

        // 3. Verificar que la disponibilidad cambio a false
        cy.request({
          method: 'GET',
          url: `/api/libros/${codigoLibro}/disponibilidad`
        }).then((dispRes) => {
          expect(dispRes.status).to.eq(200);
          expect(dispRes.body.disponible).to.eq(false);
        });

        // 4. Registrar devolucion (PUT con Fecha_Dev_Real)
        cy.request({
          method: 'PUT',
          url: `/api/prestamos/${idPrestamo}`,
          headers: { Authorization: `Bearer ${tokenAdmin}` },
          body: {
            Fecha_Dev_Real: '2026-10-20'
          }
        }).then((devRes) => {
          expect(devRes.status).to.eq(200);

          // 5. Verificar que el libro volvio a estar disponible
          cy.request({
            method: 'GET',
            url: `/api/libros/${codigoLibro}/disponibilidad`
          }).then((dispAfter) => {
            expect(dispAfter.status).to.eq(200);
            expect(dispAfter.body.disponible).to.eq(true);
          });
        });

        // Limpieza
        cy.request({
          method: 'DELETE',
          url: `/api/prestamos/${idPrestamo}`,
          headers: { Authorization: `Bearer ${tokenAdmin}` }
        });
        cy.request({
          method: 'DELETE',
          url: `/api/libros/${codigoLibro}`,
          headers: { Authorization: `Bearer ${tokenAdmin}` }
        });
        cy.request({
          method: 'DELETE',
          url: `/api/usuarios/${codigoUsuario}`,
          headers: { Authorization: `Bearer ${tokenAdmin}` }
        });
      });
    });
  });

  it('4. Debe permitir a un estudiante autenticado crear una reserva (201 Created)', () => {
    cy.loginUsuario().then((tokenUsuario) => {
      cy.request({
        method: 'POST',
        url: '/api/reservas',
        headers: { Authorization: `Bearer ${tokenUsuario}` },
        body: {
          Codigo_Usuario: 'USR_SEC_A',
          Codigo_Libro: 'LIB001',
          Posicion_Cola_Reserva: 1
        },
        failOnStatusCode: false
      }).then((res) => {
        expect(res.status).to.eq(201);
        expect(res.body).to.have.property('reserva');
        const codReserva = res.body.reserva.Codigo_Reserva;

        // Limpiar reserva de prueba
        cy.request({
          method: 'DELETE',
          url: `/api/reservas/${codReserva}`,
          headers: { Authorization: `Bearer ${tokenUsuario}` }
        });
      });
    });
  });

});
