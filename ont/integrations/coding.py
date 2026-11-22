"""Review-first coding workflow. Provider and executor remain explicitly configured."""
from pathlib import Path
import tempfile
from .delivery import checkout,command,verify,GitHubDelivery,SHA


def build_change(repository,source_commit,destination,allowed_repositories,model,brief,context,
                 verifier_image,test_argv,allowed_paths=('src/','tests/','web/')):
    """Create a tested local commit. Does not push, merge, or deploy."""
    checkout(repository,source_commit,destination,allowed_repositories)
    root=Path(destination)
    proposal=model.propose(brief,context)
    if len(proposal['patch'])>500000:raise ValueError('Patch too large')
    # git apply forbids traversal and .git paths; post-apply allowlist restricts scope further.
    with tempfile.NamedTemporaryFile(mode='w',suffix='.patch') as patch:
        patch.write(proposal['patch']);patch.flush()
        command(['git','apply','--check',patch.name],root)
        command(['git','apply',patch.name],root)
    command(['git','add','--intent-to-add','--all'],root)
    paths=command(['git','diff','--name-only'],root).splitlines()
    if not paths or any(not any(p.startswith(prefix) for prefix in allowed_paths) for p in paths):raise ValueError('Patch outside authorized paths')
    for p in paths:
        path=root/p
        if path.is_symlink():raise ValueError('Symlink changes require separate review')
    command(['git','add','--',*paths],root)
    command(['git','-c','user.name=Ont','-c','user.email=ont@localhost','-c','core.hooksPath=/dev/null','commit','-m','Ont proposed change'],root)
    commit=command(['git','rev-parse','HEAD'],root)
    evidence=verify(root,commit,verifier_image,test_argv)
    return {'summary':proposal['summary'],'commit':commit,'verification':evidence,'usage':proposal['usage'],'checkout':str(root)}


def publish_draft(result,repository,allowed_repositories,branch,base,body_path):
    """Explicit delivery step after review. Credentials belong to trusted host only."""
    delivery=GitHubDelivery(repository,allowed_repositories)
    evidence=result.get('verification',{})
    commit=result.get('commit','')
    if not SHA.fullmatch(commit) or evidence.get('passed') is not True or evidence.get('commit')!=commit:
        raise ValueError('Delivery requires passing verification for the exact commit')
    if not branch.startswith('ont/'):raise ValueError('Ont delivery branches must start with ont/')
    # Validate branch with Git before a remote write.
    command(['git','check-ref-format','--branch',branch])
    if command(['git','rev-parse','HEAD'],result['checkout'])!=result['commit']:raise ValueError('Delivery commit changed')
    expected='https://github.com/'+repository+'.git'
    remote=command(['git','remote','get-url','--push','origin'],result['checkout'])
    if remote not in (expected,expected.removesuffix('.git')):
        raise ValueError('Delivery remote does not match authorized repository')
    command(['git','push',expected,result['commit']+':refs/heads/'+branch],result['checkout'])
    return delivery.draft_pr(branch,base,'Ont: '+result['summary'][:150],body_path)
