describe('3.4. Administración del Catálogo de Libros', () => {

  const libroPrueba = {
    Codigo_Libro: 'LIB_CYPRESS_ADMIN',
    Titulo_Libro: 'Arquitectura de Software y Pruebas Automatizadas',
    Isbn_Libro: '978-9999888877',
    Edicion: '1ra Edicion',
    Anio_Publicacion: 2026
  };

  it('1. Debe rechazar registro de libro a usuario sin permisos administrativos (403 Forbidden)', () => {
    cy.loginUsuario().then((tokenUsuario) => {
      cy.request({
        method: 'POST',
        url: '/api/libros',
        headers: { Authorization: `Bearer ${tokenUsuario}` },
        body: libroPrueba,
        failOnStatusCode: false
      }).then((res) => {
        expect(res.status).to.eq(403);
        expect(res.body.mensaje).to.include('Permisos insuficientes');
      });
    });
  });

  it('2. Debe validar campos obligatorios al registrar un libro (400 Bad Request)', () => {
    cy.loginBibliotecario().then((tokenAdmin) => {
      cy.request({
        method: 'POST',
        url: '/api/libros',
        headers: { Authorization: `Bearer ${tokenAdmin}` },
        body: {
          Edicion: 'Sin Codigo Ni Titulo'
        },
        failOnStatusCode: false
      }).then((res) => {
        expect(res.status).to.eq(400);
        expect(res.body).to.have.property('error');
        expect(res.body.detalle).to.include('Codigo_Libro y Titulo_Libro son obligatorios');
      });
    });
  });

  it('3. Debe registrar un nuevo libro en el catalogo con rol de bibliotecario (201 Created)', () => {
    cy.loginBibliotecario().then((tokenAdmin) => {
      cy.request({
        method: 'POST',
        url: '/api/libros',
        headers: { Authorization: `Bearer ${tokenAdmin}` },
        body: libroPrueba
      }).then((res) => {
        expect(res.status).to.eq(201);
        expect(res.body).to.have.property('libro');
        expect(res.body.libro).to.have.property('Codigo_Libro', libroPrueba.Codigo_Libro);
        expect(res.body.libro).to.have.property('Titulo_Libro', libroPrueba.Titulo_Libro);
      });
    });
  });

  it('4. Debe consultar el libro registrado en el catalogo (200 OK)', () => {
    cy.request({
      method: 'GET',
      url: `/api/libros/${libroPrueba.Codigo_Libro}`
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.libro.Codigo_Libro).to.eq(libroPrueba.Codigo_Libro);
    });
  });

  it('5. Debe modificar la informacion del libro registrado (200 OK) e invalidar el cache', () => {
    cy.loginBibliotecario().then((tokenAdmin) => {
      // Calentar cache
      cy.request({ method: 'GET', url: '/api/libros' });

      // Actualizar libro
      cy.request({
        method: 'PUT',
        url: `/api/libros/${libroPrueba.Codigo_Libro}`,
        headers: { Authorization: `Bearer ${tokenAdmin}` },
        body: {
          Titulo_Libro: 'Arquitectura de Software y Pruebas Automatizadas (Edicion Ampliada)'
        }
      }).then((res) => {
        expect(res.status).to.eq(200);
        expect(res.body.libro.Titulo_Libro).to.include('Edicion Ampliada');

        // Verificar que la siguiente consulta al catalogo es un MISS por invalidacion
        cy.request({
          method: 'GET',
          url: '/api/libros'
        }).then((catRes) => {
          expect(catRes.status).to.eq(200);
          expect(catRes.headers['x-cache']).to.eq('MISS');
        });
      });
    });
  });

  it('6. Debe eliminar el libro del catalogo exitosamente (200 OK)', () => {
    cy.loginBibliotecario().then((tokenAdmin) => {
      cy.request({
        method: 'DELETE',
        url: `/api/libros/${libroPrueba.Codigo_Libro}`,
        headers: { Authorization: `Bearer ${tokenAdmin}` }
      }).then((res) => {
        expect(res.status).to.eq(200);

        // Comprobar que ya no existe (404 Not Found)
        cy.request({
          method: 'GET',
          url: `/api/libros/${libroPrueba.Codigo_Libro}`,
          failOnStatusCode: false
        }).then((verifyRes) => {
          expect(verifyRes.status).to.eq(404);
        });
      });
    });
  });

});
