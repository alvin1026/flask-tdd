"""
Test routes for Employee API Service
"""
import os
import logging
from unittest import TestCase
from unittest.mock import patch, MagicMock  # noqa: F401

# from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus  # noqa: F401
from wsgi import app

from service.common import status
from service.models import Employee, db, DataValidationError  # noqa: F401
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
        """It should call the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Employee Demo REST API Service")

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_get_employee_list(self):
        """It should Get a list of Employees"""
        self._create_employees(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_employee(self):
        """It should Get a single employee"""
        # get the id of an employee
        test_employee = self._create_employees(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_employee.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["first_name"], test_employee.first_name)
        self.assertEqual(data["last_name"], test_employee.last_name)

    def test_get_employee_not_found(self):
        """It should not Get an Employee that's not found"""
        response = self.client.get(F"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_create_employee(self):
        """It should Create a new Employee"""
        test_employee = EmployeeFactory()
        logging.debug("Test Employee: %s", test_employee.serialize())
        response = self.client.post(BASE_URL, json=test_employee.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        logging.debug("Location = %s", location)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_employee = response.get_json()
        self.assertEqual(new_employee["first_name"], test_employee.first_name)
        self.assertEqual(new_employee["last_name"], test_employee.last_name)
        self.assertEqual(new_employee["department"], test_employee.department)
        self.assertEqual(new_employee["gender"], test_employee.gender.name)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_employee = response.get_json()
        self.assertEqual(new_employee["first_name"], test_employee.first_name)
        self.assertEqual(new_employee["last_name"], test_employee.last_name)
        self.assertEqual(new_employee["department"], test_employee.department)
        self.assertEqual(new_employee["gender"], test_employee.gender.name)

    def test_delete_employee(self):
        """It should Delete an Employee"""
        test_employee = self._create_employees(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_employee.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_employee.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestSadPath(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_method_not_allowed(self):
        """It should not allow update without a employee id"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_employee_no_data(self):
        """It should not Create an Employee with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_no_content_type(self):
        """It should not Create an Employee with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_employee_wrong_content_type(self):
        """It should not Create en Employee with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
