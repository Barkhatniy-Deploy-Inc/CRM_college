"""Verify documented make targets use the Docker-backed workflow."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


class MakeTargetsTests(unittest.TestCase):
    def test_migrate_uses_compose_workflow(self):
        output = subprocess.check_output(["make", "-n", "migrate"], cwd=ROOT, text=True)
        self.assertIn("./scripts/local.sh migrate", output)
        self.assertNotIn("cd backend/", output)

    def test_smoke_uses_gateway(self):
        output = subprocess.check_output(["make", "-n", "smoke"], cwd=ROOT, text=True)
        self.assertIn("./scripts/local.sh check", output)

    def test_security_covers_every_dependency_manifest(self):
        output = subprocess.check_output(["make", "-n", "security"], cwd=ROOT, text=True)
        for requirements in (
            "backend/auth/requirements.txt",
            "backend/schedule/requirements.txt",
            "backend/techcard/requirements.txt",
            "backend/common/requirements-dev.txt",
        ):
            self.assertIn(requirements, output)
        self.assertIn("npm run test:dependency-audit", output)
        self.assertIn("status=1", output)


if __name__ == "__main__":
    unittest.main()
