import unittest
from app import app

class TestSeguridadCORS(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_01_origen_permitido_recibe_cors_headers(self):
        """Verifica que un frontend autorizado reciba la cabecera Access-Control-Allow-Origin."""
        res = self.client.get(
            "/api/paises",
            headers={"Origin": "http://localhost:5173"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.headers.get("Access-Control-Allow-Origin"),
            "http://localhost:5173"
        )
        self.assertEqual(
            res.headers.get("Access-Control-Allow-Credentials"),
            "true"
        )

    def test_02_preflight_options_autorizado(self):
        """Verifica que el preflight OPTIONS devuelva metodos y cabeceras permitidos."""
        res = self.client.options(
            "/api/libros",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("POST", res.headers.get("Access-Control-Allow-Methods", ""))
        self.assertIn("Authorization", res.headers.get("Access-Control-Allow-Headers", ""))
        self.assertEqual(res.headers.get("Access-Control-Max-Age"), "86400")

    def test_03_origen_no_autorizado_es_rechazado(self):
        """Verifica que un dominio desconocido o malicioso NO reciba cabecera CORS."""
        res = self.client.get(
            "/api/paises",
            headers={"Origin": "http://sitio-malicioso.com"}
        )
        # El navegador bloquea la lectura porque no se devuelve Access-Control-Allow-Origin
        self.assertIsNone(res.headers.get("Access-Control-Allow-Origin"))

if __name__ == "__main__":
    unittest.main()
