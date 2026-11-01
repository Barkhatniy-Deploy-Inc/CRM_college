#!/usr/bin/env python3
"""Import the recovered techcard and its reference SQLite database to PostgreSQL."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REFERENCE_TABLES = (
    "name_teacher",
    "lesson_type",
    "group_name",
    "lesson",
    "learning_outcomes",
    "lesson_topic",
    "pk_and_ok",
    "skills_and_Knowledge",
)
TECHCARD_TABLES = ("tech_cards", "tech_card_stages")
EXPECTED_COLUMNS = {
    "name_teacher": ("primary_key", "full_name"),
    "lesson_type": ("primary_key", "lesson_type"),
    "group_name": ("primary_key", "curator_group", "group_name"),
    "lesson": ("primary_key", "name_lesson", "Teacher", "Group_name", "type_lesson"),
    "learning_outcomes": ("primary_key", "lesson", "skill", "know"),
    "lesson_topic": ("primary_key", "lesson", "topic"),
    "pk_and_ok": ("primary_key", "lesson", "prof_comp", "general_comp"),
    "skills_and_Knowledge": ("primary_key", "lesson", "skill", "knowledge"),
    "tech_cards": (
        "id",
        "group_id",
        "lesson_id",
        "teacher_id",
        "lesson_type_id",
        "tema",
        "nomer_zanyatiya",
        "ped_tech",
        "cel_zanyatiya",
        "zadachi_obuch",
        "zadachi_razv",
        "zadachi_vosp",
        "prognoz_result",
        "oborudovanie",
        "istochniki",
    ),
    "tech_card_stages": (
        "id",
        "tech_card_id",
        "nomer_etapa",
        "nazvanie_etapa",
        "cel_etapa",
        "dlitelnost",
        "deyatelnost_prepod",
        "deyatelnost_obuch",
        "formiruemye_kompetencii",
    ),
}
EXPECTED_SOURCE_BLOBS = {
    "databaseforbros.db": ("6c852a7b66ece0f7171fa3e59d6a1712e241632c", 53248),
    "techcards.db": ("e3cce67884ec995294c3ac3039c0527226954401", 20480),
}


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def sql_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Source database contains a non-finite numeric value.")
        return repr(value)
    if isinstance(value, str):
        if "\x00" in value:
            raise ValueError("PostgreSQL text cannot store a NUL character.")
        return "convert_from(decode('" + value.encode("utf-8").hex() + "', 'hex'), 'UTF8')"
    if isinstance(value, bytes):
        return "decode('" + value.hex() + "', 'hex')"
    raise ValueError(f"Unsupported SQLite value type: {type(value).__name__}")


def open_sqlite_readonly(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def validate_source_file(path: Path, expected_sha: str, expected_size: int) -> None:
    data = path.read_bytes()
    git_blob_sha = hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()
    if len(data) != expected_size or git_blob_sha != expected_sha:
        raise ValueError(
            f"{path.name} does not match the reviewed Git source "
            f"(size={len(data)}, blob={git_blob_sha})."
        )


def read_table(
    connection: sqlite3.Connection, table: str, expected_columns: tuple[str, ...]
) -> list[tuple[Any, ...]]:
    identifier = quote_identifier(table)
    columns = tuple(row["name"] for row in connection.execute(f"PRAGMA table_info({identifier})"))
    if columns != expected_columns:
        raise ValueError(
            f"Unexpected columns in {table}: {columns!r}; expected {expected_columns!r}."
        )
    foreign_key_issues = connection.execute(f"PRAGMA foreign_key_check({identifier})").fetchall()
    if foreign_key_issues:
        raise ValueError(
            f"SQLite foreign-key check failed for {table}: {len(foreign_key_issues)} violation(s)."
        )
    order_column = "primary_key" if "primary_key" in columns else "id"
    query = f"SELECT * FROM {identifier} ORDER BY {quote_identifier(order_column)}"
    return [tuple(row) for row in connection.execute(query)]


def postgres_rows(
    docker: str, root: Path, table: str, columns: tuple[str, ...]
) -> list[tuple[Any, ...]]:
    identifier = quote_identifier(table)
    selected = ", ".join(quote_identifier(column) for column in columns)
    query = (
        f"SELECT row_to_json(source_row)::text "
        f"FROM (SELECT {selected} FROM {identifier} "
        f"ORDER BY {quote_identifier(columns[0])}) AS source_row"
    )
    result = subprocess.run(
        [
            docker,
            "compose",
            "exec",
            "-T",
            "db",
            "psql",
            "-X",
            "-A",
            "-t",
            "-q",
            "-v",
            "ON_ERROR_STOP=1",
            "-U",
            "postgres",
            "-d",
            "techcard_db",
            "-c",
            query,
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"psql exited {result.returncode}")
    rows = []
    for line in result.stdout.splitlines():
        if line.strip():
            decoded = json.loads(line)
            rows.append(tuple(decoded[column] for column in columns))
    return rows


def load_source(path: Path, tables: tuple[str, ...]) -> dict[str, list[tuple[Any, ...]]]:
    with open_sqlite_readonly(path) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"{path.name} integrity check failed: {integrity}")
        return {table: read_table(connection, table, EXPECTED_COLUMNS[table]) for table in tables}


def validate_source_relations(
    reference_rows: dict[str, list[tuple[Any, ...]]],
    techcard_rows: dict[str, list[tuple[Any, ...]]],
) -> None:
    teacher_ids = {str(row[0]) for row in reference_rows["name_teacher"]}
    group_ids = {str(row[0]) for row in reference_rows["group_name"]}
    lesson_ids = {str(row[0]) for row in reference_rows["lesson"]}
    lesson_type_ids = {str(row[0]) for row in reference_rows["lesson_type"]}

    for row in reference_rows["group_name"]:
        if row[1] is not None and str(row[1]) not in teacher_ids:
            raise ValueError("A source group references a missing curator.")
    for row in reference_rows["lesson"]:
        for value, known_ids, label in (
            (row[2], teacher_ids, "teacher"),
            (row[3], group_ids, "group"),
            (row[4], lesson_type_ids, "lesson type"),
        ):
            if value is not None and str(value) not in known_ids:
                raise ValueError(f"A source lesson references a missing {label}.")
    for table in ("learning_outcomes", "skills_and_Knowledge"):
        for row in reference_rows[table]:
            if row[1] is not None and str(row[1]) not in lesson_ids:
                raise ValueError(f"A source {table} row references a missing lesson.")

    for row in techcard_rows["tech_cards"]:
        for value, known_ids, label in (
            (row[1], group_ids, "group"),
            (row[2], lesson_ids, "lesson"),
            (row[3], teacher_ids, "teacher"),
            (row[4], lesson_type_ids, "lesson type"),
        ):
            if value is not None and str(value) not in known_ids:
                raise ValueError(f"A source techcard references a missing {label}.")
    card_ids = {row[0] for row in techcard_rows["tech_cards"]}
    if any(row[1] not in card_ids for row in techcard_rows["tech_card_stages"]):
        raise ValueError("A source techcard stage references a missing card.")


def build_import_sql(
    reference_rows: dict[str, list[tuple[Any, ...]]],
    techcard_rows: dict[str, list[tuple[Any, ...]]],
    replace: bool,
) -> str:
    statements = ["BEGIN;"]
    all_tables = (*REFERENCE_TABLES, *TECHCARD_TABLES)
    if replace:
        for table in ("tech_card_stages", "tech_cards", *reversed(REFERENCE_TABLES)):
            statements.append(f"DELETE FROM {quote_identifier(table)};")
    else:
        for table in all_tables:
            statements.append(
                "DO $$ BEGIN "
                f"IF EXISTS (SELECT 1 FROM {quote_identifier(table)} LIMIT 1) THEN "
                f"RAISE EXCEPTION 'Target table {table} is not empty'; "
                "END IF; END $$;"
            )

    for table in REFERENCE_TABLES:
        columns = EXPECTED_COLUMNS[table]
        quoted_columns = ", ".join(quote_identifier(column) for column in columns)
        for row in reference_rows[table]:
            values = ", ".join(sql_value(value) for value in row)
            statements.append(
                f"INSERT INTO {quote_identifier(table)} ({quoted_columns}) VALUES ({values});"
            )
    card_columns = EXPECTED_COLUMNS["tech_cards"]
    for row in techcard_rows["tech_cards"]:
        values = ", ".join(sql_value(value) for value in row) + ", NULL"
        columns = ", ".join(quote_identifier(column) for column in (*card_columns, "owner_id"))
        statements.append(
            f"INSERT INTO {quote_identifier('tech_cards')} ({columns}) VALUES ({values});"
        )
    stage_columns = EXPECTED_COLUMNS["tech_card_stages"]
    for row in techcard_rows["tech_card_stages"]:
        values = ", ".join(sql_value(value) for value in row)
        columns = ", ".join(quote_identifier(column) for column in stage_columns)
        statements.append(
            f"INSERT INTO {quote_identifier('tech_card_stages')} ({columns}) VALUES ({values});"
        )

    for table in REFERENCE_TABLES:
        rows = reference_rows[table]
        for row in rows:
            predicates = " AND ".join(
                f"{quote_identifier(column)} IS NOT DISTINCT FROM {sql_value(value)}"
                for column, value in zip(EXPECTED_COLUMNS[table], row)
            )
            statements.append(
                "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM "
                f"{quote_identifier(table)} WHERE {predicates}) THEN "
                f"RAISE EXCEPTION 'Source row mismatch in {table}'; "
                "END IF; END $$;"
            )
        statements.append(
            "DO $$ BEGIN IF (SELECT COUNT(*) FROM "
            f"{quote_identifier(table)}) <> {len(rows)} THEN "
            f"RAISE EXCEPTION 'Source row count mismatch in {table}'; "
            "END IF; END $$;"
        )

    for table in TECHCARD_TABLES:
        rows = techcard_rows[table]
        columns = EXPECTED_COLUMNS[table]
        for row in rows:
            predicates = " AND ".join(
                f"{quote_identifier(column)} IS NOT DISTINCT FROM {sql_value(value)}"
                for column, value in zip(columns, row)
            )
            if table == "tech_cards":
                predicates += ' AND "owner_id" IS NULL'
            statements.append(
                "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM "
                f"{quote_identifier(table)} WHERE {predicates}) THEN "
                f"RAISE EXCEPTION 'Source row mismatch in {table}'; "
                "END IF; END $$;"
            )
        statements.append(
            "DO $$ BEGIN IF (SELECT COUNT(*) FROM "
            f"{quote_identifier(table)}) <> {len(rows)} THEN "
            f"RAISE EXCEPTION 'Source row count mismatch in {table}'; "
            "END IF; END $$;"
        )

    for table in (*REFERENCE_TABLES, *TECHCARD_TABLES):
        key = "primary_key" if table in REFERENCE_TABLES else "id"
        sql_table = quote_identifier(table).replace("'", "''")
        sql_key = key.replace("'", "''")
        statements.append(
            "SELECT setval(pg_get_serial_sequence("
            f"'{sql_table}', '{sql_key}'), "
            f"COALESCE((SELECT MAX({quote_identifier(key)}) "
            f"FROM {quote_identifier(table)}), 1), "
            f"EXISTS (SELECT 1 FROM {quote_identifier(table)}));"
        )
    statements.append("COMMIT;")
    return "\n".join(statements) + "\n"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=root / "backups" / "recovered-palych-2025-11-18",
        help="Directory containing the reviewed SQLite source files.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing rows in the source-reference and techcard tables.",
    )
    args = parser.parse_args()

    source_dir = args.source_dir.resolve()
    for filename, (expected_sha, expected_size) in EXPECTED_SOURCE_BLOBS.items():
        validate_source_file(source_dir / filename, expected_sha, expected_size)

    reference_rows = load_source(source_dir / "databaseforbros.db", REFERENCE_TABLES)
    techcard_rows = load_source(source_dir / "techcards.db", TECHCARD_TABLES)
    validate_source_relations(reference_rows, techcard_rows)

    docker = os.environ.get("DOCKER_CLI") or shutil.which("docker")
    if not docker and os.name == "nt":
        default_cli = Path(r"C:\Program Files\Docker\Docker\resources\bin\docker.exe")
        if default_cli.is_file():
            docker = str(default_cli)
    if not docker:
        raise RuntimeError("Docker CLI not found; set DOCKER_CLI or add docker to PATH.")

    root_docker = subprocess.run(
        [docker, "compose", "exec", "-T", "db", "pg_isready", "-U", "postgres"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if root_docker.returncode:
        raise RuntimeError(
            root_docker.stderr.strip()
            or root_docker.stdout.strip()
            or "Local PostgreSQL is not ready."
        )

    import_sql = build_import_sql(reference_rows, techcard_rows, args.replace)
    result = subprocess.run(
        [
            docker,
            "compose",
            "exec",
            "-T",
            "db",
            "psql",
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            "-U",
            "postgres",
            "-d",
            "techcard_db",
        ],
        cwd=root,
        input=import_sql,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            result.stderr.strip() or f"PostgreSQL import failed with exit code {result.returncode}."
        )

    for table in (*REFERENCE_TABLES, *TECHCARD_TABLES):
        expected = reference_rows[table] if table in reference_rows else techcard_rows[table]
        actual = postgres_rows(docker, root, table, EXPECTED_COLUMNS[table])
        if actual != expected:
            raise RuntimeError(
                f"Post-import verification failed for {table}: "
                f"source rows={len(expected)}, target rows={len(actual)}, "
                "or data differs."
            )
        print(f"Verified {table}: {len(actual)} rows.")

    manifest_path = source_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "imported_at_utc": datetime.now(timezone.utc).isoformat(),
            "target_database": "techcard_db",
            "schema_revision": "71ac4e8d2f60",
            "reference_table_rows": {
                table: len(reference_rows[table]) for table in REFERENCE_TABLES
            },
            "techcard_table_rows": {table: len(techcard_rows[table]) for table in TECHCARD_TABLES},
            "owner_id": None,
            "data_verified_exactly": True,
            "records_disclosed": False,
        }
    )
    temporary_manifest = manifest_path.with_suffix(".json.tmp")
    temporary_manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_manifest, manifest_path)

    print("All source rows verified. The imported card owner_id is NULL.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, sqlite3.Error, ValueError, RuntimeError) as error:
        print(f"Import failed: {error}", file=sys.stderr)
        raise SystemExit(1)
