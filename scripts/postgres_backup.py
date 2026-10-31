#!/usr/bin/env python3
"""Dump each Compose PostgreSQL database to a new private directory."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ["docker", "compose"]


def database_names(config):
    env = config["services"]["db"]["environment"]
    names = {name: env[key] for name, key in (
        ("auth", "AUTH_DB_NAME"), ("schedule", "SCHEDULE_DB_NAME"), ("techcard", "TECHCARD_DB_NAME"),
    )}
    if any(not value for value in names.values()) or len(set(names.values())) != len(names):
        raise ValueError("Database names must be non-empty and distinct")
    return env["POSTGRES_USER"], names


def backup(destination):
    # Exclusive creation ensures an existing backup is never overwritten.
    destination.mkdir(mode=0o700, parents=False, exist_ok=False)
    config = subprocess.run(COMPOSE + ["config", "--format", "json"], cwd=ROOT, check=True,
                            capture_output=True, text=True)
    user, names = database_names(json.loads(config.stdout))
    for service, database in names.items():
        path = destination / f"{service}.dump"
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as output:
            subprocess.run(COMPOSE + ["exec", "-T", "db", "pg_dump", "-U", user, "-Fc",
                                      "--no-owner", "--no-privileges", "-d", database],
                           cwd=ROOT, stdout=output, check=True)
        print(f"Saved {service} database")
    manifest = {"format": "postgresql-custom", "databases": names}
    fd = os.open(destination / "manifest.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as output:
        json.dump(manifest, output, ensure_ascii=False, indent=2)
        output.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new directory; its parent must exist")
    args = parser.parse_args()
    try:
        backup(args.destination)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"Backup failed: {exc}. Incomplete directory must not be used as a backup.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
