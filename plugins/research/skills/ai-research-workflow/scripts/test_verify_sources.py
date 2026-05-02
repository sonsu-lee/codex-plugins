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

    def test_doi_verification_falls_back_to_datacite(self):
        verifier = load_module()
        source = verifier.SourceRef(
            kind="doi",
            raw="10.9999/dataset",
            identifier="10.9999/dataset",
            expected_title="Useful Dataset",
            expected_year=2025,
            expected_authors=["Ada Lovelace"],
        )
        crossref_url = "https://api.crossref.org/works/10.9999%2Fdataset"
        datacite_url = "https://api.datacite.org/dois/10.9999%2Fdataset"
        transport = FakeTransport(
            {
                ("GET", crossref_url): {
                    "status": 404,
                    "url": crossref_url,
                    "headers": {},
                    "body": b"",
                },
                ("GET", datacite_url): {
                    "status": 200,
                    "url": datacite_url,
                    "headers": {"content-type": "application/json"},
                    "body": json.dumps(
                        {
                            "data": {
                                "attributes": {
                                    "doi": "10.9999/dataset",
                                    "titles": [{"title": "Useful Dataset"}],
                                    "creators": [{"name": "Ada Lovelace"}],
                                    "publicationYear": 2025,
                                    "publisher": "Verification Archive",
                                    "url": "https://example.org/datasets/useful",
                                    "types": {"resourceTypeGeneral": "Dataset"},
                                }
                            }
                        }
                    ).encode("utf-8"),
                },
            }
        )

        result = verifier.verify_doi(source, transport)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "datacite")
        self.assertEqual(result["metadata"]["title"], "Useful Dataset")
        self.assertEqual(result["match"]["status"], "match")

    def test_metadata_mismatch_is_reported_as_top_level_status(self):
        verifier = load_module()
        source = verifier.SourceRef(
            kind="doi",
            raw="10.1234/mismatch",
            identifier="10.1234/mismatch",
            expected_title="Expected title",
        )
        crossref_url = "https://api.crossref.org/works/10.1234%2Fmismatch"
        transport = FakeTransport(
            {
                ("GET", crossref_url): {
                    "status": 200,
                    "url": crossref_url,
                    "headers": {"content-type": "application/json"},
                    "body": json.dumps({"message": {"DOI": "10.1234/mismatch", "title": ["Different title"]}}).encode(
                        "utf-8"
                    ),
                }
            }
        )

        result = verifier.verify_doi(source, transport)

        self.assertEqual(result["status"], "metadata_mismatch")
        self.assertEqual(result["match"]["status"], "mismatch")

    def test_arxiv_verification_fetches_metadata(self):
        verifier = load_module()
        source = verifier.SourceRef(
            kind="arxiv",
            raw="https://arxiv.org/abs/2402.14207",
            url="https://arxiv.org/abs/2402.14207",
            identifier="2402.14207",
            expected_title="Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models",
            expected_year=2024,
            expected_authors=["Yijia Shao"],
        )
        api_url = "https://export.arxiv.org/api/query?id_list=2402.14207"
        transport = FakeTransport(
            {
                ("GET", api_url): {
                    "status": 200,
                    "url": api_url,
                    "headers": {"content-type": "application/atom+xml"},
                    "body": b"""<?xml version='1.0' encoding='UTF-8'?>
                    <feed xmlns='http://www.w3.org/2005/Atom'>
                      <entry>
                        <id>http://arxiv.org/abs/2402.14207v2</id>
                        <published>2024-02-22T01:20:17Z</published>
                        <updated>2024-04-08T05:38:50Z</updated>
                        <title>Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models</title>
                        <author><name>Yijia Shao</name></author>
                        <author><name>Yucheng Jiang</name></author>
                        <arxiv:doi xmlns:arxiv='http://arxiv.org/schemas/atom'>10.48550/arXiv.2402.14207</arxiv:doi>
                      </entry>
                    </feed>""",
                }
            }
        )

        result = verifier.verify_arxiv(source, transport)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "arxiv")
        self.assertEqual(result["metadata"]["year"], 2024)
        self.assertEqual(result["match"]["status"], "match")

    def test_pubmed_verification_fetches_metadata(self):
        verifier = load_module()
        source = verifier.SourceRef(
            kind="pubmed",
            raw="https://pubmed.ncbi.nlm.nih.gov/12345678/",
            url="https://pubmed.ncbi.nlm.nih.gov/12345678/",
            identifier="12345678",
            expected_title="A useful biomedical paper",
            expected_year=2024,
            expected_authors=["Ada Lovelace"],
        )
        api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=12345678&retmode=json"
        transport = FakeTransport(
            {
                ("GET", api_url): {
                    "status": 200,
                    "url": api_url,
                    "headers": {"content-type": "application/json"},
                    "body": json.dumps(
                        {
                            "result": {
                                "uids": ["12345678"],
                                "12345678": {
                                    "title": "A useful biomedical paper",
                                    "pubdate": "2024 Jan",
                                    "source": "Journal of Verification",
                                    "authors": [{"name": "Ada Lovelace"}],
                                    "articleids": [{"idtype": "doi", "value": "10.1234/biomed"}],
                                },
                            }
                        }
                    ).encode("utf-8"),
                }
            }
        )

        result = verifier.verify_pubmed(source, transport)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "pubmed")
        self.assertEqual(result["metadata"]["doi"], "10.1234/biomed")
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
