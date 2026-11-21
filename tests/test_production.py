import os
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from ont.app import create_app

class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.env=patch.dict(os.environ,{'ONT_ENV':'production','ONT_ADMIN_TOKEN':'a'*40,'ONT_WORKER_TOKEN':'w'*40,'ONT_ALLOWED_HOSTS':'testserver,127.0.0.1'})
        self.env.start()
        self.path=self.tmp.name+'/db.sqlite'
    def tearDown(self): self.env.stop();self.tmp.cleanup()
    def test_fail_closed_configuration(self):
        for overrides in [{'ONT_ADMIN_TOKEN':''},{'ONT_WORKER_TOKEN':'a'*40},{'ONT_ALLOWED_HOSTS':'*'},{'ONT_ALLOWED_HOSTS':''}]:
            with patch.dict(os.environ,overrides),self.assertRaises(RuntimeError):create_app(self.path)
    def test_health_auth_and_host(self):
        with TestClient(create_app(self.path)) as c:
            self.assertEqual(c.get('/health/live').status_code,200)
            self.assertEqual(c.get('/health/ready').status_code,200)
            self.assertEqual(c.get('/openapi.json').status_code,401)
            self.assertEqual(c.get('/health/live',headers={'host':'evil.example'}).status_code,400)
    def test_chunked_and_malformed_size(self):
        with TestClient(create_app(self.path)) as c:
            headers={'Authorization':'Bearer '+'a'*40}
            def chunks():
                for _ in range(12):yield b'x'*100000
            self.assertEqual(c.post('/api/runs',content=chunks(),headers=headers).status_code,413)
            self.assertEqual(c.post('/api/runs',content=b'{}',headers={**headers,'Content-Length':'invalid'}).status_code,413)
    def test_pagination_bounds(self):
        with TestClient(create_app(self.path)) as c:
            h={'Authorization':'Bearer '+'a'*40}
            self.assertEqual(c.get('/api/overview?limit=501',headers=h).status_code,422)
            self.assertEqual(c.get('/api/overview?offset=-1',headers=h).status_code,422)
            self.assertEqual(c.get('/api/overview?limit=1',headers=h).status_code,200)
