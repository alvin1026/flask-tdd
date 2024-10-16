from datetime import date  # noqa: F401

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate  # noqa: F401
from service.models import Employee, Gender


class EmployeeFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Employee

    id = factory.Sequence(lambda n: n)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    department = FuzzyChoice(choices=["Finance", "Engineering", "HR", "Marketing"])
    gender = FuzzyChoice(choices=[Gender.MALE, Gender.FEMALE, Gender.UNKNOWN])
    # birthday = FuzzyDate(date(2008, 1, 1))
