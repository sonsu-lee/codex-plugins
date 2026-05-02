#!/usr/bin/env python3
"""Verify source links and scholarly identifiers in Markdown research reports."""

import argparse
import difflib
import ipaddress
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


URL_RE = re.compile(r"https?://[^\s\]\)>,\"']+")
BARE_DOI_RE = re.compile(r"(?<![\w/])(10\.\d{4,9}/[^\s\]\)>,\"']+)", re.IGNORECASE)
ARXIV_RE = re.compile(r"arXiv:\s*([0-9]{4}\.[0-9]{4,5}(?:v\d+)?)", re.IGNORECASE)
TRAILING_PUNCTUATION = ".,;:"


class SourceRef:
    def __init__(
        self,
        kind,
        raw,
        url=None,
        identifier=None,
        expected_title=None,
        expected_year=None,
        expected_authors=None,
    ):
        self.kind = kind
        self.raw = raw
        self.url = url
        self.identifier = identifier
        self.expected_title = expected_title
        self.expected_year = expected_year
        self.expected_authors = expected_authors or []

    def to_dict(self):
        return {
            "kind": self.kind,
            "raw": self.raw,
            "url": self.url,
            "identifier": self.identifier,
            "expected_title": self.expected_title,
            "expected_year": self.expected_year,
            "expected_authors": self.expected_authors,
        }


class UrllibTransport:
    def request(self, url, method="GET", headers=None, timeout=10):
        req = urllib.request.Request(url, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = b""
                if method != "HEAD":
                    body = response.read(1024 * 256)
                return {
                    "status": response.status,
                    "url": response.geturl(),
                    "headers": dict(response.headers.items()),
                    "body": body,
                }
        except urllib.error.HTTPError as exc:
            body = b""
            try:
                body = exc.read(1024 * 64)
            except Exception:
                body = b""
            return {
                "status": exc.code,
                "url": exc.url,
                "headers": dict(exc.headers.items()) if exc.headers else {},
                "body": body,
            }
        except Exception as exc:
            return {
                "status": None,
                "url": url,
                "headers": {},
                "body": b"",
                "error": f"{type(exc).__name__}: {exc}",
            }


def normalize_url(url):
    return url.strip().rstrip(TRAILING_PUNCTUATION)


def normalize_doi(value):
    value = urllib.parse.unquote(value.strip())
    value = value.replace("https://doi.org/", "").replace("http://doi.org/", "")
    value = value.replace("doi:", "")
    return value.rstrip(TRAILING_PUNCTUATION).lower()


def extract_arxiv_id(url_or_text):
    parsed = urllib.parse.urlparse(url_or_text)
    if parsed.netloc.endswith("arxiv.org"):
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2 and parts[0] in {"abs", "pdf"}:
            arxiv_id = parts[1]
            if arxiv_id.endswith(".pdf"):
                arxiv_id = arxiv_id[:-4]
            return arxiv_id.rstrip(TRAILING_PUNCTUATION)
    match = ARXIV_RE.search(url_or_text)
    if match:
        return match.group(1)
    return None


def classify_url(url):
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    if host in {"doi.org", "dx.doi.org"}:
        return SourceRef(kind="doi", raw=url, url=url, identifier=normalize_doi(parsed.path.lstrip("/")))
    arxiv_id = extract_arxiv_id(url)
    if arxiv_id:
        return SourceRef(kind="arxiv", raw=url, url=url, identifier=arxiv_id)
    if host.endswith("openreview.net"):
        query = urllib.parse.parse_qs(parsed.query)
        forum = query.get("id", [None])[0]
        return SourceRef(kind="openreview", raw=url, url=url, identifier=forum)
    if host.endswith("pubmed.ncbi.nlm.nih.gov"):
        parts = [part for part in parsed.path.split("/") if part]
        pmid = parts[0] if parts else None
        return SourceRef(kind="pubmed", raw=url, url=url, identifier=pmid)
    return SourceRef(kind="url", raw=url, url=url)


def extract_sources(markdown):
    sources = []
    seen = set()

    for match in URL_RE.finditer(markdown):
        url = normalize_url(match.group(0))
        if url not in seen:
            seen.add(url)
            sources.append(classify_url(url))

    for match in BARE_DOI_RE.finditer(markdown):
        doi = normalize_doi(match.group(1))
        if doi not in seen:
            seen.add(doi)
            sources.append(SourceRef(kind="doi", raw=match.group(1), identifier=doi))

    for match in ARXIV_RE.finditer(markdown):
        arxiv_id = match.group(1)
        key = f"arxiv:{arxiv_id}"
        if key not in seen:
            seen.add(key)
            sources.append(SourceRef(kind="arxiv", raw=match.group(0), identifier=arxiv_id))

    return sources


def is_unsafe_host(hostname):
    if not hostname:
        return True
    normalized = hostname.strip("[]").lower()
    if normalized in {"localhost", "localhost.localdomain"} or normalized.endswith(".local"):
        return True
    try:
        ip = ipaddress.ip_address(normalized)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast
    except ValueError:
        pass
    return False


def is_safe_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    return not is_unsafe_host(parsed.hostname)


def verify_url(source, transport=None, timeout=10):
    if not source.url or not is_safe_url(source.url):
        return {"source": source.to_dict(), "status": "blocked", "reason": "unsafe_url"}

    transport = transport or UrllibTransport()
    headers = {"User-Agent": "codex-research-source-verifier/0.1"}
    response = transport.request(source.url, method="HEAD", headers=headers, timeout=timeout)
    method = "HEAD"
    if response.get("status") in {403, 405} or response.get("status") is None:
        response = transport.request(source.url, method="GET", headers=headers, timeout=timeout)
        method = "GET"

    status = response.get("status")
    result_status = "ok" if status is not None and 200 <= status < 400 else "failed"
    return {
        "source": source.to_dict(),
        "status": result_status,
        "http_status": status,
        "method": method,
        "final_url": response.get("url"),
        "content_type": _header_value(response.get("headers", {}), "content-type"),
        "error": response.get("error"),
    }


def _header_value(headers, name):
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def crossref_url(doi):
    return "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")


