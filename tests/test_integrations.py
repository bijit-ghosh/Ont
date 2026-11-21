import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from ont.gateway import application
from ont.integrations.model import ModelClient,BudgetLedger
from ont.integrations.memory import SemanticMemory
from ont.integrations.identity import PKCE,Principals
from ont.integrations.delivery import GitHubDelivery,checkout
from ont.integrations.runtime import fan_out,KubernetesRelease
from ont.integrations.mcp import handle

class IntegrationTests(unittest.TestCase):
    def test_model_contract_and_endpoint(self):
        calls=[]
        def transport(p):
            calls.append(p);return {'choices':[{'message':{'content':json.dumps({'patch':'diff','summary':'change'})}}],'usage':{'total_tokens':10}}
        model=ModelClient('https://provider.example/chat','secret','model',['provider.example'],transport)
        self.assertEqual(model.propose('brief','context')['patch'],'diff');self.assertEqual(calls[0]['max_tokens'],2000)
        with self.assertRaises(ValueError):ModelClient('http://evil/chat','x','m',['evil'])
    def test_budget_reservations_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            b=BudgetLedger(Path(tmp)/'b.db');b.reserve('one',5,10);b.reserve('two',5,10)
            with self.assertRaises(ValueError):b.reserve('three',1,10)
            b.settle('one',2);b.reserve('three',1,10)
            with self.assertRaises(ValueError):b.settle('one',2)
    def test_memory_scope_and_vectors(self):
        with tempfile.TemporaryDirectory() as tmp:
            m=SemanticMemory(Path(tmp)/'m.db');m.put('a','1','alpha',[1,0]);m.put('b','2','secret',[1,0]);m.put('a','3','beta',[0,1])
            rows=m.search('a',[1,0]);self.assertEqual(rows[0]['id'],'1');self.assertNotIn('secret',str(rows))
            with self.assertRaises(ValueError):m.put('a','x','bad',[0,0])
    def test_pkce_replay(self):
        from urllib.parse import urlparse,parse_qs
        p=PKCE();url=p.begin('https://id.example/auth','client','https://ont.example/callback','openid')
        state=parse_qs(urlparse(url).query)['state'][0];self.assertTrue(p.consume(state))
        with self.assertRaises(PermissionError):p.consume(state)
    def test_tenant_isolation_and_roles(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'ONT_ENV':'development','ONT_ADMIN_TOKEN':'a'*40,'ONT_WORKER_TOKEN':'w'*40,'ONT_ALLOWED_HOSTS':'','ONT_TENANT_DATA':tmp,'ONT_PRINCIPALS':json.dumps({'1'*40:{'tenant':'one','role':'admin'},'2'*40:{'tenant':'two','role':'admin'},'3'*40:{'tenant':'one','role':'reader'}})}):
            c=TestClient(application());h=lambda k:{'Authorization':'Bearer '+k*40}
            r=c.post('/api/runs',headers=h('1'),json={'title':'Private run','brief':'Tenant one private work order','mode':'demo'})
            self.assertEqual(r.status_code,201);rid=r.json()['id']
            self.assertEqual(c.get('/api/runs/'+rid,headers=h('2')).status_code,404)
            self.assertEqual(c.get('/api/runs/'+rid,headers=h('3')).status_code,200)
            self.assertEqual(c.post('/api/runs',headers=h('3'),json={}).status_code,403)
            self.assertEqual(c.post('/api/worker/claim',headers=h('1'),json={'worker':'x'}).status_code,403)
            c.close()
    def test_draft_pr_reconciliation(self):
        calls=[]
        def run(args):
            calls.append(args);return '[{"url":"https://github.com/o/r/pull/1"}]'
        d=GitHubDelivery('o/r',['o/r'],run);self.assertFalse(d.draft_pr('ont/task','main','title','body.md')['created']);self.assertEqual(len(calls),1)
    def test_checkout_requires_exact_allowed_commit(self):
        with self.assertRaises(ValueError):checkout('evil/repo','main','/tmp/unused',[])
    def test_rollout_failure_rolls_back(self):
        calls=[]
        def run(args,**kwargs):
            calls.append(args)
            if 'status' in args and len([a for a in calls if 'status' in a])==1:raise RuntimeError('not ready')
            return ''
        r=KubernetesRelease('ctx','ns','app','app',[('ctx','ns','app','app')],run)
        with self.assertRaises(RuntimeError):r.rollout('registry/app@sha256:'+'a'*64)
        self.assertTrue(any('undo' in a for a in calls))
    def test_fanout_and_mcp(self):
        self.assertEqual(fan_out([1,2,3],lambda x:x*x,2),[1,4,9])
        self.assertIn('tools',handle({'id':1,'method':'tools/list'})['result'])
        self.assertIsNone(handle({'method':'notifications/initialized'}))

class VerificationTests(unittest.TestCase):
    def test_verifier_requires_clean_commit_and_digest(self):
        from ont.integrations.delivery import verify
        with tempfile.TemporaryDirectory() as tmp,patch('ont.integrations.delivery.command',side_effect=['a'*40,'']):
            with self.assertRaises(ValueError):verify(tmp,'a'*40,'python:latest',['pytest'])
    def test_verifier_emits_only_on_success(self):
        from ont.integrations.delivery import verify
        import subprocess
        image='registry/test@sha256:'+'a'*64
        with tempfile.TemporaryDirectory() as tmp,patch('ont.integrations.delivery.command',side_effect=['a'*40,'']),patch('ont.integrations.delivery.subprocess.run',side_effect=subprocess.CalledProcessError(1,'test')):
            with self.assertRaises(subprocess.CalledProcessError):verify(tmp,'a'*40,image,['pytest'])
    def test_invalid_credentials_are_rejected(self):
        p=Principals({'a'*40:{'tenant':'one','role':'admin'}})
        with self.assertRaises(PermissionError):p.authenticate('Bearer é'*40)
