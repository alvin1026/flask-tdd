"""
Driver Service

This service implements a REST API that allows user to Create, Read, Update
and Delete Drivers from the online ride-sharing application.
"""

from flask import jsonify, request, url_for, abort  # noqa: F401
from flask import current_app as app
from service.models import Employee
from service.common import status


@app.route("/health")
def health_check():
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


@app.route("/")
def index():
    """Root URL response"""

    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Employee Demo REST API Service",
            version="1.0",
            paths=url_for("list_employees", _external=True),
        ),
        status.HTTP_200_OK,
    )


@app.route("/employees", methods=["GET"])
def list_employees():
    """Returns all Employees"""
    app.logger.info("Request for employee list")
    employees = Employee.all()

    results = [employee.serialize() for employee in employees]
    app.logger.info("Returning %d employees", len(results))
    return jsonify(results), status.HTTP_200_OK


@app.route("/employees/<int:employee_id>", methods=["GET"])
def get_employees(employee_id):
    """
    Retrieve a single Employee

    This endpoint will return an Employee based on its id
    """
    app.logger.info("Request to Retrieve an employee with id [%s]", employee_id)

    # Attempt to find the Employee and abort if not found
    employee = Employee.find(employee_id)
    if not employee:
        abort(status.HTTP_404_NOT_FOUND, f"Employee with id '{employee_id}' was not found.")

    app.logger.info("Returning employee: %s %s", employee.first_name, employee.last_name)
    return jsonify(employee.serialize()), status.HTTP_200_OK


@app.route("/employees", methods=["POST"])
def create_employees():
    """
    Create an Employee
    This endpoint will create an Employee based on the data in the body that is posted
    """
    app.logger.info("Request to Create an Employee...")
    check_content_type("application/json")

    employee = Employee()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    employee.deserialize(data)

    employee.create()
    app.logger.info("Employee with new id [%s] saved!", employee.id)

    # Return the location of the new Employee
    location_url = url_for("get_employees", employee_id=employee.id, _external=True)
    return jsonify(employee.serialize()), status.HTTP_201_CREATED, {"location": location_url}


@app.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employees(employee_id):
    """
    Delete an Employee

    This endpoint will delete an Employee based on the id specified in the path
    """
    app.logger.info("Request to Delete an Employee with id [%s]", employee_id)

    # Delete the Employee if it exists
    employee = Employee.find(employee_id)
    if employee:
        app.logger.info("Employee with ID: %d found.", employee.id)
        employee.delete()

    app.logger.info("Employee with ID: %d delete complete.", employee_id)
    return {}, status.HTTP_204_NO_CONTENT


def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
