"""Black-box production container smoke and restart test. No external services required."""
import json
import os
import secrets
import subprocess
import sys
import time

image=sys.argv[1] if len(sys.argv)>1 else 'ont-control-plane:validated'
name='ont-smoke-'+secrets.token_hex(5);volume=name+'-data'
env=os.environ.copy();env.update(ONT_ADMIN_TOKEN=secrets.token_urlsafe(40),ONT_WORKER_TOKEN=secrets.token_urlsafe(40))
def docker(*args,check=True):return subprocess.run(['docker','--host=unix:///var/run/docker.sock',*args],env=env,capture_output=True,text=True,check=check,timeout=30)
probe="import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/health/ready',timeout=2)"
def ready():
    for _ in range(40):
        if docker('exec',name,'python','-c',probe,check=False).returncode==0:return
        time.sleep(.25)
    raise RuntimeError('Container did not become ready')
check_code='''
import json,os,urllib.request,urllib.error
base='http://127.0.0.1:3000'
def call(path,method='GET',body=None,auth=True):
    req=urllib.request.Request(base+path,method=method,data=json.dumps(body).encode() if body else None,headers={**({'Authorization':'Bearer '+os.environ['ONT_ADMIN_TOKEN']} if auth else {}),'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=5) as r:return r.status,r.read(),{k.lower():v for k,v in r.headers.items()}
for path in ['/','/assets/app.js','/assets/style.css','/health/live','/health/ready']:
    status,content,headers=call(path,auth=False)
    assert status==200 and content
    assert headers.get('x-content-type-options')=='nosniff'
try:call('/api/overview',auth=False);raise AssertionError('Unauthenticated API allowed')
except urllib.error.HTTPError as e:assert e.code==401
_,body,_=call('/api/runs','POST',{'title':'Container smoke test','brief':'Validate production HTTP and restart persistence.','mode':'demo'})
r=json.loads(body);rid=r['id']
_,body,_=call('/api/runs/'+rid+'/action','POST',{'action':'simulate'})
assert json.loads(body)['stage']==1
_,body,_=call('/api/runs/'+rid)
assert len(json.loads(body)['artifacts'])==1
print(json.dumps({'id':rid,'checks':'assets, health, auth, create, stage, artifact'}))
'''
try:
    docker('volume','create',volume)
    docker('run','-d','--name',name,'--network=none','--cap-drop=ALL','--security-opt=no-new-privileges','--memory=512m','--cpus=1','--pids-limit=128',
           '-e','ONT_ADMIN_TOKEN','-e','ONT_WORKER_TOKEN','-e','ONT_ENV=production','-e','ONT_ALLOWED_HOSTS=127.0.0.1',
           '--mount','type=volume,source='+volume+',target=/app/data',image)
    ready();result=json.loads(docker('exec',name,'python','-c',check_code).stdout)
    docker('restart',name);ready()
    restore="import urllib.request,json,os; r=json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:3000/api/runs/"+result['id']+"',headers={'Authorization':'Bearer '+os.environ['ONT_ADMIN_TOKEN']}))); assert r['stage']==1 and len(r['artifacts'])==1; print('Restart persistence passed')"
    docker('exec',name,'python','-c',restore)
    print(json.dumps({'passed':True,'image':image,'http_checks':result['checks'],'restart_persistence':True,'network':'none'}))
finally:
    docker('rm','-f',name,check=False);docker('volume','rm',volume,check=False)
