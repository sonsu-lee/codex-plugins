import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


SCRIPT_PATH = Path(__file__).with_name("check_plugin_quality.py")


def load_checker():
    spec = importlib.util.spec_from_file_location("check_plugin_quality", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PluginQualityCheckerTests(unittest.TestCase):
    def setUp(self):
        self.checker = load_checker()

    def write_json(self, path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def write_text(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def create_valid_plugin_repo(self, root):
        plugin_dir = root / "plugins" / "demo-plugin"
        self.write_json(
            plugin_dir / ".codex-plugin" / "plugin.json",
            {
                "name": "demo-plugin",
                "version": "0.1.0",
                "description": "Demo plugin for validation.",
                "author": {"name": "sonsu"},
                "homepage": "https://example.com/demo-plugin",
                "repository": "https://example.com/repo",
                "license": "UNLICENSED",
                "keywords": ["demo"],
                "skills": "./skills/",
                "interface": {
                    "displayName": "Demo Plugin",
                    "shortDescription": "Demo validation plugin.",
                    "longDescription": "A valid demo plugin used by tests.",
                    "developerName": "sonsu",
                    "category": "Productivity",
                    "capabilities": ["Interactive", "Read"],
                    "websiteURL": "https://example.com/demo-plugin",
                    "privacyPolicyURL": "https://openai.com/policies/row-privacy-policy/",
                    "termsOfServiceURL": "https://openai.com/policies/row-terms-of-use/",
                    "defaultPrompt": ["Validate this demo plugin."],
                    "brandColor": "#475569",
                    "screenshots": [],
                },
            },
        )
        self.write_text(
            plugin_dir / "skills" / "demo-skill" / "SKILL.md",
            """---
name: demo-skill
description: "Use when validating the demo plugin."
---

# Demo Skill

Read `references/demo.md` when deeper checks are needed.
""",
        )
        self.write_text(
            plugin_dir / "skills" / "demo-skill" / "agents" / "openai.yaml",
            """interface:
  display_name: "Demo Skill"
  short_description: "Demo validation skill"
  default_prompt: "Validate this demo plugin."
""",
        )
        self.write_text(
            plugin_dir / "skills" / "demo-skill" / "references" / "demo.md",
            "# Demo Reference\n",
        )
        self.write_json(
            root / ".agents" / "plugins" / "marketplace.json",
            {
                "name": "test-marketplace",
                "interface": {"displayName": "Test Marketplace"},
                "plugins": [
                    {
                        "name": "demo-plugin",
                        "source": {
                            "source": "local",
                            "path": "./plugins/demo-plugin",
                        },
                        "policy": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_INSTALL",
                        },
                        "category": "Productivity",
                    }
                ],
            },
        )
        return plugin_dir

    def add_second_plugin_with_duplicate_role(self, root):
        plugin_dir = root / "plugins" / "copy-plugin"
        self.write_json(
            plugin_dir / ".codex-plugin" / "plugin.json",
            {
                "name": "copy-plugin",
                "version": "0.1.0",
                "description": "Copy plugin for validation.",
                "author": {"name": "sonsu"},
                "homepage": "https://example.com/copy-plugin",
                "repository": "https://example.com/repo",
                "license": "UNLICENSED",
                "keywords": ["copy"],
                "skills": "./skills/",
                "interface": {
                    "displayName": "Copy Plugin",
                    "shortDescription": "Copy validation plugin.",
                    "longDescription": "A second plugin used by tests.",
                    "developerName": "sonsu",
                    "category": "Productivity",
                    "capabilities": ["Interactive", "Read"],
                    "websiteURL": "https://example.com/copy-plugin",
                    "privacyPolicyURL": "https://openai.com/policies/row-privacy-policy/",
                    "termsOfServiceURL": "https://openai.com/policies/row-terms-of-use/",
                    "defaultPrompt": ["Validate this copy plugin."],
                    "brandColor": "#475569",
                    "screenshots": [],
                },
            },
        )
        self.write_text(
            plugin_dir / "skills" / "copy-skill" / "SKILL.md",
            """---
name: copy-skill
description: "Use when validating the demo plugin."
---

# Copy Skill
""",
        )
        self.write_text(
            plugin_dir / "skills" / "copy-skill" / "agents" / "openai.yaml",
            """interface:
  display_name: "Copy Skill"
  short_description: "Copy validation skill"
  default_prompt: "Validate this demo plugin."
""",
        )
        marketplace = root / ".agents" / "plugins" / "marketplace.json"
        marketplace_payload = json.loads(marketplace.read_text(encoding="utf-8"))
        marketplace_payload["plugins"].append(
            {
                "name": "copy-plugin",
                "source": {
                    "source": "local",
                    "path": "./plugins/demo-plugin",
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Productivity",
            }
        )
        self.write_json(marketplace, marketplace_payload)
        return plugin_dir

    def test_valid_plugin_repo_has_no_findings(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_valid_plugin_repo(root)

            findings = self.checker.run_checks(root)

            self.assertEqual([], findings)

    def test_detects_placeholders_broken_references_and_marketplace_mismatch(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin_dir = self.create_valid_plugin_repo(root)
            plugin_json = plugin_dir / ".codex-plugin" / "plugin.json"
            payload = json.loads(plugin_json.read_text(encoding="utf-8"))
            payload["description"] = "[TODO: fill this in]"
            payload["interface"]["capabilities"] = ["Interactive", "Write"]
            self.write_json(plugin_json, payload)
            skill_path = plugin_dir / "skills" / "demo-skill" / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8")
                + "\nRead `references/missing.md` for missing details.\n",
                encoding="utf-8",
            )
            marketplace = root / ".agents" / "plugins" / "marketplace.json"
            marketplace_payload = json.loads(marketplace.read_text(encoding="utf-8"))
            marketplace_payload["plugins"][0]["source"]["path"] = "./plugins/wrong"
            self.write_json(marketplace, marketplace_payload)

            findings = self.checker.run_checks(root)
            messages = "\n".join(f.message for f in findings)

            self.assertIn("placeholder", messages.lower())
            self.assertIn("missing.md", messages)
            self.assertIn("marketplace", messages.lower())
            self.assertIn("write capability", messages.lower())

    def test_detects_marketplace_duplicate_paths_and_duplicate_role_text(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_valid_plugin_repo(root)
            self.add_second_plugin_with_duplicate_role(root)

            findings = self.checker.run_checks(root)
            messages = "\n".join(f.message for f in findings)

            self.assertIn("duplicate marketplace source path", messages.lower())
            self.assertIn("duplicate skill description", messages.lower())
            self.assertIn("duplicate agents default_prompt", messages.lower())


if __name__ == "__main__":
    unittest.main()
