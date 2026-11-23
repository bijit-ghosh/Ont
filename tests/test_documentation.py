from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
class DocumentationTests(unittest.TestCase):
    def test_local_links_and_images_exist(self):
        files=[ROOT/'README.md',ROOT/'CONTRIBUTING.md',ROOT/'SECURITY.md',*sorted((ROOT/'docs').rglob('*.md'))]
        missing=[]
        for p in files:
            for target in re.findall(r'\]\(([^\s)]+)\)',p.read_text()):
                if '://' in target or target.startswith(('#','mailto:')):continue
                path=target.split('#',1)[0]
                if path and not (p.parent/path).exists():missing.append((str(p.relative_to(ROOT)),target))
        self.assertEqual(missing,[])
    def test_release_badge_and_project_identity(self):
        text=(ROOT/'README.md').read_text()
        self.assertIn('https://github.com/bijit-ghosh/Ont/actions/workflows/ci.yml/badge.svg?branch=main',text)
        self.assertIn('## About',text);self.assertIn('## Mission',text)
        self.assertNotIn('Defensive simulation',text)
        for p in [ROOT/'README.md',*sorted((ROOT/'docs').rglob('*.md'))]:
            self.assertNotIn('github.com/bijit-ghosh/CyberOps',p.read_text())
            self.assertNotIn('github.com/bijit-ghosh/CortexState',p.read_text())
