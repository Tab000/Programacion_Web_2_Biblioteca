describe('3.3. Inicio de Sesión y Permisos', () => {

  it('1. Debe iniciar sesion exitosamente con credenciales validas de estudiante', () => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        identificador: 'usuario.a@test.com',
        Password: 'UserPass123'
      }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body).to.have.property('access_token');
      expect(res.body).to.have.property('tipo_token', 'Bearer');
      expect(res.body).to.have.property('rol', 'usuario');
      expect(res.body).to.have.property('usuario');
    });
  });

  it('2. Debe rechazar inicio de sesion con credenciales incorrectas (401 Unauthorized)', () => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        identificador: 'usuario.a@test.com',
        Password: 'PasswordEquivocado999'
      },
      failOnStatusCode: false
    }).then((res) => {
      expect(res.status).to.eq(401);
      expect(res.body).to.have.property('error', 'Credenciales invalidas');
    });
  });

  it('3. Debe rechazar peticion a endpoint protegido sin token Bearer (401 Unauthorized)', () => {
    cy.request({
      method: 'GET',
      url: '/api/auth/perfil',
      failOnStatusCode: false
    }).then((res) => {
      expect(res.status).to.eq(401);
      expect(res.body).to.have.property('error', 'Acceso no autorizado');
      expect(res.body.mensaje).to.include('Se requiere un token JWT');
    });
  });

  it('4. Debe acceder a /api/auth/perfil con token valido y retornar datos del usuario', () => {
    cy.loginUsuario().then((token) => {
      cy.request({
        method: 'GET',
        url: '/api/auth/perfil',
        headers: {
          Authorization: `Bearer ${token}`
        }
      }).then((res) => {
        expect(res.status).to.eq(200);
        expect(res.body).to.have.property('rol', 'usuario');
        expect(res.body).to.have.property('usuario');
        expect(res.body.usuario).to.have.property('Email_Usuario', 'usuario.a@test.com');
      });
    });
  });

  it('5. Debe autenticar bibliotecario con endpoint dedicado y emitir rol bibliotecario', () => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login-bibliotecario',
      body: {
        identificador: 'biblio.seguridad@test.com',
        Password: 'AdminPass123'
      }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body).to.have.property('rol', 'bibliotecario');
      expect(res.body).to.have.property('access_token');
    });
  });

  it('6. Debe impedir que un estudiante consulte o modifique perfiles ajenos (Aislamiento 403)', () => {
    cy.loginUsuario('usuario.a@test.com', 'UserPass123').then((token) => {
      cy.request({
        method: 'GET',
        url: '/api/usuarios/USR_SEC_B',
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false
      }).then((res) => {
        expect(res.status).to.eq(403);
        expect(res.body).to.have.property('error', 'Acceso denegado (403)');
      });
    });
  });

  it('7. Debe registrar un nuevo Estudiante o Docente y emitir JWT con claims', () => {
    const timestamp = Date.now();
    cy.request({
      method: 'POST',
      url: '/api/auth/registro',
      body: {
        Codigo_Usuario: `CY_EST_${timestamp}`,
        Nombre_Usuario: `Estudiante Cypress ${timestamp}`,
        Email_Usuario: `cy_est_${timestamp}@universidad.edu.co`,
        Password: 'Password123',
        Tipo_Usuario: 'Estudiante',
        Facultad: 'Facultad de Ingeniería'
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('access_token');
      expect(res.body).to.have.property('rol', 'usuario');
      expect(res.body).to.have.property('tipo_usuario', 'Estudiante');
    });
  });

  it('8. Debe registrar un nuevo Bibliotecario y emitir JWT con rol de administrador', () => {
    const timestamp = Date.now();
    cy.request({
      method: 'POST',
      url: '/api/auth/registro-bibliotecario',
      body: {
        Codigo_Bibliotecario: `CY_BIB_${timestamp}`,
        Nombre_Bibliotecario: `Bibliotecario Cypress ${timestamp}`,
        Email_Bibliotecario: `cy_bib_${timestamp}@universidad.edu.co`,
        Password: 'AdminPassword123',
        Turno: 'Mañana'
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('access_token');
      expect(res.body).to.have.property('rol', 'bibliotecario');
      expect(res.body).to.have.property('tipo_usuario', 'Bibliotecario');
    });
  });

  it('9. Debe iniciar sesion con los 3 perfiles demo precargados (Estudiante, Docente, Bibliotecario)', () => {
    // 1. Estudiante
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: { identificador: 'estudiante@universidad.edu.co', Password: 'Password123' }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.rol).to.eq('usuario');
      expect(res.body.tipo_usuario).to.eq('Estudiante');
    });

    // 2. Docente
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: { identificador: 'docente@universidad.edu.co', Password: 'Password123' }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.rol).to.eq('usuario');
      expect(res.body.tipo_usuario).to.eq('Docente');
    });

    // 3. Bibliotecario
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: { identificador: 'bibliotecario@universidad.edu.co', Password: 'AdminPassword123' }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.rol).to.eq('bibliotecario');
      expect(res.body.tipo_usuario).to.eq('Bibliotecario');
    });
  });

});
