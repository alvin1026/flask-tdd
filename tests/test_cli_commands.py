"""
CLI Command Extensions for Flask
"""

import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

# pylint: disable=unused-import
from wsgi import app  # noqa: F401
from service.common.cli_commands import db_create  # noqa: E402


class TestFlaskCLI(TestCase):
    """Flask CLI Command Tests"""

    def setUp(self):
        # This sets up a CliRunner, a helper class provided by Click (which Flask uses for CLI commands) to
        # simulate command-line invocations. This is called before each test method is executed.
        self.runner = CliRunner()

    @patch("service.common.cli_commands.db")
    def test_db_create(self, db_mock):
        """It should call the db-create command"""
        db_mock.return_value = MagicMock()
        with patch.dict(os.environ, {"FLASK_APP": "wsgi:app"}, clear=True):
            result = self.runner.invoke(db_create)
            self.assertEqual(result.exit_code, 0)
