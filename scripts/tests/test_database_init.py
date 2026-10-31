"""Validate database initialization before any SQL is run."""
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


class DatabaseInitTests(unittest.TestCase):
    def test_refuses_duplicate_database_names(self):
        env = os.environ | {"AUTH_DB_NAME": "same", "SCHEDULE_DB_NAME": "same", "TECHCARD_DB_NAME": "cards", "POSTGRES_USER": "postgres"}
        result = subprocess.run(["sh", str(ROOT / "db-init/01-create-databases.sh")], env=env, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("distinct", result.stderr)


if __name__ == "__main__":
    unittest.main()
