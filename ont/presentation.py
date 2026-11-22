"""Prepare a repeatable, isolated demonstration using the actual workflow API.
Run: python -m scripts.presentation --prepare-only
Then: ONT_DB=data/presentation.sqlite3 python -m uvicorn ont.app:app --host 127.0.0.1 --port 3000
"""
import argparse
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
from ont.app import create_app


def prepare(path):
    path=Path(path)
    if path.exists():raise ValueError('Presentation database already exists; choose a new --db path to preserve prior work')
    app=create_app(path)
    token=os.environ.get('ONT_ADMIN_TOKEN','')
    headers={'Authorization':'Bearer '+token} if token else {}
    with TestClient(app) as client:
        def call(route,body):
            r=client.post('/api'+route,json=body,headers=headers)
            r.raise_for_status();return r.json()
        orders=[]
        for title,steps in [('Explore a new product feature',0),('Review a proposed implementation plan',2),('Review build-stage evidence',4),('Inspect a completed demonstration',5)]:
            r=call('/runs',{'title':title,'brief':'Presentation demonstration of Ont workflow state, review gates, and illustrative artifacts. No model, repository changes, or production deployment are performed.','mode':'demo'})
            for _ in range(steps):
                if r['status']=='awaiting_approval':r=call('/runs/'+r['id']+'/action',{'action':'approve'})
                r=call('/runs/'+r['id']+'/action',{'action':'simulate'})
            orders.append({'id':r['id'],'title':title,'status':r['status'],'mode':r['mode']})
    return {'database':str(path.resolve()),'orders':orders,'note':'All seeded orders are explicitly labeled demo simulations.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--db',default='data/presentation.sqlite3');p.add_argument('--prepare-only',action='store_true');args=p.parse_args()
    try:report=prepare(args.db)
    except ValueError as e:p.error(str(e))
    print(json.dumps(report,indent=2))
    if not args.prepare_only:
        import uvicorn
        uvicorn.run(create_app(args.db),host='127.0.0.1',port=3000)

if __name__=='__main__':main()
