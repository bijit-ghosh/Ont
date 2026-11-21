import json
import os
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from fastapi.testclient import TestClient
from ont.app import create_app

class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=self.temp.name+'/db.sqlite'
        self.env=patch.dict(os.environ,{'ONT_ADMIN_TOKEN':'admin-secret','ONT_WORKER_TOKEN':'worker-secret'})
        self.env.start()
        self.client=TestClient(create_app(self.path))
        self.admin={'Authorization':'Bearer admin-secret'}
        self.worker={'Authorization':'Bearer worker-secret'}
    def tearDown(self):
        self.client.close();self.env.stop();self.temp.cleanup()
    def post(self,path,data,worker=False):
        return self.client.post('/api'+path,json=data,headers=self.worker if worker else self.admin)
    def new(self,mode='live'):
        r=self.post('/runs',{'title':'Add billing service','brief':'Implement metered billing with verification evidence.', 'mode':mode})
        self.assertEqual(r.status_code,201,r.text)
        return r.json()['id']
    def claim(self):return self.post('/worker/claim',{'worker':'test'},True).json()
    def result(self,c,**updates):
        d={'lease':c['lease'],'success':True,'summary':'stage finished','cost':1,'artifacts':[{'name':'evidence.txt','content':'test evidence'}]};d.update(updates)
        return self.post('/worker/'+c['run']['id']+'/result',d,True)
    def test_auth_boundaries(self):
        self.assertEqual(self.client.get('/api/overview').status_code,401)
        self.assertEqual(self.client.get('/api/overview',headers=self.worker).status_code,401)
        self.assertEqual(self.post('/worker/claim',{'worker':'x'}).status_code,401)
        r=self.client.post('/api/runs',json={},headers={**self.admin,'Origin':'https://evil.example'})
        self.assertEqual(r.status_code,403)
    def test_live_pipeline_gates_evidence_and_replay(self):
        rid=self.new()
        c=self.claim();self.assertEqual(c['run']['stage_name'],'triage')
        self.assertIsNone(self.claim()['run'])
        self.assertEqual(self.result(c).status_code,200)
        self.assertEqual(self.result(c).status_code,409)
        c=self.claim();self.assertEqual(c['run']['stage_name'],'spec')
        self.assertEqual(self.result(c).json()['status'],'awaiting_approval')
        self.assertIsNone(self.claim()['run'])
        self.assertEqual(self.post('/runs/'+rid+'/action',{'action':'approve'}).json()['stage'],2)
        c=self.claim();self.assertEqual(self.result(c).status_code,200)
        c=self.claim();self.assertEqual(self.result(c).json()['status'],'awaiting_approval')
        self.post('/runs/'+rid+'/action',{'action':'approve'})
        c=self.claim();self.assertEqual(self.result(c).status_code,422)
        evidence={'name':'verification.json','content':json.dumps({'passed':True,'command':'python -m unittest','commit':'abc123'})}
        r=self.result(c,artifacts=[evidence]);self.assertEqual(r.json()['status'],'completed')
        self.assertEqual(r.json()['cost'],5)
    def test_demo_does_not_execute_or_charge(self):
        rid=self.new('demo');self.assertIsNone(self.claim()['run'])
        for stage in range(5):
            r=self.post('/runs/'+rid+'/action',{'action':'simulate'})
            self.assertEqual(r.status_code,200)
            if r.json()['status']=='awaiting_approval': self.post('/runs/'+rid+'/action',{'action':'approve'})
        self.assertEqual(r.json()['status'],'demo_completed');self.assertEqual(r.json()['cost'],0)
        self.assertEqual(self.post('/runs/'+rid+'/action',{'action':'simulate'}).status_code,409)
    def test_live_cannot_simulate_or_skip_gates(self):
        rid=self.new()
        for action in ['simulate','approve','requeue']:
            self.assertEqual(self.post('/runs/'+rid+'/action',{'action':action}).status_code,409)
    def test_cancellation_invalidates_lease(self):
        rid=self.new();c=self.claim();self.post('/runs/'+rid+'/action',{'action':'cancel'})
        self.assertEqual(self.result(c).status_code,409)
    def test_expiry_recovery(self):
        rid=self.new();c=self.claim()
        with sqlite3.connect(self.path) as db: db.execute('UPDATE runs SET lease_until=0 WHERE id=?',(rid,))
        self.assertEqual(self.result(c).status_code,409)
        self.assertEqual(self.post('/runs/'+rid+'/action',{'action':'requeue'}).status_code,200)
        new=self.claim();self.assertNotEqual(new['lease'],c['lease'])
        self.assertEqual(self.result(c).status_code,409)
    def test_budget_and_snapshot(self):
        config={'name':'Test','repository':'bijit-ghosh/Ont','budget':1,'model':'test','approval_stages':['spec','review']}
        self.client.put('/api/factory',json=config,headers=self.admin)
        rid=self.new();config['budget']=50
        self.client.put('/api/factory',json=config,headers=self.admin)
        c=self.claim();self.assertEqual(c['remaining_budget'],1)
        self.assertEqual(self.result(c,cost=2).status_code,409)
        self.assertEqual(self.result(c,cost=1).json()['status'],'failed')
        self.assertIsNone(self.claim()['run'])
    def test_atomic_claim(self):
        self.new()
        with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(lambda _:self.claim(),range(4)))
        self.assertEqual(sum(r['run'] is not None for r in results),1)
    def test_persistence_export_and_hash(self):
        rid=self.new('demo');self.post('/runs/'+rid+'/action',{'action':'simulate'})
        c=TestClient(create_app(self.path))
        r=c.get('/api/runs/'+rid,headers=self.admin).json()
        self.assertEqual(len(r['artifacts']),1);self.assertEqual(len(r['artifacts'][0]['sha256']),64)
        exported=c.get('/api/export',headers=self.admin)
        self.assertEqual(exported.status_code,200);self.assertNotIn('lease',exported.json()['runs'][0])
        c.close()
    def test_invalid_requests(self):
        self.assertEqual(self.post('/runs',{'title':'   ','brief':'           '}).status_code,422)
        config={'name':'Test','repository':'https://bad','budget':-1,'model':'test','approval_stages':['verify']}
        self.assertEqual(self.client.put('/api/factory',json=config,headers=self.admin).status_code,422)
    def test_rejection_is_terminal(self):
        rid=self.new('demo')
        for _ in range(2):self.post('/runs/'+rid+'/action',{'action':'simulate'})
        self.assertEqual(self.post('/runs/'+rid+'/action',{'action':'reject'}).json()['status'],'failed')
        self.assertEqual(self.post('/runs/'+rid+'/action',{'action':'approve'}).status_code,409)
    def test_heartbeat(self):
        self.new();c=self.claim()
        self.assertEqual(self.post('/worker/'+c['run']['id']+'/heartbeat',{'lease':c['lease']},True).status_code,200)

if __name__=='__main__': unittest.main()
