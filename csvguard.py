"""Validate common CSV quality rules without third-party dependencies."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


def _value_type(value: str) -> str:
    if value == "":
        return "missing"
    try:
        int(value)
        return "integer"
    except ValueError:
        pass
    try:
        float(value)
        return "number"
    except ValueError:
        return "text"


def inspect_csv(path: str | Path, required: set[str] | None = None) -> dict[str, Any]:
    """Return deterministic quality findings for *path*.

    The function is deliberately small so it can be imported by a pipeline or
    tested without invoking the command-line interface.
    """
    required = required or set()
    rows: list[dict[str, str]] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row")
        headers = reader.fieldnames
        for row in reader:
            rows.append({header: row.get(header, "") or "" for header in headers})

    missing_columns = sorted(required - set(headers))
    missing_values = {
        header: sum(row[header] == "" for row in rows)
        for header in headers
        if any(row[header] == "" for row in rows)
    }

    seen: dict[tuple[str, ...], int] = {}
    duplicate_rows: list[dict[str, int]] = []
    for number, row in enumerate(rows, start=2):
        key = tuple(row[header] for header in headers)
        if key in seen:
            duplicate_rows.append({"first_row": seen[key], "duplicate_row": number})
        else:
            seen[key] = number

    type_mismatches: dict[str, dict[str, int]] = {}
    for header in headers:
        types: dict[str, int] = {}
        for row in rows:
            kind = _value_type(row[header])
            if kind != "missing":
                types[kind] = types.get(kind, 0) + 1
        if len(types) > 1:
            type_mismatches[header] = types

    return {
        "file": str(path),
        "rows": len(rows),
        "columns": headers,
        "missing_required_columns": missing_columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "type_mismatches": type_mismatches,
        "passed": not (missing_columns or missing_values or duplicate_rows or type_mismatches),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="CSV file to inspect")
    parser.add_argument("--required", default="", help="Comma-separated required columns")
    args = parser.parse_args(argv)
    try:
        report = inspect_csv(args.file, {name for name in args.required.split(",") if name})
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
