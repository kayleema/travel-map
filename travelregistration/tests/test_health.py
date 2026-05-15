import json
from unittest.mock import patch

from django.test import RequestFactory
from django.test import TestCase

from travelregistration.views import health


class HealthViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_health_returns_operational_json(self):
        response = health(self.factory.get("/health"))
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(data["status"], "ok")
        self.assertIn("checked_at", data)
        self.assertIn("hostname", data)
        self.assertIn("platform", data)
        self.assertIn("load_average", data)
        self.assertIn("memory", data)
        self.assertIn("system", data["memory"])
        self.assertIn("process", data["memory"])
        self.assertIn("pid", data["process"])
        self.assertIn("uptime_seconds", data["process"])
        # self.assertIn("python", data["runtime"])
        # self.assertIn("django", data["runtime"])
        self.assertTrue(data["database"]["ok"])
        self.assertIn("vendor", data["database"])

    def test_health_reports_degraded_when_database_check_fails(self):
        database_health = {
            "ok": False,
            "vendor": "sqlite",
            "error": "OperationalError",
        }

        with patch("travelregistration.views._get_database_health", return_value=database_health):
            response = health(self.factory.get("/health"))

        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "degraded")
        self.assertEqual(data["database"]["error"], "OperationalError")
