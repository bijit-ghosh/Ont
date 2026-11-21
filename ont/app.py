"""Ont control plane. Single-tenant MVP; no task text is executed by this server."""
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
STAGES = ['triage', 'spec', 'build', 'review', 'verify']
DEFAULT = {'name': 'Product engineering', 'repository': 'bijit-ghosh/Ont', 'budget': 20.0,
           'model': 'Bring your own harness', 'approval_stages': ['spec', 'review']}


def create_app(db_path=None):
    db_path = str(db_path or os.getenv('ONT_DB', ROOT / 'data' / 'ont.sqlite3'))
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    @contextmanager
    def db():
        con = sqlite3.connect(db_path, timeout=15)
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON')
        try:
            con.execute('BEGIN IMMEDIATE')
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS runs (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, brief TEXT NOT NULL, mode TEXT NOT NULL,
          status TEXT NOT NULL, stage INTEGER NOT NULL DEFAULT 0, budget REAL NOT NULL,
          cost REAL NOT NULL DEFAULT 0, config TEXT NOT NULL, created REAL NOT NULL,
          updated REAL NOT NULL, lease TEXT, lease_until REAL, worker TEXT);
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL REFERENCES runs(id),
          kind TEXT NOT NULL, message TEXT NOT NULL, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS artifacts (
          id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), stage TEXT NOT NULL,
          name TEXT NOT NULL, content TEXT NOT NULL, sha256 TEXT NOT NULL, created REAL NOT NULL);
        ''')
        c.execute('INSERT OR IGNORE INTO settings VALUES (?,?)', ('factory', json.dumps(DEFAULT)))
    app = FastAPI(title='Ont Software Factory', version='0.1.0', docs_url=None, redoc_url=None)
    def event(c, rid, kind, message):
        c.execute('INSERT INTO events(run_id,kind,message,created) VALUES (?,?,?,?)', (rid,kind,message,time.time()))
    def get(c, rid):
        row = c.execute('SELECT * FROM runs WHERE id=?', (rid,)).fetchone()
        if row is None: raise HTTPException(404, 'Run not found')
        return dict(row)
    def public(r):
        r = dict(r)
        r.pop('lease', None)
        r.pop('lease_until', None)
        r['config'] = json.loads(r['config'])
        r['stage_name'] = STAGES[r['stage']]
        return r
    def artifact(c,r,name,content):
        c.execute('INSERT INTO artifacts VALUES (?,?,?,?,?,?,?)',
                  (secrets.token_hex(8),r['id'],STAGES[r['stage']],name,content,hashlib.sha256(content.encode()).hexdigest(),time.time()))
    def transition(c,r):
        if STAGES[r['stage']] in json.loads(r['config'])['approval_stages']:
            status, stage = 'awaiting_approval', r['stage']
        elif r['stage'] == len(STAGES)-1:
            status, stage = ('demo_completed' if r['mode']=='demo' else 'completed'),r['stage']
        else: status,stage = 'queued',r['stage']+1
        c.execute('UPDATE runs SET status=?,stage=?,lease=NULL,lease_until=NULL,updated=? WHERE id=?', (status,stage,time.time(),r['id']))
        event(c,r['id'],status,'Stage finished; '+('human approval required' if status=='awaiting_approval' else status.replace('_',' ')))
    @app.middleware('http')
    async def security(req: Request, call_next):
        # Token remains in environment/session memory, never in shipped source.
        if req.url.path.startswith('/api'):
            worker = req.url.path.startswith('/api/worker/')
            key = os.getenv('ONT_WORKER_TOKEN' if worker else 'ONT_ADMIN_TOKEN', '')
            if worker and not key:
                return JSONResponse({'detail':'Worker access disabled; configure ONT_WORKER_TOKEN'},503)
            if key and not hmac.compare_digest(req.headers.get('authorization',''), 'Bearer '+key):
                return JSONResponse({'detail':'Authentication required'},401)
            origin = req.headers.get('origin')
            if origin and origin != str(req.base_url).rstrip('/'):
                return JSONResponse({'detail':'Cross-origin request rejected'},403)
            if req.headers.get('content-length','0').isdigit() and int(req.headers.get('content-length','0'))>1_100_000:
                return JSONResponse({'detail':'Request too large'},413)
        response = await call_next(req)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Content-Security-Policy']="default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        if req.url.path.startswith('/api'): response.headers['Cache-Control']='no-store'
        return response
    @app.get('/api/overview')
    def overview():
        with db() as c:
            runs = [public(r) for r in c.execute('SELECT * FROM runs ORDER BY created DESC')]
            config = json.loads(c.execute("SELECT value FROM settings WHERE key='factory'").fetchone()[0])
        return {'runs':runs,'factory':config,'stages':STAGES,
                'auth_enabled':bool(os.getenv('ONT_ADMIN_TOKEN')), 'worker_enabled':bool(os.getenv('ONT_WORKER_TOKEN'))}
    @app.put('/api/factory')
    def factory(data: Factory):
        with db() as c:
            c.execute("UPDATE settings SET value=? WHERE key='factory'",(json.dumps(data.model_dump()),))
        return data
    @app.post('/api/runs',status_code=201)
    def create(data: NewRun):
        rid = 'ont-'+secrets.token_hex(4)
        with db() as c:
            config=json.loads(c.execute("SELECT value FROM settings WHERE key='factory'").fetchone()[0])
            now=time.time()
            c.execute('INSERT INTO runs(id,title,brief,mode,status,budget,config,created,updated) VALUES (?,?,?,?,?,?,?,?,?)',
                      (rid,data.title.strip(),data.brief.strip(),data.mode,'queued',config['budget'],json.dumps(config),now,now))
            event(c,rid,'created', 'Demo simulation created' if data.mode=='demo' else 'Execution queued; awaiting an external worker')
            return public(get(c,rid))
    @app.get('/api/runs/{rid}')
    def detail(rid:str):
        with db() as c:
            r=public(get(c,rid))
            r['events']=[dict(x) for x in c.execute('SELECT * FROM events WHERE run_id=? ORDER BY id',(rid,))]
            r['artifacts']=[dict(x) for x in c.execute('SELECT * FROM artifacts WHERE run_id=? ORDER BY created',(rid,))]
            return r
    @app.post('/api/runs/{rid}/action')
    def action(rid:str,data: Action):
        with db() as c:
            r=get(c,rid)
            if data.action=='cancel':
                if r['status'] in ['completed','demo_completed','cancelled','failed']: raise HTTPException(409,'Run is already terminal')
                c.execute("UPDATE runs SET status='cancelled',lease=NULL,lease_until=NULL,updated=? WHERE id=?",(time.time(),rid))
                event(c,rid,'cancelled','Cancelled by operator; late worker results will be rejected')
            elif data.action in ['approve','reject']:
                if r['status']!='awaiting_approval': raise HTTPException(409,'Run is not awaiting approval')
                status='queued' if data.action=='approve' else 'failed'
                c.execute('UPDATE runs SET status=?,stage=?,updated=? WHERE id=?',(status,r['stage']+1 if data.action=='approve' else r['stage'],time.time(),rid))
                event(c,rid,data.action,data.note or ('Approved by operator' if data.action=='approve' else 'Rejected by operator'))
            elif data.action=='requeue':
                if r['status']!='running' or (r['lease_until'] or 0)>time.time(): raise HTTPException(409,'Only an expired worker lease can be requeued')
                c.execute("UPDATE runs SET status='queued',lease=NULL,lease_until=NULL,updated=? WHERE id=?",(time.time(),rid))
                event(c,rid,'requeued','Expired lease reset by operator; inspect external side effects before retrying')
            else:
                if r['mode']!='demo' or r['status']!='queued': raise HTTPException(409,'Only queued demo stages can be simulated')
                stage=STAGES[r['stage']]
                content=f'# Simulated {stage}\n\nTask: {r["title"]}\n\nThis is a demonstration artifact, not agent output. No repository was changed, no model was called, and no tests were executed.\n\n'
                content += {'triage':'Scope the request, identify affected components, and define acceptance criteria.',
                            'spec':'Proposed flow: inspect repository → implement → verify. Operator review is required.',
                            'build':'A real harness would produce a patch here. This simulation produces no code.',
                            'review':'Review the patch and its supporting evidence before approving verification.',
                            'verify':'A real worker must submit verification evidence. This demo cannot establish correctness.'}[stage]
                artifact(c,r,stage+'-demo.md',content)
                event(c,rid,'simulation',f'Simulated {stage}; $0 charged')
                transition(c,r)
            return public(get(c,rid))
    @app.post('/api/worker/claim')
    def claim(data: Claim):
        with db() as c:
            row=c.execute("SELECT * FROM runs WHERE status='queued' AND mode='live' AND cost<budget ORDER BY created LIMIT 1").fetchone()
            if row is None: return {'run':None}
            r=dict(row); token=secrets.token_urlsafe(32); until=time.time()+300
            c.execute("UPDATE runs SET status='running',worker=?,lease=?,lease_until=?,updated=? WHERE id=?",(data.worker,token,until,time.time(),r['id']))
            event(c,r['id'],'claimed',f'{data.worker} claimed {STAGES[r["stage"]]}')
            return {'run':public(get(c,r['id'])),'lease':token,'lease_until':until,'remaining_budget':r['budget']-r['cost'], 'artifacts':[dict(a) for a in c.execute('SELECT * FROM artifacts WHERE run_id=? ORDER BY created',(r['id'],))]}
    def check_lease(r,token):
        if r['status']!='running' or not hmac.compare_digest(r['lease'] or '',token) or r['lease_until']<time.time():
            raise HTTPException(409,'Lease expired, superseded, or run no longer active')
    @app.post('/api/worker/{rid}/heartbeat')
    def heartbeat(rid:str,data: Lease):
        with db() as c:
            r=get(c,rid); check_lease(r,data.lease)
            until=time.time()+300
            c.execute('UPDATE runs SET lease_until=?,updated=? WHERE id=?',(until,time.time(),rid))
            return {'lease_until':until}
    @app.post('/api/worker/{rid}/result')
    def result(rid:str,data: Result):
        with db() as c:
            r=get(c,rid); check_lease(r,data.lease)
            if r['cost']+data.cost>r['budget']+1e-9: raise HTTPException(409,'Reported cost exceeds remaining budget; operator reconciliation required')
            if data.success and not data.artifacts: raise HTTPException(422,'Successful stages require an evidence artifact')
            if data.success and STAGES[r['stage']]=='verify' and not any(a.name=='verification.json' for a in data.artifacts):
                raise HTTPException(422,'Verification requires verification.json with test evidence')
            if data.success and STAGES[r['stage']]=='verify':
                try:
                    evidence=json.loads(next(a.content for a in data.artifacts if a.name=='verification.json'))
                    if evidence.get('passed') is not True or not isinstance(evidence.get('command'),str) or not evidence['command'].strip() or not isinstance(evidence.get('commit'),str) or not evidence['commit'].strip(): raise ValueError()
                except (ValueError,AttributeError): raise HTTPException(422,'Verification evidence needs passed=true, command, and commit')
            for a in data.artifacts: artifact(c,r,a.name,a.content)
            c.execute('UPDATE runs SET cost=cost+? WHERE id=?',(data.cost,rid))
            event(c,rid,'worker_result',data.summary)
            if not data.success:
                c.execute("UPDATE runs SET status='failed',lease=NULL,lease_until=NULL,updated=? WHERE id=?",(time.time(),rid))
            elif r['cost']+data.cost>=r['budget'] and r['stage']<len(STAGES)-1:
                c.execute("UPDATE runs SET status='failed',lease=NULL,lease_until=NULL,updated=? WHERE id=?",(time.time(),rid))
                event(c,rid,'budget','Accounted budget exhausted; no next stage dispatched')
            else: transition(c,r)
            return public(get(c,rid))
    @app.get('/api/export')
    def export():
        with db() as c:
            return {table:[dict(r) for r in c.execute('SELECT * FROM '+table)] for table in ['settings','events','artifacts']} | {'runs':[public(r) for r in c.execute('SELECT * FROM runs ORDER BY created DESC')]}
    @app.get('/')
    def index(): return FileResponse(ROOT/'web/index.html')
    app.mount('/assets',StaticFiles(directory=ROOT/'web'),name='assets')
    return app

class Factory(BaseModel):
    name:str=Field(min_length=1,max_length=80,pattern=r'.*\S.*')
    repository:str=Field(min_length=3,max_length=180,pattern=r'^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$')
    budget:float=Field(gt=0,le=1000,allow_inf_nan=False)
    model:str=Field(min_length=1,max_length=80)
    approval_stages:list[Literal['spec','review']]=Field(default=['spec','review'],max_length=2)
class NewRun(BaseModel):
    title:str=Field(min_length=3,max_length=160,pattern=r'.*\S.*')
    brief:str=Field(min_length=10,max_length=12000,pattern=r'[\s\S]*\S[\s\S]*')
    mode:Literal['demo','live']='demo'
class Action(BaseModel):
    action:Literal['approve','reject','cancel','simulate','requeue']
    note:str=Field(default='',max_length=1000)
class Claim(BaseModel):
    worker:str=Field(min_length=1,max_length=80)
class Lease(BaseModel):
    lease:str=Field(min_length=16,max_length=100)
class Artifact(BaseModel):
    name:str=Field(min_length=1,max_length=120)
    content:str=Field(max_length=150000)
class Result(Lease):
    success:bool
    summary:str=Field(min_length=1,max_length=4000)
    cost:float=Field(default=0,ge=0,le=1000,allow_inf_nan=False)
    artifacts:list[Artifact]=Field(default=[],max_length=6)

app=create_app()
