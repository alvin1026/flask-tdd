# flask-tdd

This is a simple RESTful service using Python Flask and PostgreSQL. The resource model is persistence using SQLAlchemy to keep the application simple.

## Bring up the development environment

### Using docker-compose file
```shell
docker-compose up -d
```

## Running the tests

Run the unit tests using `pytest`
```shell
make test
```

PyTest is configured to automatically run the `coverage` tool and you should see a percentage-of-coverage report at the end of your tests. If you want to see what lines of code were not tested, use:
```shell
coverage report -m
```

This is particularly useful because it reports the line numbers for the code that have not been covered so you know which lines you want to target with new test cases to get higher code coverage.

You can also manually run `pytest` with `coverage` (but settings in `pyproject.toml` do this already)
```shell
$ pytest --pspec --cov=service --cov-fail-under=95
```

It's also a good idea to make sure that your Python code follows the PEP8 standard. Both `flake8` and `pylint` have been included in the `pyproject.toml` file so that you can check if your code is compliant like this:
```shell
make lint
```
Which does the equivalent of these commands:
```shell
flake8 service tests --count --select=E9,F63,F7,F82 --show-source --statistics --ignore=F401
flake8 service tests --count --max-complexity=10 --max-line-length=127 --statistics
pylint service tests --max-line-length=127  --disable=R0801
```
