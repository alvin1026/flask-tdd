import os
import logging
from unittest import TestCase
from unittest.mock import patch  # noqa: F401
from datetime import date  # noqa: F401
from wsgi import app
from service.models import Employee, Gender, DataValidationError, db
from tests.factories import EmployeeFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


class TestCaseBase(TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        db.session.query(Employee).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()


class TestEmployeeModel(TestCaseBase):

    def test_create_an_employee(self):
        employee = Employee(first_name="John", last_name="Daniel", gender=Gender.MALE, department="Engineering")
        self.assertEqual(str(employee), "<Employee John Daniel id=[None]>")
        self.assertTrue(employee is not None)
        self.assertEqual(employee.id, None)
        self.assertEqual(employee.department, "Engineering")
        self.assertEqual(employee.gender, Gender.MALE)
        employee = Employee(first_name="Kate", last_name="Jess", gender=Gender.FEMALE, department="Finance")
        self.assertEqual(employee.gender, Gender.FEMALE)

    def test_add_an_employee(self):
        employees = Employee.all()
        self.assertEqual(employees, [])
        employee = Employee(first_name="John", last_name="Daniel", gender=Gender.MALE, department="Engineering")
        self.assertTrue(employee is not None)
        self.assertEqual(employee.id, None)
        employee.create()
        self.assertIsNotNone(employee.id)
        employees = Employee.all()
        self.assertEqual(len(employees), 1)

    def test_update_an_employee(self):

        employee = EmployeeFactory()
        logging.debug(employee)
        employee.id = None
        employee.create()
        logging.debug(employee)
        self.assertIsNotNone(employee.id)
        employee.department = "HR"
        original_id = employee.id
        employee.update()
        self.assertEqual(employee.id, original_id)
        self.assertEqual(employee.department, "HR")
        employees = Employee.all()
        self.assertEqual(len(employees), 1)
        self.assertEqual(employees[0].id, original_id)
        self.assertEqual(employees[0].department, "HR")

    def test_update_no_id(self):
        employee = EmployeeFactory()
        logging.debug(employee)
        employee.id = None
        self.assertRaises(DataValidationError, employee.update)


class TestModelQueries(TestCaseBase):
    """Employee Model Query Tests"""

    def test_find_employee(self):
        """It should find an Employee by ID"""
        employees = EmployeeFactory.create_batch(5)
        for employee in employees:
            employee.create()
        logging.debug(employees)
        # Make sure they got saved
        self.assertEqual(len(Employee.all()), 5)
        # find the 2nd employee in the list
        employee = Employee.find(employees[1].id)
        self.assertIsNot(employee, None)
        self.assertEqual(employee.id, employees[1].id)
        self.assertEqual(employee.first_name, employees[1].first_name)
        self.assertEqual(employee.last_name, employees[1].last_name)
        self.assertEqual(employee.department, employees[1].department)
        self.assertEqual(employee.gender, employees[1].gender)


class TestExceptionHandlers(TestCaseBase):

    @patch("service.models.db.session.commit")
    def test_create_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        employee = EmployeeFactory()
        self.assertRaises(DataValidationError, employee.create)

    @patch("service.models.db.session.commit")
    def test_update_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        employee = EmployeeFactory()
        self.assertRaises(DataValidationError, employee.update)

    @patch("service.models.db.session.commit")
    def test_delete_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        employee = EmployeeFactory()
        self.assertRaises(DataValidationError, employee.delete)

