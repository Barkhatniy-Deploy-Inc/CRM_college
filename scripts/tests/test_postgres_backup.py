"""Safety checks for the PostgreSQL backup command."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("postgres_backup", ROOT / "scripts/postgres_backup.py")
backup_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup_module)


class BackupTests(unittest.TestCase):
    def test_refuses_existing_directory_before_running_docker(self):
        with tempfile.TemporaryDirectory() as parent, patch.object(backup_module.subprocess, "run") as run:
            with self.assertRaises(FileExistsError):
                backup_module.backup(Path(parent))
            run.assert_not_called()

    def test_rejects_duplicate_database_names(self):
        config = {"services": {"db": {"environment": {
            "POSTGRES_USER": "postgres", "AUTH_DB_NAME": "same", "SCHEDULE_DB_NAME": "same", "TECHCARD_DB_NAME": "cards",
        }}}}
        with self.assertRaisesRegex(ValueError, "distinct"):
            backup_module.database_names(config)


if __name__ == "__main__":
    unittest.main()
