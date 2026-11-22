import tempfile
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from ont.integrations.coding import build_change
from ont.integrations.model import BudgetLedger
from ont.integrations.delivery import command

class DeliveryPathTests(unittest.TestCase):
    def fixture(self,root):
        command(['git','init','-b','main'],root)
        (root/'src').mkdir();(root/'src/app.txt').write_text('before\n')
        command(['git','add','.'],root)
        command(['git','-c','user.name=Test','-c','user.email=test@localhost','commit','-m','base'],root)
        return command(['git','rev-parse','HEAD'],root)
    def test_real_git_patch_commit_and_verification_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);commit=self.fixture(root)
            class Model:
                def propose(self,*args):return {'patch':'diff --git a/src/app.txt b/src/app.txt\n--- a/src/app.txt\n+++ b/src/app.txt\n@@ -1 +1 @@\n-before\n+after\n','summary':'Update app','usage':{}}
            def verifier(path,sha,*args):
                self.assertEqual(command(['git','status','--porcelain'],path),'')
                self.assertNotEqual(sha,commit)
                self.assertEqual((root/'src/app.txt').read_text(),'after\n')
                return {'passed':True,'commit':sha}
            with patch('ont.integrations.coding.checkout'),patch('ont.integrations.coding.verify',side_effect=verifier):
                r=build_change('owner/repo',commit,root,['owner/repo'],Model(),'task','context','pinned-image',['test'])
            self.assertEqual(r['commit'],r['verification']['commit'])
    def test_unauthorized_new_file_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);commit=self.fixture(root)
            class Model:
                def propose(self,*args):return {'patch':'diff --git a/secrets.txt b/secrets.txt\nnew file mode 100644\n--- /dev/null\n+++ b/secrets.txt\n@@ -0,0 +1 @@\n+unauthorized\n','summary':'bad','usage':{}}
            with patch('ont.integrations.coding.checkout'),patch('ont.integrations.coding.verify') as verify,self.assertRaises(ValueError):
                build_change('o/r',commit,root,['o/r'],Model(),'task','context','image',['test'])
            verify.assert_not_called()
    def test_only_one_concurrent_budget_settlement_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=BudgetLedger(Path(tmp)/'ledger.db');ledger.reserve('same',5,5)
            def settle(_):
                try:ledger.settle('same',2);return True
                except ValueError:return False
            with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(settle,range(8)))
            self.assertEqual(sum(results),1)
