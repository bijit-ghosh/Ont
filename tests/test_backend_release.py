"""Presentation-release regression checks for startup auth and gateway login."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from ont.app import create_app
from ont.gateway import application

class BackendReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.settings={'ONT_ENV':'production','ONT_ADMIN_TOKEN':'a'*40,
                       'ONT_WORKER_TOKEN':'w'*40,'ONT_ALLOWED_HOSTS':'testserver'}
        self.env=patch.dict(os.environ,self.settings);self.env.start()
    def tearDown(self):
        self.env.stop();self.tmp.cleanup()
    def test_running_app_keeps_validated_credentials(self):
        with TestClient(create_app(Path(self.tmp.name)/'app.db')) as c:
            with patch.dict(os.environ,{'ONT_ADMIN_TOKEN':'','ONT_WORKER_TOKEN':''}):
                self.assertEqual(c.get('/api/overview').status_code,401)
                self.assertEqual(c.post('/api/worker/claim',json={'worker':'probe'}).status_code,401)
                result=c.get('/api/overview',headers={'Authorization':'Bearer '+'a'*40})
                self.assertEqual(result.status_code,200)
                self.assertTrue(result.json()['auth_enabled']);self.assertTrue(result.json()['worker_enabled'])
    def test_enormous_content_length_fails_closed(self):
        with TestClient(create_app(Path(self.tmp.name)/'app.db')) as c:
            r=c.post('/api/runs',content=b'{}',headers={'Authorization':'Bearer '+'a'*40,'Content-Length':'9'*5000})
            self.assertEqual(r.status_code,413)
    def test_gateway_challenges_invalid_auth_but_denies_valid_role(self):
        with patch.dict(os.environ,{'ONT_TENANT_DATA':self.tmp.name,
            'ONT_PRINCIPALS':json.dumps({'r'*40:{'tenant':'acme','role':'reader'}})}):
            with TestClient(application()) as c:
                for header in ['', 'r'*40, 'Bearer wrong']:
                    r=c.get('/api/overview',headers={'Authorization':header})
                    self.assertEqual(r.status_code,401)
                    self.assertEqual(r.headers['www-authenticate'],'Bearer')
                r=c.get('/api/overview',headers={'Authorization':'Bearer '+'r'*40})
                self.assertEqual(r.status_code,200)
                r=c.post('/api/runs',json={},headers={'Authorization':'Bearer '+'r'*40})
                self.assertEqual(r.status_code,403)

if __name__=='__main__':unittest.main()
