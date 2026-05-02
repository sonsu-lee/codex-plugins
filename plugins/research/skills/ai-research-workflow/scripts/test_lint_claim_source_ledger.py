import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("lint_claim_source_ledger.py")


def load_module():
    spec = importlib.util.spec_from_file_location("lint_claim_source_ledger", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALID_LEDGER = """# Claim-Source Ledger

## Claim C1

- Claim: Codex skills use progressive disclosure.
- Reference: OpenAI Agent Skills documentation
- Canonical URL: https://developers.openai.com/codex/skills
- Source Tier: S
- Access Path: official_doc
- Grounding: The source describes skill metadata and loading behavior.
- Support Label: supported
- Fit Judgement: The reference directly describes the claimed Codex skill behavior.
- Limitations: Product behavior can change.
"""


class LintClaimSourceLedgerTests(unittest.TestCase):
    def test_valid_ledger_passes(self):
        linter = load_module()

        result = linter.lint_ledger(VALID_LEDGER)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["errors"], [])

    def test_missing_required_field_fails(self):
        linter = load_module()
        ledger = VALID_LEDGER.replace("- Fit Judgement: The reference directly describes the claimed Codex skill behavior.\n", "")

        result = linter.lint_ledger(ledger)

        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["errors"][0]["code"], "missing_field")
        self.assertEqual(result["errors"][0]["field"], "Fit Judgement")

    def test_invalid_support_label_fails(self):
        linter = load_module()
        ledger = VALID_LEDGER.replace("- Support Label: supported", "- Support Label: plausible")

        result = linter.lint_ledger(ledger)

        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["errors"][0]["code"], "invalid_support_label")

    def test_metadata_only_support_requires_grounding(self):
        linter = load_module()
        ledger = VALID_LEDGER.replace("- Support Label: supported", "- Support Label: metadata_only")
        ledger = ledger.replace("- Grounding: The source describes skill metadata and loading behavior.", "- Grounding:")

        result = linter.lint_ledger(ledger)

        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["errors"][0]["code"], "missing_grounding_for_metadata_only")

    def test_cli_writes_json_and_returns_nonzero_for_errors(self):
        linter = load_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Path(tmpdir) / "ledger.md"
            output = Path(tmpdir) / "ledger-lint.json"
            ledger.write_text("# Claim-Source Ledger\n\n## Claim C1\n\n- Claim: Missing fields.\n", encoding="utf-8")

            exit_code = linter.main([str(ledger), "--json", str(output)])

            self.assertEqual(exit_code, 1)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "fail")


if __name__ == "__main__":
    unittest.main()
