"""Run layer-mapped, local enterprise evaluation scenarios with auditable evidence."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
KINDS={'local','mocked_contract','local_git_mocked_verifier','rust','frontend','container','enterprise_gate'}

def validate_catalog(data):
    layers=data['layers'];cases=data['cases']
    if len(layers)!=7 or len(set(layers))!=7 or not cases:raise ValueError('Exactly seven distinct layers and cases required')
    ids=set()
    for case in cases:
        if case['id'] in ids or case['layer'] not in layers or case['kind'] not in KINDS or not case['criterion']:raise ValueError('Invalid/duplicate case')
        if not re.fullmatch(r'[A-Z]{3}-[A-Z0-9]+',case['id']):raise ValueError('Invalid case ID')
        ids.add(case['id'])
        for selector in case.get('selectors',[]):
            if not re.fullmatch(r'tests\.[A-Za-z0-9_.]+',selector):raise ValueError('Untrusted selector')
        if case['kind'] in {'local','mocked_contract','local_git_mocked_verifier'} and not case.get('selectors'):raise ValueError('Executable case has no tests')
        if case['kind']=='enterprise_gate' and not case.get('requirement'):raise ValueError('Enterprise gate has no acceptance requirement')
    if {c['layer'] for c in cases if c['kind']!='enterprise_gate'}!=set(layers):raise ValueError('Every layer needs executable coverage')
    return data

def fingerprint(root):
    digest=hashlib.sha256();count=0
    for directory,dirs,files in os.walk(root):
        dirs[:]=sorted(d for d in dirs if d not in {'.git','.venv','target','build','dist','data','__pycache__','reports'} and not d.endswith('.egg-info'))
        for filename in sorted(files):
            p=Path(directory)/filename
            if p.suffix not in {'.py','.rs','.js','.mjs','.sh','.toml','.lock','.json'}:continue
            if p.name=='validation-report.json':continue
            digest.update(str(p.relative_to(root)).encode()+b'\0'+p.read_bytes());count+=1
    return {'sha256':digest.hexdigest(),'files':count}

def run_case(case,profile,image,output):
    result={k:case[k] for k in ['id','layer','criterion','kind']}
    if case['kind']=='enterprise_gate':return result|{'status':'blocked','reason':case['reason'],'required_action':case['requirement']}
    if case['kind']=='container' and profile!='deployment':return result|{'status':'blocked','reason':'deployment_profile_required','required_action':'Build the runtime image and run --profile deployment.'}
    if case['kind']=='rust':command=['bash','native/scheduler/check.sh'];needed=['cargo']
    elif case['kind']=='frontend':command=['node','tests/frontend_release.mjs'];needed=['node']
    elif case['kind']=='container':command=[sys.executable,'scripts/container_smoke.py',image];needed=['docker']
    else:command=[sys.executable,'-m','evals.probe',*case['selectors']];needed=[]
    missing=[name for name in needed if not shutil.which(name)]
    if missing:return result|{'status':'blocked','reason':'missing_tool','required_action':'Install '+', '.join(missing)}
    if case['kind']=='container':
        probe=subprocess.run(['docker','--host=unix:///var/run/docker.sock','image','inspect','--format','{{.Id}}',image],capture_output=True,timeout=30)
        if probe.returncode:return result|{'status':'blocked','reason':'image_unavailable','required_action':'Build '+image+' on the accessible Docker daemon.'}
        result['image_id']=probe.stdout.decode().strip()
    env=os.environ.copy();env.update(ONT_ENV='development',ONT_ADMIN_TOKEN='',ONT_WORKER_TOKEN='',ONT_ALLOWED_HOSTS='')
    start=time.monotonic()
    try:
        process=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=180)
        log=process.stdout+'\n'+process.stderr
        status='passed' if process.returncode==0 else 'failed'
        counts=None
        if case.get('selectors'):
            marker=next((line[len('ONT_EVAL_RESULT='):] for line in reversed(process.stdout.splitlines()) if line.startswith('ONT_EVAL_RESULT=')),None)
            counts=json.loads(marker) if marker else None
            if not counts or not counts['tests'] or counts['skipped'] or counts['expected_failures'] or counts.get('failures',0) or counts.get('errors',0) or counts.get('unexpected_successes',0):status='failed'
        result|={'status':status,'exit_code':process.returncode,'test_counts':counts}
    except subprocess.TimeoutExpired:
        log='Evaluation exceeded 180-second timeout.';result|={'status':'failed','reason':'timeout'}
    log_path=output/(case['id']+'.log');log_path.write_text(log[:500000])
    result|={'duration_seconds':round(time.monotonic()-start,4),'command':command,'evidence':log_path.name,'evidence_sha256':hashlib.sha256(log_path.read_bytes()).hexdigest()}
    return result

def summarize(results,layers,profile):
    required=[r for r in results if r['kind']!='enterprise_gate' and (profile=='deployment' or r['kind']!='container')]
    state=lambda rows:'failed' if any(r['status']=='failed' for r in rows) else 'blocked' if any(r['status']=='blocked' for r in rows) else 'passed'
    return {'automated_gate':state(required),'enterprise_gate':state(results),'counts':dict(Counter(r['status'] for r in results)),
            'layers':{layer:dict(Counter(r['status'] for r in results if r['layer']==layer)) for layer in layers}}

def markdown(report):
    lines=['# Ont enterprise evaluation scorecard','',f"Source: `{report['git_commit']}` · Profile: `{report['profile']}`",'',f"Automated gate: **{report['summary']['automated_gate'].upper()}** · Enterprise gate: **{report['summary']['enterprise_gate'].upper()}**",'',
           '| Layer | Passed | Failed | Blocked |','| --- | ---: | ---: | ---: |']
    for layer,counts in report['summary']['layers'].items():lines.append(f"| {layer.replace('_',' ')} | {counts.get('passed',0)} | {counts.get('failed',0)} | {counts.get('blocked',0)} |")
    lines+=['','## Scenarios','','| ID | Status | Evidence / required action |','| --- | --- | --- |']
    for r in report['results']:
        detail=r.get('required_action',f"[{r.get('evidence','')}](./{r.get('evidence','')})")
        lines.append(f"| {r['id']} | {r['status']} | {detail} |")
    lines+=['','Contract tests use controlled fixtures or mocked external services where labeled. A blocked gate is never counted as passed. This report is not enterprise certification.','']
    return '\n'.join(lines)

def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',choices=['core','deployment'],default='core');p.add_argument('--out',required=True);p.add_argument('--image',default='ont-control-plane:validated');p.add_argument('--require-enterprise',action='store_true');a=p.parse_args()
    output=Path(a.out).resolve()
    if output.exists():p.error('Output must be a new directory to preserve earlier evidence')
    # Keep generated evidence outside implementation inputs.
    catalog_path=Path(__file__).with_name('catalog.json');raw=catalog_path.read_bytes();catalog=validate_catalog(json.loads(raw))
    source=fingerprint(ROOT)
    output.mkdir(parents=True)
    sha=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip() or 'unversioned'
    report={'schema_version':1,'suite':catalog['suite'],'profile':a.profile,'git_commit':sha,'started_at':datetime.now(timezone.utc).isoformat(),'working_tree_dirty':bool(subprocess.run(['git','status','--porcelain'],cwd=ROOT,capture_output=True,text=True).stdout.strip()),'catalog_sha256':hashlib.sha256(raw).hexdigest(),'source':source,'results':[]}
    for case in catalog['cases']:
        try:r=run_case(case,a.profile,a.image,output)
        except Exception as error:r={k:case[k] for k in ['id','layer','criterion','kind']}|{'status':'failed','reason':type(error).__name__}
        report['results'].append(r);print(f"{r['id']}: {r['status']}",flush=True)
    report['finished_at']=datetime.now(timezone.utc).isoformat();report['summary']=summarize(report['results'],catalog['layers'],a.profile)
    report['source_changed_during_run']=fingerprint(ROOT)!=source
    if report['source_changed_during_run']:
        report['summary']['automated_gate']='failed'
        report['summary']['enterprise_gate']='failed'
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');(output/'scorecard.md').write_text(markdown(report))
    print(json.dumps(report['summary'],indent=2))
    if report['summary']['automated_gate']=='failed':return 1
    if report['summary']['automated_gate']=='blocked' or (a.require_enterprise and report['summary']['enterprise_gate']!='passed'):return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
