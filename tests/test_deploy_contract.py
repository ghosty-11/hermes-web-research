from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DeployContractTest(unittest.TestCase):
    def test_manifest_packages_web_research_plugin_tree(self) -> None:
        manifest = json.loads((ROOT / "deploy" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("hermes-web-research", manifest["module"])
        self.assertEqual(
            [{"source": "plugin", "destination": "plugins/hermes-web-research", "kind": "tree"}],
            manifest["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
