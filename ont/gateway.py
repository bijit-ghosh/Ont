"""Tenant-isolated bearer gateway. Launch with uvicorn ont.gateway:application --factory.
SSO should terminate at a verified OIDC ingress; never trust arbitrary identity headers.
"""
import json
import os
from pathlib import Path
from starlette.requests import Request
from starlette.responses import JSONResponse
from .app import create_app
from .integrations.identity import Principals


def application():
    principals=Principals(json.loads(os.environ['ONT_PRINCIPALS']))
    root=Path(os.environ.get('ONT_TENANT_DATA','data/tenants')).resolve()
    admin=os.environ.get('ONT_ADMIN_TOKEN','');worker=os.environ.get('ONT_WORKER_TOKEN','')
    if len(admin)<32 or len(worker)<32 or admin==worker:raise ValueError('Distinct backend credentials required')
    apps={}
    for p in principals.keys.values():
        tenant=p['tenant']
        if tenant not in apps:apps[tenant]=create_app(root/tenant/'ont.sqlite3')
    default=next(iter(apps.values()))
    async def gateway(scope,receive,send):
        if scope['type']!='http':return await default(scope,receive,send)
        request=Request(scope)
        path=scope['path']
        if not (path.startswith('/api') or path=='/openapi.json'):
            return await default(scope,receive,send)
        try:
            authorization=request.headers.get('authorization','')
            if not authorization.startswith('Bearer '):raise PermissionError('Authentication required')
            p=principals.authenticate(authorization)
        except PermissionError:
            return await JSONResponse({'detail':'Authentication required'},401,headers={'WWW-Authenticate':'Bearer','Cache-Control':'no-store'})(scope,receive,send)
        if not principals.authorize(p,path,scope['method']):
            return await JSONResponse({'detail':'Role does not authorize this operation'},403,headers={'Cache-Control':'no-store'})(scope,receive,send)
        new=dict(scope)
        new['headers']=[(k,v) for k,v in scope['headers'] if k.lower()!=b'authorization']+[(b'authorization',('Bearer '+(worker if p['role']=='worker' else admin)).encode())]
        return await apps[p['tenant']](new,receive,send)
    return gateway
