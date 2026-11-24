#!/usr/bin/env python3
"""Add deterministic exact/near duplicate flags to a prospect CSV or XLSX.

The script reads common Chinese/English name and canonical URL columns. It never
deletes rows; exact matches are marked duplicate and near-name matches are marked
possible_duplicate for human review.
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlsplit


NAME_COLUMNS = ("名称", "name", "candidate_name", "community_name", "prospect_name")
URL_COLUMNS = ("官网/主页", "canonical_url", "url", "website", "profile_url")


def normalized_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold()
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", value)


def normalized_url(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if "://" not in raw:
        raw = "https://" + raw
    try:
        parts = urlsplit(raw)
    except ValueError:
        return ""
    host = parts.netloc.casefold().removeprefix("www.")
    path = re.sub(r"/+", "/", parts.path).rstrip("/")
    return f"{host}{path}"


def find_value(row: dict[str, object], candidates: tuple[str, ...]) -> str:
    lowered = {str(k).strip().casefold(): v for k, v in row.items() if k is not None}
    for candidate in candidates:
        value = lowered.get(candidate.casefold())
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def read_rows(path: Path) -> list[dict[str, object]]:
    if path.suffix.casefold() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    if path.suffix.casefold() in {".xlsx", ".xlsm"}:
        try:
            from openpyxl import load_workbook
        except ImportError as exc:
            raise SystemExit("openpyxl is required to read XLSX files") from exc
        workbook = load_workbook(path, read_only=True, data_only=True)
        rows: list[dict[str, object]] = []
        main_sheets = [
            sheet for sheet in workbook.worksheets
            if "BD名单" in sheet.title and "待复核" not in sheet.title
        ]
        for sheet in main_sheets or workbook.worksheets:
            values = list(sheet.iter_rows(values_only=True))
            header_index = next(
                (i for i, row in enumerate(values) if any(str(cell).strip() in NAME_COLUMNS for cell in row if cell is not None)),
                None,
            )
            if header_index is None:
                continue
            headers = [str(cell).strip() if cell is not None else "" for cell in values[header_index]]
            for values_row in values[header_index + 1 :]:
                row = {headers[i]: values_row[i] for i in range(min(len(headers), len(values_row))) if headers[i]}
                if find_value(row, NAME_COLUMNS):
                    rows.append(row)
        return rows
    raise SystemExit(f"Unsupported file type: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--historical", required=True, nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--near-threshold", type=float, default=0.93)
    args = parser.parse_args()

    candidate_rows = read_rows(args.candidates)
    historical_rows = [row for path in args.historical for row in read_rows(path)]
    historical = []
    for row in historical_rows:
        name = find_value(row, NAME_COLUMNS)
        historical.append((name, normalized_name(name), normalized_url(find_value(row, URL_COLUMNS))))

    output_rows = []
    for row in candidate_rows:
        name = find_value(row, NAME_COLUMNS)
        name_key = normalized_name(name)
        url_key = normalized_url(find_value(row, URL_COLUMNS))
        exact = next((item for item in historical if (url_key and item[2] == url_key) or (name_key and item[1] == name_key)), None)
        near = None
        if exact is None and name_key:
            near = max(historical, key=lambda item: SequenceMatcher(None, name_key, item[1]).ratio(), default=None)
            if near and SequenceMatcher(None, name_key, near[1]).ratio() < args.near_threshold:
                near = None
        result = dict(row)
        result["dedupe_key"] = url_key or name_key
        result["duplicate_status"] = "duplicate" if exact else "possible_duplicate" if near else "unique"
        result["duplicate_match"] = exact[0] if exact else near[0] if near else ""
        output_rows.append(result)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(key for row in output_rows for key in row.keys()))
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    main()

