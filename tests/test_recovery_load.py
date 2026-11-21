import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from fastapi.testclient import TestClient
from ont.app import create_app

class RecoveryLoadTests(unittest.TestCase):
    def test_workload_backup_restore(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'ONT_ENV':'development','ONT_ADMIN_TOKEN':'test-admin','ONT_WORKER_TOKEN':'test-worker','ONT_ALLOWED_HOSTS':''}):
            db=Path(tmp)/'db.sqlite';client=TestClient(create_app(db));h={'Authorization':'Bearer test-admin'}
            start=time.monotonic()
            def create(i):
                return client.post('/api/runs',headers=h,json={'title':f'Load task {i}','brief':'Acceptance checks for synthetic concurrency workload.','mode':'live'})
            with ThreadPoolExecutor(max_workers=8) as pool:created=list(pool.map(create,range(100)))
            self.assertTrue(all(r.status_code==201 for r in created))
            self.assertEqual(len({r.json()['id'] for r in created}),100)
            self.assertEqual(len(client.get('/api/overview?limit=50',headers=h).json()['runs']),50)
            self.assertEqual(len(client.get('/api/overview?limit=50&offset=50',headers=h).json()['runs']),50)
            backup=Path(tmp)/'backup.sqlite'
            subprocess.run([sys.executable,'scripts/backup.py',str(db),str(backup)],check=True,capture_output=True)
            restored=TestClient(create_app(backup))
            self.assertEqual(len(restored.get('/api/overview',headers=h).json()['runs']),100)
            with sqlite3.connect(backup) as c:self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            restored.close();client.close()
            print(f'Synthetic 100-run concurrency and restore check: {time.monotonic()-start:.2f}s')
    def test_improvement_loop_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            inbox=Path(tmp)/'in';inbox.mkdir();out=Path(tmp)/'out'
            rows=[dict(task=str(i),seed=0,split='holdout',policy=p,quality=q,cost=1,latency=10,safe=True) for i in range(25) for p,q in [('base',.7),('new',.9)]]
            (inbox/'eval.json').write_text(json.dumps(rows))
            cmd=[sys.executable,'scripts/improve_loop.py',str(inbox),str(out),'--baseline','base','--candidate','new','--once']
            for _ in range(2):subprocess.run(cmd,check=True,capture_output=True)
            reports=list(out.glob('*.json'));self.assertEqual(len(reports),1)
            r=json.loads(reports[0].read_text());self.assertTrue(r['eligible_for_review']);self.assertFalse(r['promoted'])
