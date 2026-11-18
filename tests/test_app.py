import unittest
from app import create_app
from app.models import db, Item


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SECRET_KEY = "test-secret-key"
    PORT = 5000
    HOST = "127.0.0.1"
    PLATFORM = "Unit Test Environment"
    APP_ENV = "testing"
    IS_MYSQL = False


class ApplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_healthz_endpoint(self):
        """Verify /healthz returns 200 and healthy status."""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["database"]["connected"])

    def test_index_page_renders(self):
        """Verify index HTML dashboard renders."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Deployment Workshop", response.data)

    def test_create_item_via_form(self):
        """Verify web form submission creates record."""
        response = self.client.post(
            "/items",
            data={
                "title": "Test Deployment",
                "category": "Testing",
                "description": "Integration test item",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            item = Item.query.filter_by(title="Test Deployment").first()
            self.assertIsNotNone(item)
            self.assertEqual(item.category, "Testing")

    def test_api_endpoints(self):
        """Verify REST API GET and POST."""
        # Create item via API
        post_res = self.client.post(
            "/api/items",
            json={
                "title": "API Test",
                "description": "JSON API verification",
                "category": "API",
            },
        )
        self.assertEqual(post_res.status_code, 201)
        created_id = post_res.get_json()["data"]["id"]

        # List items via API
        get_res = self.client.get("/api/items")
        self.assertEqual(get_res.status_code, 200)
        data = get_res.get_json()
        self.assertGreaterEqual(data["count"], 1)

    def test_info_api(self):
        """Verify system info API returns platform and database diagnostics."""
        res = self.client.get("/api/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("diagnostics", data)
        self.assertIn("database", data)


if __name__ == "__main__":
    unittest.main()
