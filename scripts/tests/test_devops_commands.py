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

    def test_security_audits_every_requirements_file(self):
        output = subprocess.check_output(["make", "-n", "security"], cwd=ROOT, text=True)
        recipe = output.split("security:", 1)[1] if "security:" in output else output
        for req in (
            "backend/auth/requirements.txt",
            "backend/schedule/requirements.txt",
            "backend/techcard/requirements.txt",
            "backend/common/requirements-dev.txt",
        ):
            self.assertIn(req, recipe)
        self.assertIn("npm run test:prod-audit", recipe)

    def test_security_reports_any_failed_audit(self):
        output = subprocess.check_output(["make", "-n", "security"], cwd=ROOT, text=True)
        recipe = output.split("security:", 1)[1] if "security:" in output else output
        self.assertIn("status=1", recipe)
        self.assertRegex(recipe, r"exit \$+status")


if __name__ == "__main__":
    unittest.main()
