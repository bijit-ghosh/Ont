"""Continuously evaluate newly recorded datasets. No model training or production writes."""
import argparse
import hashlib
import json
from pathlib import Path
import signal
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ont.improvement import evaluate
p=argparse.ArgumentParser();p.add_argument('inbox');p.add_argument('reports');p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True);p.add_argument('--once',action='store_true');p.add_argument('--interval',type=int,default=60);a=p.parse_args()
if a.interval<5:p.error('interval must be at least 5 seconds')
stop=False

def halt(*_):
    global stop
    stop=True
signal.signal(signal.SIGTERM,halt);signal.signal(signal.SIGINT,halt)
inbox=Path(a.inbox);reports=Path(a.reports);reports.mkdir(parents=True,exist_ok=True)
while not stop:
    for path in sorted(inbox.glob('*.json')):
        if stop:break
        try:
            if path.stat().st_size > 10_000_000: raise ValueError('Dataset exceeds 10 MB limit')
            raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
            target=reports/(digest+'.json')
            if target.exists():continue
            result=evaluate(json.loads(raw),a.baseline,a.candidate)
            result['dataset_sha256']=digest
            tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(target)
        except (ValueError,KeyError,TypeError,OSError) as e:
            print(f'{path.name}: evaluation failed: {e}',file=sys.stderr,flush=True)
            if a.once:raise SystemExit(1)
    if a.once:break
    # Short sleeps allow prompt signal shutdown.
    for _ in range(a.interval):
        if stop:break
        time.sleep(1)
