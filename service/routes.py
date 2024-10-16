"""
Driver Service

This service implements a REST API that allows user to Create, Read, Update
and Delete Drivers from the online ride-sharing application.
"""

from flask import jsonify, request, url_for, abort  # noqa: F401
from flask import current_app as app
from service.models import Employee, Gender
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


@app.route("/drivers", methods=["GET"])
def list_employees():
    """Returns all Employees"""
    app.logger.info("Request for employee list")

    employees = []

    # Parse any arguments from the query string

    department = request.args.get("department")
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    gender = request.args.get("gender")

    if department:
        app.logger.info("Find by department: %s", department)
        employees = Employee.find_by_departmnet(department)
    elif first_name:
        app.logger.info("Find by first name: %s", first_name)
        employees = Employee.find_by_first_name(first_name)
    elif last_name:
        app.logger.info("Find by last name: %s", last_name)
        employees = Employee.find_by_last_name(last_name)
    elif gender:
        app.logger.info("Find by gender: %s", gender)
        # create enum from string
        employees = Employee.find_by_gender(Gender[gender.upper()])
    else:
        app.logger.info("Find all")
        employees = Employee.all()

    results = [employee.serailize() for employee in employees]
    app.logger.info("Returning %d employees", len(results))
    return jsonify(results), status.HTTP_200_OK
