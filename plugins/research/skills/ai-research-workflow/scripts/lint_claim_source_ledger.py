#!/usr/bin/env python3
"""Lint internal claim-source ledgers for source support review."""

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = [
    "Claim",
    "Reference",
    "Canonical URL",
    "Source Tier",
    "Access Path",
    "Grounding",
    "Support Label",
    "Fit Judgement",
    "Limitations",
]

ALLOWED_SUPPORT_LABELS = {
    "supported",
    "partially_supported",
    "partially-supported",
    "unsupported",
    "contradicted",
    "uncertain",
    "ambiguous",
    "metadata_only",
    "metadata-only",
    "not_checked",
    "not-checked",
}

ALLOWED_ACCESS_PATHS = {
    "full_text",
    "full-text",
    "abstract",
    "metadata",
    "official_doc",
    "official-doc",
    "code",
    "changelog",
    "release_note",
    "release-note",
    "table",
    "figure",
    "api_response",
    "api-response",
    "repository",
    "benchmark",
    "not_checked",
    "not-checked",
}

URL_RE = re.compile(r"^https?://")


def lint_ledger(markdown):
    errors = []
    warnings = []
    entries = parse_entries(markdown)

    if not entries:
        errors.append({"code": "missing_claim_entries"})

    for index, entry in enumerate(entries, start=1):
        errors.extend(lint_entry(index, entry))

    return {
        "status": "fail" if errors else "pass",
        "entry_count": len(entries),
        "errors": errors,
        "warnings": warnings,
    }


def parse_entries(markdown):
    sections = re.split(r"(?m)^##\s+Claim\b.*$", markdown)
    if len(sections) <= 1:
        return []

    entries = []
    for section in sections[1:]:
        fields = {}
        for line in section.splitlines():
            match = re.match(r"^\s*[-*]\s*([^:]+):\s*(.*)$", line)
            if match:
                fields[normalize_field(match.group(1))] = match.group(2).strip()
        entries.append(fields)
    return entries


def normalize_field(field):
    return " ".join(field.strip().split()).lower()


def lint_entry(index, entry):
    errors = []
    for field in REQUIRED_FIELDS:
        if normalize_field(field) not in entry:
            errors.append({"code": "missing_field", "entry": index, "field": field})

    canonical_url = entry.get(normalize_field("Canonical URL"), "")
    if canonical_url and not URL_RE.match(canonical_url):
        errors.append({"code": "invalid_canonical_url", "entry": index, "value": canonical_url})

    support_label = entry.get(normalize_field("Support Label"), "")
    if support_label and normalize_token(support_label) not in {normalize_token(label) for label in ALLOWED_SUPPORT_LABELS}:
        errors.append({"code": "invalid_support_label", "entry": index, "value": support_label})

    access_path = entry.get(normalize_field("Access Path"), "")
    if access_path and normalize_token(access_path) not in {normalize_token(path) for path in ALLOWED_ACCESS_PATHS}:
        errors.append({"code": "invalid_access_path", "entry": index, "value": access_path})

    grounding = entry.get(normalize_field("Grounding"), "")
    if normalize_token(support_label) == "metadata_only" and not grounding:
        errors.append({"code": "missing_grounding_for_metadata_only", "entry": index})

    return errors


def normalize_token(value):
    return (value or "").strip().lower().replace("-", "_")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lint a Markdown claim-source ledger.")
    parser.add_argument("ledger", help="Markdown claim-source ledger path")
    parser.add_argument("--json", dest="json_path", help="Write machine-readable JSON report to this path")
    args = parser.parse_args(argv)

    markdown = Path(args.ledger).read_text(encoding="utf-8")
    result = lint_ledger(markdown)
    data = json.dumps(result, indent=2, ensure_ascii=False)
    if args.json_path:
        Path(args.json_path).write_text(data + "\n", encoding="utf-8")
    else:
        print(data)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
