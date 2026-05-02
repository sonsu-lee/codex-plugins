#!/usr/bin/env python3
"""Deterministic checks for this personal Codex plugin marketplace."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


PLACEHOLDER_RE = re.compile(r"\[TODO\b|TODO:", re.IGNORECASE)
LOCAL_REF_RE = re.compile(r"`(references/[^`]+\.md)`|\((references/[^)]+\.md)\)")
WRITE_KEYWORDS = {
    "edit",
    "write",
    "create",
    "delete",
    "fix",
    "stage",
    "staging",
    "commit",
    "push",
    "publish",
    "resolve",
    "apply patch",
    "apply patches",
}


def normalize_text(value: Any) -> str:
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", value.strip().lower())


class Finding:
    def __init__(self, code: str, severity: str, path: str, message: str) -> None:
        self.code = code
        self.severity = severity
        self.path = path
        self.message = message

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "path": self.path,
            "message": self.message,
        }


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def load_json(path: Path, root: Path, findings: list[Finding]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        findings.append(Finding("PQ001", "P0", rel(path, root), "required JSON file is missing"))
    except json.JSONDecodeError as exc:
        findings.append(
            Finding("PQ002", "P0", rel(path, root), f"invalid JSON: {exc.msg} at line {exc.lineno}")
        )
    return None


def check_placeholder(path: Path, root: Path, findings: list[Finding]) -> None:
    if path.is_file() and PLACEHOLDER_RE.search(path.read_text(encoding="utf-8")):
        findings.append(Finding("PQ003", "P1", rel(path, root), "placeholder TODO text remains"))


def plugin_dirs(root: Path) -> list[Path]:
    plugins_root = root / "plugins"
    if not plugins_root.is_dir():
        return []
    return sorted(path for path in plugins_root.iterdir() if path.is_dir())


def check_required_mapping(
    payload: dict[str, Any],
    keys: list[str],
    path: Path,
    root: Path,
    findings: list[Finding],
) -> None:
    for key in keys:
        current: Any = payload
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                findings.append(Finding("PQ004", "P1", rel(path, root), f"missing required field `{key}`"))
                break
            current = current[part]


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    if not text.startswith("---\n"):
        return None, "missing YAML frontmatter"
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, "unterminated YAML frontmatter"
    raw = text[4:end]
    try:
        payload = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        return None, f"invalid YAML frontmatter: {exc}"
    if not isinstance(payload, dict):
        return None, "frontmatter must be a mapping"
    return payload, None


def check_skill(skill_path: Path, root: Path, findings: list[Finding]) -> tuple[str, dict[str, str]]:
    text = skill_path.read_text(encoding="utf-8")
    skill_record = {"path": rel(skill_path, root)}
    check_placeholder(skill_path, root, findings)
    frontmatter, error = parse_frontmatter(text)
    if error:
        findings.append(Finding("PQ005", "P1", rel(skill_path, root), error))
    else:
        for key in ("name", "description"):
            if not frontmatter.get(key):
                findings.append(
                    Finding("PQ006", "P1", rel(skill_path, root), f"missing frontmatter `{key}`")
                )
        skill_record["name"] = normalize_text(frontmatter.get("name"))
        skill_record["description"] = normalize_text(frontmatter.get("description"))

    skill_dir = skill_path.parent
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.is_file():
        findings.append(Finding("PQ007", "P2", rel(openai_yaml, root), "agents/openai.yaml is missing"))
    else:
        try:
            openai_payload = yaml.safe_load(openai_yaml.read_text(encoding="utf-8"))
            if isinstance(openai_payload, dict):
                interface = openai_payload.get("interface", {})
                if isinstance(interface, dict):
                    skill_record["agents_default_prompt"] = normalize_text(interface.get("default_prompt"))
        except yaml.YAMLError as exc:
            findings.append(
                Finding("PQ008", "P1", rel(openai_yaml, root), f"invalid agents/openai.yaml: {exc}")
            )

    for match in LOCAL_REF_RE.finditer(text):
        ref = match.group(1) or match.group(2)
        ref_path = skill_dir / ref
        if not ref_path.is_file():
            findings.append(
                Finding("PQ009", "P1", rel(skill_path, root), f"referenced file `{ref}` does not exist")
            )

    return text, skill_record


def check_plugin(
    plugin_dir: Path,
    root: Path,
    findings: list[Finding],
) -> tuple[str | None, set[str], str, list[dict[str, str]]]:
    manifest_path = plugin_dir / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path, root, findings)
    all_skill_text = ""
    skill_records: list[dict[str, str]] = []
    capabilities: set[str] = set()
    if isinstance(manifest, dict):
        required = [
            "name",
            "version",
            "description",
            "author.name",
            "homepage",
            "repository",
            "license",
            "keywords",
            "skills",
            "interface.displayName",
            "interface.shortDescription",
            "interface.longDescription",
            "interface.developerName",
            "interface.category",
            "interface.capabilities",
            "interface.defaultPrompt",
            "interface.brandColor",
        ]
        check_required_mapping(manifest, required, manifest_path, root, findings)
        if manifest.get("name") != plugin_dir.name:
            findings.append(
                Finding(
                    "PQ010",
                    "P1",
                    rel(manifest_path, root),
                    f"manifest name `{manifest.get('name')}` does not match folder `{plugin_dir.name}`",
                )
            )
        skills_value = manifest.get("skills")
        if isinstance(skills_value, str):
            skills_dir = plugin_dir / skills_value
            if not skills_dir.is_dir():
                findings.append(
                    Finding("PQ011", "P1", rel(manifest_path, root), f"skills path `{skills_value}` is missing")
                )
        interface = manifest.get("interface", {})
        if isinstance(interface, dict):
            raw_capabilities = interface.get("capabilities", [])
            if isinstance(raw_capabilities, list):
                capabilities = {str(item) for item in raw_capabilities}
    check_placeholder(manifest_path, root, findings)

    for skill_path in sorted((plugin_dir / "skills").glob("*/SKILL.md")):
        skill_text, skill_record = check_skill(skill_path, root, findings)
        all_skill_text += "\n" + skill_text
        skill_records.append(skill_record)

    lowered = all_skill_text.lower()
    has_write_behavior = any(keyword in lowered for keyword in WRITE_KEYWORDS)
    if "Write" in capabilities and not has_write_behavior:
        findings.append(
            Finding(
                "PQ012",
                "P2",
                rel(manifest_path, root),
                "Write capability is declared but no write-owning skill behavior was detected",
            )
        )

    return (
        manifest.get("name") if isinstance(manifest, dict) else None,
        capabilities,
        all_skill_text,
        skill_records,
    )


def check_marketplace(root: Path, plugin_names: set[str], findings: list[Finding]) -> None:
    marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
    marketplace = load_json(marketplace_path, root, findings)
    if not isinstance(marketplace, dict):
        return
    check_placeholder(marketplace_path, root, findings)
    check_required_mapping(marketplace, ["name", "interface.displayName", "plugins"], marketplace_path, root, findings)
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list):
        findings.append(Finding("PQ013", "P0", rel(marketplace_path, root), "`plugins` must be a list"))
        return

    seen: set[str] = set()
    seen_paths: dict[str, str] = {}
    marketplace_names: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            findings.append(Finding("PQ014", "P1", rel(marketplace_path, root), f"plugin entry {index} is not an object"))
            continue
        check_required_mapping(
            entry,
            [
                "name",
                "source.source",
                "source.path",
                "policy.installation",
                "policy.authentication",
                "category",
            ],
            marketplace_path,
            root,
            findings,
        )
        name = entry.get("name")
        if isinstance(name, str):
            marketplace_names.add(name)
            if name in seen:
                findings.append(Finding("PQ015", "P1", rel(marketplace_path, root), f"duplicate marketplace entry `{name}`"))
            seen.add(name)
        source = entry.get("source", {})
        source_path = source.get("path") if isinstance(source, dict) else None
        if isinstance(name, str) and isinstance(source_path, str):
            first_name = seen_paths.get(source_path)
            if first_name and first_name != name:
                findings.append(
                    Finding(
                        "PQ019",
                        "P1",
                        rel(marketplace_path, root),
                        f"duplicate marketplace source path `{source_path}` used by `{first_name}` and `{name}`",
                    )
                )
            seen_paths.setdefault(source_path, name)
        if isinstance(name, str) and source_path != f"./plugins/{name}":
            findings.append(
                Finding(
                    "PQ016",
                    "P1",
                    rel(marketplace_path, root),
                    f"marketplace entry `{name}` path `{source_path}` should be `./plugins/{name}`",
                )
            )
        if isinstance(source_path, str):
            manifest_path = root / source_path.replace("./", "", 1) / ".codex-plugin" / "plugin.json"
            if not manifest_path.is_file():
                findings.append(
                    Finding("PQ017", "P1", rel(marketplace_path, root), f"marketplace path `{source_path}` does not resolve to a plugin manifest")
                )

    for plugin_name in sorted(plugin_names - marketplace_names):
        findings.append(Finding("PQ018", "P2", "plugins", f"plugin `{plugin_name}` is not registered in marketplace"))


def check_duplicate_skill_signals(skill_records: list[dict[str, str]], findings: list[Finding]) -> None:
    for field, label, code in (
        ("name", "skill name", "PQ020"),
        ("description", "skill description", "PQ021"),
        ("agents_default_prompt", "agents default_prompt", "PQ022"),
    ):
        seen: dict[str, str] = {}
        for record in skill_records:
            value = record.get(field, "")
            if not value:
                continue
            path = record.get("path", "<unknown>")
            first_path = seen.get(value)
            if first_path and first_path != path:
                findings.append(
                    Finding(
                        code,
                        "P2",
                        path,
                        f"duplicate {label} also appears in `{first_path}`; verify role boundaries and routing intent",
                    )
                )
            else:
                seen[value] = path


def run_checks(root: str | Path) -> list[Finding]:
    root = Path(root).resolve()
    findings: list[Finding] = []
    plugin_names: set[str] = set()
    skill_records: list[dict[str, str]] = []
    for plugin_dir in plugin_dirs(root):
        name, _capabilities, _skill_text, records = check_plugin(plugin_dir, root, findings)
        if name:
            plugin_names.add(name)
        skill_records.extend(records)
    check_marketplace(root, plugin_names, findings)
    check_duplicate_skill_signals(skill_records, findings)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Repository root to validate")
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON")
    args = parser.parse_args()

    findings = run_checks(args.root)
    if args.json:
        print(json.dumps([finding.as_dict() for finding in findings], indent=2))
    elif findings:
        for finding in findings:
            print(f"[{finding.severity}] {finding.code} {finding.path}: {finding.message}")
    else:
        print("No plugin quality findings.")
    return 1 if any(finding.severity in {"P0", "P1"} for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
