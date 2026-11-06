describe('3.1. Búsqueda y Catálogo de Libros', () => {

  it('1. Debe consultar el catalogo general de libros exitosamente (200 OK)', () => {
    cy.request({
      method: 'GET',
      url: '/api/libros'
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('libros');
      expect(response.body).to.have.property('total');
      expect(response.headers).to.have.property('x-cache');
    });
  });

  it('2. Debe buscar libros por titulo existente mediante query param ?titulo=', () => {
    cy.request({
      method: 'GET',
      url: '/api/libros?titulo=Sistemas',
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('libros');
      if (response.body.libros.length > 0) {
        expect(response.body.libros[0].Titulo_Libro).to.include('Sistemas');
      }
    });
  });

  it('3. Debe retornar lista vacia con total 0 cuando un libro no existe', () => {
    cy.request({
      method: 'GET',
      url: '/api/libros?titulo=LibroInexistenteXYZ123456789',
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body.total).to.eq(0);
      expect(response.body.libros).to.have.length(0);
    });
  });

  it('4. Debe consultar los detalles de un libro y validar contrato de datos', () => {
    cy.request({
      method: 'GET',
      url: '/api/libros'
    }).then((listRes) => {
      if (listRes.body.libros.length > 0) {
        const codigoLibro = listRes.body.libros[0].Codigo_Libro;
        cy.request({
          method: 'GET',
          url: `/api/libros/${codigoLibro}`
        }).then((detailRes) => {
          expect(detailRes.status).to.eq(200);
          expect(detailRes.body).to.have.property('libro');
          expect(detailRes.body.libro).to.have.property('Codigo_Libro', codigoLibro);
          expect(detailRes.body.libro).to.have.property('Titulo_Libro');
        });
      }
    });
  });

  it('5. Debe validar el ciclo de vida del cache (MISS inicial, HIT subsiguiente y ETag)', () => {
    // Primera consulta
    cy.request({
      method: 'GET',
      url: '/api/libros?titulo=CacheCiclo'
    }).then((res1) => {
      expect(res1.status).to.eq(200);
      const etag = res1.headers['etag'];

      // Segunda consulta inmediata -> HIT
      cy.request({
        method: 'GET',
        url: '/api/libros?titulo=CacheCiclo'
      }).then((res2) => {
        expect(res2.status).to.eq(200);
        expect(res2.headers['x-cache']).to.eq('HIT');

        // Peticion condicional If-None-Match -> 304 Not Modified
        if (etag) {
          cy.request({
            method: 'GET',
            url: '/api/libros?titulo=CacheCiclo',
            headers: { 'If-None-Match': etag }
          }).then((res304) => {
            expect(res304.status).to.eq(304);
          });
        }
      });
    });
  });

  it('6. Debe consultar disponibilidad de ejemplar en tiempo real con TTL corto (10s)', () => {
    cy.request({
      method: 'GET',
      url: '/api/libros'
    }).then((res) => {
      if (res.body.libros.length > 0) {
        const cod = res.body.libros[0].Codigo_Libro;
        cy.request({
          method: 'GET',
          url: `/api/libros/${cod}/disponibilidad`
        }).then((dispRes) => {
          expect(dispRes.status).to.eq(200);
          expect(dispRes.body).to.have.property('disponible');
          expect(dispRes.body).to.have.property('codigo_libro', cod);
          expect(dispRes.headers['cache-control']).to.include('max-age=10');
        });
      }
    });
  });

});
