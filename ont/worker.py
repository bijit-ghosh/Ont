"""Reference Docker harness bridge. Runs an operator-selected image, never host task commands.
Usage: python -m ont.worker --once
The harness reads /ont/task.json and writes /ont/result.json. See docs/WORKER.md.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

URL=os.getenv('ONT_URL','http://127.0.0.1:3000').rstrip('/')
TOKEN=os.getenv('ONT_WORKER_TOKEN','')
IMAGE=os.getenv('ONT_RUNNER_IMAGE','')
REPO=os.getenv('ONT_REPOSITORY','')

def api(path,body):
    req=urllib.request.Request(URL+'/api/worker/'+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+TOKEN})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)

def run_one():
    claim=api('claim',{'worker':os.getenv('ONT_WORKER_NAME','docker-runner')})
    if not claim['run']:return False
    run=claim['run'];rid=run['id'];lease=claim['lease'];name='ont-'+secrets.token_hex(6)
    # Fail closed on repository mismatch. Never clone a user-controlled location on the host.
    if run['config']['repository']!=REPO:
        api(rid+'/result',{'lease':lease,'success':False,'summary':'Worker repository allowlist mismatch','cost':0,'artifacts':[]})
        return True
    payload={**run,'remaining_budget':claim['remaining_budget'],'untrusted_brief':run['brief'],'prior_artifacts':claim.get('artifacts',[])}
    with tempfile.TemporaryDirectory(prefix='ont-run-') as tmp:
        root=Path(tmp);root.chmod(0o777)
        task=root/'task.json';task.write_text(json.dumps(payload));task.chmod(0o444)
        cmd=['docker','run','--rm','--name',name,'--network=none','--read-only','--cap-drop=ALL',
             '--security-opt=no-new-privileges','--pids-limit=128','--memory=2g','--cpus=2',
             '--user=65534:65534','--tmpfs=/tmp:rw,noexec,nosuid,size=256m',
             '--mount',f'type=bind,source={tmp},target=/ont',IMAGE]
        started=time.monotonic();proc=None
        try:
            # Do not forward control-plane credentials into the container.
            proc=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            while proc.poll() is None:
                if time.monotonic()-started>240:
                    raise RuntimeError('Harness exceeded the 240 second stage deadline')
                time.sleep(2)
                api(rid+'/heartbeat',{'lease':lease})
            if proc.returncode:raise RuntimeError('Harness container failed; inspect worker-host Docker diagnostics')
            result_path=root/'result.json'
            if result_path.is_symlink() or not result_path.is_file() or result_path.stat().st_size>950000:
                raise RuntimeError('Missing or oversized harness result')
            result=json.loads(result_path.read_text())
            if not isinstance(result,dict):raise RuntimeError('Harness result must be a JSON object')
            result['lease']=lease
            api(rid+'/result',result)
            print(f'{rid}: stage result recorded',flush=True)
        except Exception as error:
            # If cancelled or the lease expired, this report is rejected as intended.
            try:api(rid+'/result',{'lease':lease,'success':False,'summary':str(error)[:1000],'cost':0,'artifacts':[]})
            except Exception:pass
            print(f'{rid}: worker stopped: {error}',flush=True)
        finally:
            subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
            if proc and proc.poll() is None:proc.kill();proc.wait()
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--once',action='store_true');args=p.parse_args()
    if not TOKEN or not IMAGE or not REPO:raise SystemExit('Set ONT_WORKER_TOKEN, ONT_RUNNER_IMAGE, and ONT_REPOSITORY. No harness is bundled.')
    subprocess.run(['docker','image','inspect',IMAGE],check=True,stdout=subprocess.DEVNULL)
    while True:
        try:worked=run_one()
        except (urllib.error.URLError,ValueError) as e:print('Worker API error:',e,flush=True);worked=False
        if args.once:break
        if not worked:time.sleep(5)

if __name__=='__main__':main()
