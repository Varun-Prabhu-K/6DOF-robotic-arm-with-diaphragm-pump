import unittest
import json
from app import app


class TestAppEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"6-DOF Robotic Arm Control Dashboard", response.data)

    def test_ports_endpoint(self):
        response = self.client.get("/api/ports")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_status_endpoint(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("connected", data)
        self.assertIn("port", data)

    def test_command_when_disconnected(self):
        response = self.client.post(
            "/api/command",
            json={"kind": "joint", "channel": 0, "angle": 90}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get("ok"))
        self.assertIn("not connected", data.get("message", "").lower())

    def test_invalid_connect_payload(self):
        response = self.client.post("/api/connect", json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get("ok"))


if __name__ == "__main__":
    unittest.main()
