import os
import logging
from unittest import TestCase
from unittest.mock import patch, MagicMock  # noqa: F401

# from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus  # noqa: F401
from wsgi import app

# from service import create_app
from service.common import status
from service.models import Employee, Gender, db, DataValidationError  # noqa: F401
from tests.factories import EmployeeFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/employees"


class TestEmployeeService(TestCase):
    """Employee Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        """Runs for each test"""
        self.client = app.test_client()
        db.session.query(Employee).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_employees(self, count: int = 1) -> list:
        """Utility function to bulk create employees"""
        employees = []
        for _ in range(count):
            test_employee = EmployeeFactory()
            response = self.client.post(BASE_URL, json=test_employee.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test employee"
            )
            new_employee = response.get_json()
            test_employee.id = new_employee["id"]
            employees.append(test_employee)
        return employees

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Employee Demo REST API Service")

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def get_employee_list(self):
        self._create_employees(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
