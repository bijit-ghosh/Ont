from pathlib import Path
import tempfile
import unittest
from scripts.presentation import prepare

class PresentationTests(unittest.TestCase):
    def test_fixture_states_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'presentation.sqlite3';r=prepare(p)
            self.assertEqual([x['status'] for x in r['orders']],['queued','awaiting_approval','awaiting_approval','demo_completed'])
            self.assertTrue(all(x['mode']=='demo' for x in r['orders']))
            with self.assertRaises(ValueError):prepare(p)