def verify_doi(source, transport=None, timeout=10):
    transport = transport or UrllibTransport()
    doi = source.identifier or normalize_doi(source.raw)
    url = crossref_url(doi)
    response = transport.request(
        url,
        method="GET",
        headers={"Accept": "application/json", "User-Agent": "codex-research-source-verifier/0.1"},
        timeout=timeout,
    )
    if response.get("status") != 200:
        return {
            "source": source.to_dict(),
            "status": "not_found",
            "provider": "crossref",
            "http_status": response.get("status"),
            "error": response.get("error"),
        }

    try:
        payload = json.loads(response.get("body", b"{}").decode("utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "source": source.to_dict(),
            "status": "failed",
            "provider": "crossref",
            "reason": f"invalid_json: {exc}",
        }

    metadata = normalize_crossref_metadata(payload.get("message", {}))
    return {
        "source": source.to_dict(),
        "status": "ok",
        "provider": "crossref",
        "metadata": metadata,
        "match": score_metadata_match(source, metadata),
    }


def normalize_crossref_metadata(message):
    title = first(message.get("title")) or ""
    container = first(message.get("container-title")) or ""
    year = extract_crossref_year(message)
    authors = []
    for author in message.get("author", []) or []:
        name = " ".join(part for part in [author.get("given"), author.get("family")] if part)
        if name:
            authors.append(name)
    return {
        "doi": normalize_doi(message.get("DOI", "")) if message.get("DOI") else None,
        "title": title,
        "authors": authors,
        "year": year,
        "container": container,
        "url": message.get("URL"),
        "type": message.get("type"),
    }


def first(value):
    if isinstance(value, list) and value:
        return value[0]
    if isinstance(value, str):
        return value
    return None


def extract_crossref_year(message):
    for key in ("issued", "published-print", "published-online", "created"):
        date_parts = (message.get(key) or {}).get("date-parts")
        if date_parts and date_parts[0]:
            return date_parts[0][0]
    return None


def normalize_text(value):
    value = (value or "").lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def title_similarity(left, right):
    return difflib.SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def score_metadata_match(source, metadata):
    checks = {}
    expected_title = source.expected_title
    if expected_title:
        checks["title_similarity"] = round(title_similarity(expected_title, metadata.get("title")), 3)
    if source.expected_year:
        checks["year_match"] = source.expected_year == metadata.get("year")
    if source.expected_authors:
        observed = {normalize_text(author) for author in metadata.get("authors", [])}
        expected = {normalize_text(author) for author in source.expected_authors}
        checks["author_overlap"] = sorted(expected & observed)

    if not checks:
        return {"status": "unchecked", "checks": checks}
    title_ok = checks.get("title_similarity", 1.0) >= 0.92
    year_ok = checks.get("year_match", True) is True
    author_ok = bool(checks.get("author_overlap", [True]))
    return {"status": "match" if title_ok and year_ok and author_ok else "mismatch", "checks": checks}


def verify_source(source, transport=None, offline=False):
    if offline:
        return {"source": source.to_dict(), "status": "not_checked", "reason": "offline"}
    if source.kind == "doi":
        return verify_doi(source, transport=transport)
    return verify_url(source, transport=transport)


def build_payload(markdown, transport=None, offline=False):
    sources = extract_sources(markdown)
    results = [verify_source(source, transport=transport, offline=offline) for source in sources]
    counts = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    return {
        "summary": {"total": len(results), "by_status": counts},
        "sources": [result["source"] for result in results],
        "results": results,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify source links and scholarly identifiers in a Markdown report.")
    parser.add_argument("report", help="Markdown report path")
    parser.add_argument("--offline", action="store_true", help="Only extract sources; do not perform network checks")
    parser.add_argument("--json", dest="json_path", help="Write machine-readable JSON report to this path")
    args = parser.parse_args(argv)

    markdown = Path(args.report).read_text(encoding="utf-8")
    payload = build_payload(markdown, offline=args.offline)
    data = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.json_path:
        Path(args.json_path).write_text(data + "\n", encoding="utf-8")
    else:
        print(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
