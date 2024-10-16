import os
import logging
from datetime import date
from enum import Enum
from retry import retry
from flask_sqlalchemy import SQLAlchemy

# global variables for retry (must be int)
RETRY_COUNT = int(os.environ.get("RETRY_COUNT", 5))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", 1))
RETRY_BACKOFF = int(os.environ.get("RETRY_BACKOFF", 2))

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


@retry(Exception, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
def init_db() -> None:
    """Initialize Tables"""
    db.create_all()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing"""


class Gender(Enum):
    """Enumeration of valid Employee Genders"""

    MALE = 0
    FEMALE = 1
    UNKNOWN = 3


class Employee(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255), nullable=False)
    gender = db.Column(
        db.Enum(Gender), nullable=False, server_default=(Gender.UNKNOWN.name)
    )
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    last_updated = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)

    def __repr__(self):
        return f"<Employee {self.first_name} {self.last_name} id=[{self.id}]>"

    def create(self) -> None:
        logger.info("Creating %s %s", self.first_name, self.last_name)
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self) -> None:
        logger.info("Saving %s %s", self.first_name, self.last_name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    @classmethod
    def all(cls) -> list:
        logger.info("Processing all Employees")
        return cls.query.all()

