import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from evals.run import ROOT,validate_catalog,run_case,summarize,main,fingerprint

class EnterpriseEvalTests(unittest.TestCase):
    def catalog(self):return json.loads((ROOT/'evals/catalog.json').read_text())
    def test_every_layer_has_executable_and_enterprise_gates(self):
        c=validate_catalog(self.catalog())
        self.assertEqual(len(c['layers']),7)
        self.assertEqual({r['layer'] for r in c['cases'] if r['kind']=='enterprise_gate'},set(c['layers']))
    def test_duplicate_and_unsafe_selector_rejected(self):
        c=self.catalog();c['cases'].append(c['cases'][0])
        with self.assertRaises(ValueError):validate_catalog(c)
        c=self.catalog();c['cases'][0]['selectors']=['os.system']
        with self.assertRaises(ValueError):validate_catalog(c)
    def test_zero_and_skipped_tests_cannot_pass(self):
        case=self.catalog()['cases'][0]
        for count,skipped in [(0,0),(1,1)]:
            payload={'tests':count,'skipped':skipped,'expected_failures':0}
            response=subprocess.CompletedProcess([],0,'ONT_EVAL_RESULT='+json.dumps(payload),'')
            with tempfile.TemporaryDirectory() as tmp,patch('evals.run.subprocess.run',return_value=response):
                self.assertEqual(run_case(case,'core','image',Path(tmp))['status'],'failed')
    def test_missing_tool_is_blocked_not_passed(self):
        case=next(c for c in self.catalog()['cases'] if c['kind']=='rust')
        with tempfile.TemporaryDirectory() as tmp,patch('evals.run.shutil.which',return_value=None):
            self.assertEqual(run_case(case,'core','image',Path(tmp))['status'],'blocked')
    def test_failed_process_records_failure_and_evidence(self):
        case=self.catalog()['cases'][0]
        with tempfile.TemporaryDirectory() as tmp,patch('evals.run.subprocess.run',return_value=subprocess.CompletedProcess([],1,'','failure')):
            r=run_case(case,'core','image',Path(tmp));self.assertEqual(r['status'],'failed');self.assertEqual(len(r['evidence_sha256']),64)
    def test_strict_enterprise_mode_blocks_incomplete_suite(self):
        def result(case,*args):return {'id':case['id'],'layer':case['layer'],'criterion':case['criterion'],'kind':case['kind'],'status':'blocked' if case['kind']=='enterprise_gate' else 'passed','required_action':'external qualification' if case['kind']=='enterprise_gate' else ''}
        with tempfile.TemporaryDirectory() as tmp,patch('sys.argv',['evals.run','--out',str(Path(tmp)/'report'),'--require-enterprise']),patch('evals.run.run_case',side_effect=result),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(),2)
            r=json.loads((Path(tmp)/'report/report.json').read_text())
            self.assertEqual(r['summary']['automated_gate'],'passed');self.assertEqual(r['summary']['enterprise_gate'],'blocked')
    def test_missing_test_selector_fails_real_probe(self):
        import sys
        p=subprocess.run([sys.executable,'-m','evals.probe','tests.test_app.NoSuchClass'],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)

    def test_fingerprint_covers_ui_and_deployment_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'web').mkdir();(root/'web/index.html').write_text('one')
            a=fingerprint(root);(root/'web/index.html').write_text('two');b=fingerprint(root)
            self.assertNotEqual(a,b)
            (root/'compose.yaml').write_text('services: {}');c=fingerprint(root)
            self.assertNotEqual(b,c)
            (root/'Dockerfile').write_text('FROM scratch');self.assertNotEqual(c,fingerprint(root))
