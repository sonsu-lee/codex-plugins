import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("lint_report.py")


def load_module():
    spec = importlib.util.spec_from_file_location("lint_report", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALID_REPORT = """# Test Report

작성일: 2026-05-02
리서치 모드: workflow-update-review
확신도: 중간

## 핵심 답변

Direct answer with a source https://example.org/source.

## 주요 결론

- Finding.

## 분석

Analysis.

## 리스크와 한계

- Risk.

## 실행 권고

1. Apply the change. 검증: run a sample. 롤백: remove the rule if false positives increase.

## 참고 출처

- Example: https://example.org/source
"""


class LintReportTests(unittest.TestCase):
    def test_valid_report_has_no_errors(self):
        linter = load_module()

        result = linter.lint_report(VALID_REPORT)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])

    def test_missing_required_section_is_an_error(self):
        linter = load_module()
        markdown = VALID_REPORT.replace("## 분석\n\nAnalysis.\n\n", "")

        result = linter.lint_report(markdown)

        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["errors"][0]["code"], "missing_section")
        self.assertEqual(result["errors"][0]["section"], "## 분석")

    def test_internal_artifact_heading_is_an_error(self):
        linter = load_module()
        markdown = VALID_REPORT + "\n## Claim Ledger\n\nInternal notes.\n"

        result = linter.lint_report(markdown)

        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["errors"][0]["code"], "internal_artifact_heading")

    def test_workflow_report_requires_validation_and_rollback_language(self):
        linter = load_module()
        markdown = VALID_REPORT.replace("검증: run a sample. 롤백: remove the rule if false positives increase.", "")

        result = linter.lint_report(markdown)

        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["errors"][0]["code"], "missing_workflow_validation_or_rollback")

    def test_cli_writes_json_and_returns_nonzero_for_errors(self):
        linter = load_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            report = Path(tmpdir) / "report.md"
            output = Path(tmpdir) / "lint.json"
            report.write_text("# Too short\n", encoding="utf-8")

            exit_code = linter.main([str(report), "--json", str(output)])

            self.assertEqual(exit_code, 1)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "fail")


if __name__ == "__main__":
    unittest.main()
