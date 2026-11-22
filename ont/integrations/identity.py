"""Trusted principal mapping and one-use PKCE transactions; no home-grown JWT verifier."""
import base64
import hashlib
import hmac
import secrets
import time
from urllib.parse import urlencode,urlparse,parse_qsl,urlunparse

class Principals:
    def __init__(self,keys):
        if not keys:raise ValueError('At least one principal is required')
        self.keys=keys
        for token,p in keys.items():
            if len(token)<32 or p.get('role') not in ['admin','reader','worker'] or not p.get('tenant','').isalnum():raise ValueError('Invalid principal mapping')
    def authenticate(self,authorization):
        if not isinstance(authorization,str) or not authorization.startswith('Bearer '):raise PermissionError('Bearer authentication required')
        token=authorization[len('Bearer '):]
        for expected,p in self.keys.items():
            if hmac.compare_digest(token.encode(),expected.encode()):return dict(p)
        raise PermissionError('Authentication required')
    @staticmethod
    def authorize(principal,path,method):
        role=principal['role']
        if path.startswith('/api/worker/'):return role=='worker'
        if path.startswith('/api') or path=='/openapi.json':return role=='admin' or (role=='reader' and method=='GET')
        return True

class PKCE:
    def __init__(self):self.pending={}
    def begin(self,authorization_url,client_id,redirect_uri,scope):
        auth=urlparse(authorization_url);redirect=urlparse(redirect_uri)
        if any(u.scheme!='https' or not u.hostname or u.username or u.password or u.fragment for u in (auth,redirect)):raise ValueError('Valid HTTPS endpoints required')
        now=time.monotonic()
        self.pending={k:v for k,v in self.pending.items() if v[0]>now}
        if len(self.pending)>=1000:raise ValueError('Too many pending OAuth transactions')
        state=secrets.token_urlsafe(32);verifier=secrets.token_urlsafe(48)
        challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
        self.pending[state]=(now+300,verifier)
        params=dict(parse_qsl(auth.query))
        params.update({'client_id':client_id,'redirect_uri':redirect_uri,'scope':scope,'response_type':'code','state':state,'code_challenge':challenge,'code_challenge_method':'S256'})
        return urlunparse(auth._replace(query=urlencode(params)))
    def consume(self,state):
        row=self.pending.pop(state,None)
        if not row or row[0]<time.monotonic():raise PermissionError('Expired or invalid OAuth state')
        return row[1]
