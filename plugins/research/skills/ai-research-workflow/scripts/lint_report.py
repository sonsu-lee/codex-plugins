#!/usr/bin/env python3
"""Lint Markdown research reports for required reader-facing quality gates."""

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "## 핵심 답변",
    "## 주요 결론",
    "## 분석",
    "## 리스크와 한계",
    "## 실행 권고",
    "## 참고 출처",
]

INTERNAL_ARTIFACT_HEADINGS = [
    "Claim Ledger",
    "Evidence Matrix",
    "Quality Gate Results",
    "Workflow Implications",
    "Rollback Table",
]

URL_RE = re.compile(r"https?://[^\s\]\)>,\"']+")


def lint_report(markdown):
    errors = []
    warnings = []

    for section in REQUIRED_SECTIONS:
        if section not in markdown:
            errors.append({"code": "missing_section", "section": section})

    for heading in INTERNAL_ARTIFACT_HEADINGS:
        if re.search(rf"^#+\s+{re.escape(heading)}\s*$", markdown, flags=re.MULTILINE | re.IGNORECASE):
            errors.append({"code": "internal_artifact_heading", "heading": heading})

    if "## 참고 출처" in markdown:
        sources_block = markdown.split("## 참고 출처", 1)[1]
        if not URL_RE.search(sources_block):
            errors.append({"code": "missing_source_url", "section": "## 참고 출처"})

    mode = extract_mode(markdown)
    if "workflow-update-review" in mode and not has_validation_and_rollback(markdown):
        errors.append({"code": "missing_workflow_validation_or_rollback"})

    return {
        "status": "fail" if errors else "pass",
        "mode": mode,
        "errors": errors,
        "warnings": warnings,
    }


def extract_mode(markdown):
    match = re.search(r"^리서치 모드:\s*(.+)$", markdown, flags=re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip()


def has_validation_and_rollback(markdown):
    validation_words = ("검증", "validation", "validate")
    rollback_words = ("롤백", "rollback", "중단 조건", "되돌")
    lower = markdown.lower()
    has_validation = any(word.lower() in lower for word in validation_words)
    has_rollback = any(word.lower() in lower for word in rollback_words)
    return has_validation and has_rollback


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lint a Markdown research report.")
    parser.add_argument("report", help="Markdown report path")
    parser.add_argument("--json", dest="json_path", help="Write machine-readable JSON report to this path")
    args = parser.parse_args(argv)

    markdown = Path(args.report).read_text(encoding="utf-8")
    result = lint_report(markdown)
    data = json.dumps(result, indent=2, ensure_ascii=False)
    if args.json_path:
        Path(args.json_path).write_text(data + "\n", encoding="utf-8")
    else:
        print(data)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
