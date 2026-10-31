"""Checks for the local Compose contract without starting containers."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ComposeConfigTests(unittest.TestCase):
    def compose(self, *args, extra_env=None):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env") as env_file:
            env_file.write("DB_PASSWORD=test-password\nSECRET_KEY=test-secret\nINTERNAL_API_TOKEN=test-internal\n")
            env_file.flush()
            env = {key: value for key, value in os.environ.items() if key not in {
                "DB_PASSWORD", "SECRET_KEY", "INTERNAL_API_TOKEN", "DB_PORT", "DB_PUBLISHED_PORT",
                "APP_PORT", "AUTH_DB_NAME", "SCHEDULE_DB_NAME", "TECHCARD_DB_NAME", "DB_NAME",
            }}
            env.update(extra_env or {})
            result = subprocess.run(
                ["docker", "compose", "--env-file", env_file.name, *args, "config", "--format", "json"],
                cwd=ROOT, env=env, text=True, capture_output=True, check=True,
            )
            return json.loads(result.stdout)

    def test_default_only_publishes_loopback_gateway(self):
        services = self.compose()["services"]
        for name in ("db", "auth", "schedule", "techcard", "frontend"):
            self.assertFalse(services[name].get("ports"), name)
        port = services["nginx"]["ports"][0]
        self.assertEqual((port["host_ip"], port["published"], port["target"]), ("127.0.0.1", "8080", 80))

    def test_db_names_and_port_are_consistent(self):
        services = self.compose(extra_env={"DB_PUBLISHED_PORT": "5544", "SCHEDULE_DB_NAME": "classes"})["services"]
        self.assertEqual(services["db"]["environment"]["SCHEDULE_DB_NAME"], "classes")
        self.assertEqual(services["schedule"]["environment"]["DB_NAME"], "classes")
        for name in ("auth", "schedule", "techcard"):
            self.assertEqual(str(services[name]["environment"]["DB_PORT"]), "5432")

    def test_debug_ports_are_loopback_and_separate(self):
        config = self.compose("-f", "docker-compose.yml", "-f", "docker-compose.debug.yml", extra_env={"DB_PUBLISHED_PORT": "5544"})
        port = config["services"]["db"]["ports"][0]
        self.assertEqual((port["host_ip"], port["published"], port["target"]), ("127.0.0.1", "5544", 5432))

    def test_tunnel_profile_exists(self):
        self.assertIn("ngrok", self.compose("--profile", "tunnel")["services"])

    def test_missing_database_password_is_rejected(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env") as env_file:
            env_file.write("DB_PASSWORD=\nSECRET_KEY=test-secret\nINTERNAL_API_TOKEN=test-internal\n")
            env_file.flush()
            env = os.environ.copy()
            env.pop("DB_PASSWORD", None)
            result = subprocess.run(
                ["docker", "compose", "--env-file", env_file.name, "config", "--quiet"],
                cwd=ROOT, env=env, text=True, capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("DB_PASSWORD", result.stderr)


if __name__ == "__main__":
    unittest.main()
