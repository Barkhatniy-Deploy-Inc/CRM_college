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


if __name__ == "__main__":
    unittest.main()
