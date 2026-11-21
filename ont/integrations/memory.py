"""Scoped caller-supplied embedding retrieval; no provider or extractor coupling."""
import json
import math
import sqlite3

class SemanticMemory:
    def __init__(self,path):
        self.path=str(path)
        with sqlite3.connect(self.path) as c:c.execute('CREATE TABLE IF NOT EXISTS memory(tenant TEXT,id TEXT,text TEXT,embedding TEXT,PRIMARY KEY(tenant,id))')
    @staticmethod
    def vector(v):
        if not isinstance(v,list) or not v or len(v)>8192 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in v):raise ValueError('Invalid embedding')
        norm=math.sqrt(sum(x*x for x in v))
        if not norm or not math.isfinite(norm):raise ValueError('Invalid vector norm')
        return [x/norm for x in v]
    def put(self,tenant,key,text,embedding):
        v=self.vector(embedding)
        if not tenant or not key or len(text)>12000:raise ValueError('Invalid memory')
        with sqlite3.connect(self.path) as c:c.execute('INSERT OR REPLACE INTO memory VALUES (?,?,?,?)',(tenant,key,text,json.dumps(v)))
    def search(self,tenant,embedding,limit=5):
        if not 1<=limit<=100:raise ValueError('Limit out of bounds')
        v=self.vector(embedding)
        with sqlite3.connect(self.path) as c:rows=c.execute('SELECT id,text,embedding FROM memory WHERE tenant=?',(tenant,)).fetchall()
        ranked=[]
        for key,text,raw in rows:
            e=json.loads(raw)
            if len(e)!=len(v):continue
            ranked.append({'id':key,'text':text,'score':sum(a*b for a,b in zip(v,e))})
        return sorted(ranked,key=lambda r:(-r['score'],r['id']))[:limit]
