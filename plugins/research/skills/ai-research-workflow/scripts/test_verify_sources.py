import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("verify_sources.py")


def load_module():
    spec = importlib.util.spec_from_file_location("verify_sources", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeTransport:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def request(self, url, method="GET", headers=None, timeout=10):
        self.calls.append((method, url))
        key = (method, url)
        if key not in self.responses:
            return {"status": 404, "url": url, "headers": {}, "body": b""}
        return self.responses[key]


class VerifySourcesTests(unittest.TestCase):
    def test_extracts_urls_and_identifiers_from_markdown(self):
        verifier = load_module()
        markdown = """
        See [RAG](https://doi.org/10.48550/arXiv.2005.11401) and
        https://arxiv.org/abs/2210.03629 plus https://example.org/page.
        """

        sources = verifier.extract_sources(markdown)

        self.assertEqual([s.kind for s in sources], ["doi", "arxiv", "url"])
        self.assertEqual(sources[0].identifier, "10.48550/arxiv.2005.11401")
        self.assertEqual(sources[1].identifier, "2210.03629")
        self.assertEqual(sources[2].url, "https://example.org/page")

    def test_blocks_unsafe_urls_before_network_access(self):
        verifier = load_module()
        source = verifier.SourceRef(kind="url", raw="http://127.0.0.1/admin", url="http://127.0.0.1/admin")
        transport = FakeTransport({})

        result = verifier.verify_url(source, transport)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "unsafe_url")
        self.assertEqual(transport.calls, [])

    def test_head_falls_back_to_get_when_method_not_allowed(self):
        verifier = load_module()
        source = verifier.SourceRef(kind="url", raw="https://example.org/page", url="https://example.org/page")
        transport = FakeTransport(
            {
                ("HEAD", "https://example.org/page"): {
                    "status": 405,
                    "url": "https://example.org/page",
                    "headers": {},
                    "body": b"",
                },
                ("GET", "https://example.org/page"): {
                    "status": 200,
                    "url": "https://example.org/page",
                    "headers": {"content-type": "text/html"},
                    "body": b"<html></html>",
                },
            }
        )

        result = verifier.verify_url(source, transport)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["http_status"], 200)
        self.assertEqual(result["method"], "GET")

    def test_doi_verification_normalizes_crossref_metadata_and_scores_match(self):
        verifier = load_module()
        source = verifier.SourceRef(
            kind="doi",
            raw="https://doi.org/10.1234/Test.DOI",
            url="https://doi.org/10.1234/Test.DOI",
            identifier="10.1234/test.doi",
            expected_title="A useful research paper",
            expected_year=2024,
        )
        crossref_url = "https://api.crossref.org/works/10.1234%2Ftest.doi"
        transport = FakeTransport(
            {
                ("GET", crossref_url): {
                    "status": 200,
                    "url": crossref_url,
                    "headers": {"content-type": "application/json"},
                    "body": json.dumps(
                        {
                            "message": {
                                "DOI": "10.1234/test.doi",
                                "title": ["A Useful Research Paper"],
                                "author": [{"given": "Ada", "family": "Lovelace"}],
                                "issued": {"date-parts": [[2024, 1, 5]]},
                                "container-title": ["Journal of Verification"],
                                "URL": "https://doi.org/10.1234/test.doi",
                            }
                        }
                    ).encode("utf-8"),
                }
            }
        )

        result = verifier.verify_doi(source, transport)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "crossref")
        self.assertEqual(result["metadata"]["title"], "A Useful Research Paper")
        self.assertEqual(result["metadata"]["year"], 2024)
        self.assertEqual(result["match"]["status"], "match")

    def test_cli_outputs_json_for_offline_extraction(self):
        verifier = load_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            report = Path(tmpdir) / "report.md"
            output = Path(tmpdir) / "out.json"
            report.write_text("Source: https://arxiv.org/abs/2004.14974\n", encoding="utf-8")

            exit_code = verifier.main([str(report), "--offline", "--json", str(output)])

            self.assertEqual(exit_code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["total"], 1)
            self.assertEqual(payload["sources"][0]["kind"], "arxiv")


if __name__ == "__main__":
    unittest.main()
