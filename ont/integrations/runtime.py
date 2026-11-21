"""Bounded fan-out and explicit Kubernetes release controller."""
from concurrent.futures import ThreadPoolExecutor
import re
from .delivery import command

def fan_out(tasks,worker,max_workers=4):
    if not 1<=max_workers<=16 or len(tasks)>100:raise ValueError('Fan-out limit')
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures=[pool.submit(worker,t) for t in tasks]
        return [f.result() for f in futures]

class KubernetesRelease:
    def __init__(self,context,namespace,deployment,container,allowed,runner=command):
        if (context,namespace,deployment,container) not in allowed:raise ValueError('Release target not authorized')
        self.args=['kubectl','--context',context,'--namespace',namespace];self.deployment=deployment;self.container=container;self.run=runner
    def rollout(self,image):
        if not re.fullmatch(r'[A-Za-z0-9._:/-]+@sha256:[a-f0-9]{64}',image):raise ValueError('Immutable image required')
        self.run(self.args+['set','image','deployment/'+self.deployment,self.container+'='+image])
        try:self.run(self.args+['rollout','status','deployment/'+self.deployment,'--timeout=120s'],timeout=130)
        except Exception:
            self.rollback();raise
        return {'status':'ready','image':image}
    def rollback(self):
        self.run(self.args+['rollout','undo','deployment/'+self.deployment])
        self.run(self.args+['rollout','status','deployment/'+self.deployment,'--timeout=120s'],timeout=130)
