"""Bounded repeatable release gate. Fail immediately; fix defects before rerunning."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
p=argparse.ArgumentParser();p.add_argument('--cycles',type=int,default=3);a=p.parse_args()
if not 1<=a.cycles<=20:p.error('cycles must be between 1 and 20')
root=Path(__file__).resolve().parents[1]
checks=[[sys.executable,'-m','unittest','discover','-s','tests','-v'],[sys.executable,'-m','compileall','-q','ont','scripts'],['node','--check','web/app.js'],['git','diff','--check'],['bash','native/scheduler/check.sh']]
report={'started':time.time(),'cycles':a.cycles,'checks':[],'passed':False}
try:
    for cycle in range(a.cycles):
        for cmd in checks:
            result=subprocess.run(cmd,cwd=root)
            report['checks'].append({'cycle':cycle+1,'command':cmd,'exit_code':result.returncode})
            if result.returncode:raise SystemExit(result.returncode)
    report['passed']=True
finally:
    report['finished']=time.time()
    (root/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n')
