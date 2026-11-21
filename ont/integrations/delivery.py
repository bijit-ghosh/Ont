"""Checkout, isolated verification, and idempotent GitHub draft-PR adapters."""
import json
from pathlib import Path
import re
import subprocess

REPO=re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
SHA=re.compile(r'^[0-9a-f]{40}$')

def command(args,cwd=None,timeout=120):
    return subprocess.run(args,cwd=cwd,check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()

def checkout(repository,commit,destination,allowed):
    if repository not in allowed or not REPO.fullmatch(repository) or not SHA.fullmatch(commit):
        raise ValueError('Repository or immutable commit is not allowed')
    destination=Path(destination)
    if destination.exists():raise ValueError('Checkout destination must be new')
    command(['git','-c','protocol.file.allow=never','clone','--no-checkout','--no-recurse-submodules','https://github.com/'+repository+'.git',str(destination)])
    command(['git','checkout','--detach',commit],destination)
    actual=command(['git','rev-parse','HEAD'],destination)
    if actual!=commit:raise ValueError('Checkout commit mismatch')
    return actual

def verify(checkout_path,commit,image,test_argv,timeout=120):
    """Run operator-selected checks without shell expansion in a no-network container."""
    root=Path(checkout_path).resolve()
    if not SHA.fullmatch(commit) or command(['git','rev-parse','HEAD'],root)!=commit:raise ValueError('Verification commit mismatch')
    if command(['git','status','--porcelain','--untracked-files=all'],root):raise ValueError('Verification requires a clean committed checkout')
    if '@sha256:' not in image or not test_argv or any(not isinstance(s,str) for s in test_argv):raise ValueError('Pinned image and command array required')
    subprocess.run(['docker','run','--rm','--network=none','--read-only','--user=65534:65534','--cap-drop=ALL','--security-opt=no-new-privileges',
        '--memory=2g','--cpus=2','--pids-limit=128','--tmpfs=/tmp:rw,nosuid,size=256m','--mount',f'type=bind,source={root},target=/src,readonly','--workdir=/src',image,*test_argv],check=True,timeout=timeout,capture_output=True)
    return {'passed':True,'commit':commit,'command':json.dumps(test_argv),'image':image,'independent':True}

class GitHubDelivery:
    def __init__(self,repository,allowed,runner=command):
        if repository not in allowed or not REPO.fullmatch(repository):raise ValueError('Repository not allowed')
        self.repository=repository;self.run=runner
    def draft_pr(self,head,base,title,body_path):
        for branch in (head,base):
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./-]{0,150}',branch) or '..' in branch:raise ValueError('Invalid branch')
        existing=json.loads(self.run(['gh','pr','list','--repo',self.repository,'--head',head,'--base',base,'--state','all','--json','url']))
        if existing:return {'url':existing[0]['url'],'created':False}
        url=self.run(['gh','pr','create','--repo',self.repository,'--head',head,'--base',base,'--title',title,'--body-file',str(body_path),'--draft'])
        return {'url':url,'created':True}
