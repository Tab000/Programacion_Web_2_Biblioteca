// Comandos personalizados para pruebas automatizadas con Cypress

Cypress.Commands.add('loginUsuario', (identificador = 'usuario.a@test.com', password = 'UserPass123') => {
  return cy.request({
    method: 'POST',
    url: '/api/auth/login',
    body: {
      identificador,
      Password: password
    },
    failOnStatusCode: false
  }).then((response) => {
    return response.body.access_token;
  });
});

Cypress.Commands.add('loginBibliotecario', (identificador = 'biblio.seguridad@test.com', password = 'AdminPass123') => {
  return cy.request({
    method: 'POST',
    url: '/api/auth/login-bibliotecario',
    body: {
      identificador,
      Password: password
    },
    failOnStatusCode: false
  }).then((response) => {
    return response.body.access_token;
  });
});
