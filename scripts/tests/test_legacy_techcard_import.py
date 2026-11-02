"""Tests for resolving the legacy importer target from Docker Compose."""

import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "legacy_techcard_import", ROOT / "scripts/import_legacy_techcard_sqlite.py"
)
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


def compose_config(postgres_user="crm_user", database_name="crm_cards", service_database=None):
    return {
        "services": {
            "db": {
                "environment": {
                    "POSTGRES_USER": postgres_user,
                    "TECHCARD_DB_NAME": service_database or database_name,
                }
            },
            "techcard": {"environment": {"TECHCARD_DB_NAME": database_name}},
        }
    }


class PostgresTargetTests(unittest.TestCase):
    def test_reads_user_and_database_from_resolved_compose_configuration(self):
        config = compose_config()
        result = subprocess.CompletedProcess(
            args=["docker", "compose", "config"],
            returncode=0,
            stdout=json.dumps(config),
            stderr="",
        )
        with patch.object(importer.subprocess, "run", return_value=result) as run:
            target = importer.postgres_target("docker", ROOT)

        self.assertEqual(target, ("crm_user", "crm_cards"))
        run.assert_called_once_with(
            ["docker", "compose", "config", "--format", "json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_rejects_mismatched_database_names_between_services(self):
        config = compose_config(service_database="other_cards")
        result = subprocess.CompletedProcess(
            args=["docker", "compose", "config"],
            returncode=0,
            stdout=json.dumps(config),
            stderr="",
        )
        with patch.object(importer.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(ValueError, "differs"):
                importer.postgres_target("docker", ROOT)

    def test_reports_compose_configuration_failure(self):
        result = subprocess.CompletedProcess(
            args=["docker", "compose", "config"], returncode=1, stdout="", stderr="invalid .env"
        )
        with patch.object(importer.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "invalid .env"):
                importer.postgres_target("docker", ROOT)


if __name__ == "__main__":
    unittest.main()
