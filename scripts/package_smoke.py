"""Install the built wheel away from the checkout and test its bundled UI and demo."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
wheel=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else next(Path('dist').glob('*.whl')).resolve()
with tempfile.TemporaryDirectory(prefix='ont-wheel-') as tmp:
    target=Path(tmp)/'installed'
    subprocess.run([sys.executable,'-m','pip','install','--no-deps','--no-compile','--target',str(target),str(wheel)],check=True)
    env=os.environ.copy();env.update(PYTHONPATH=str(target),ONT_ENV='development',ONT_ALLOWED_HOSTS='',ONT_ADMIN_TOKEN='',ONT_WORKER_TOKEN='')
    code='''
import json
from pathlib import Path
from fastapi.testclient import TestClient
from ont.app import WEB,create_app
from ont.presentation import prepare
assert 'installed' in str(WEB) and WEB.name=='static',str(WEB)
with TestClient(create_app('isolated.sqlite3')) as client:
    for path in ['/','/assets/app.js','/assets/style.css','/health/ready']:
        r=client.get(path);assert r.status_code==200,(path,r.status_code)
r=prepare('demo.sqlite3')
assert len(r['orders'])==4 and r['orders'][-1]['status']=='demo_completed'
print(json.dumps({'wheel_smoke':'passed','bundled_assets':True,'isolated_demo':True}))
'''
    subprocess.run([sys.executable,'-c',code],cwd=tmp,env=env,check=True)
    subprocess.run([sys.executable,'-m','ont.cli','--version'],cwd=tmp,env=env,check=True)
