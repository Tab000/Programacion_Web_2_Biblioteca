// Importar comandos personalizados
import './commands';

// Ocultar errores no capturados del navegador durante las pruebas si fuera necesario
Cypress.on('uncaught:exception', (err, runnable) => {
  return false;
});
