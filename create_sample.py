"""
Script to create sample data and write to json file.
"""
import json

from tests.factories import EmployeeFactory


def generate():
    """Generate sample data"""
    employees = []

    for _ in range(10):
        employee = EmployeeFactory()
        employee_dict = employee.serialize()
        employee_dict.pop("id", None)
        employees.append(employee_dict)

    with open("sample_employees.json", "w") as file:
        json.dump(employees, file, indent=4)


if __name__ == "__main__":
    generate()
