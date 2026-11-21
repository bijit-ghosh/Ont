"""Minimal local stdio MCP server exposing a read-only capability catalog."""
import json
import sys

def handle(request):
    method=request.get('method');rid=request.get('id')
    if rid is None:return None
    if method=='initialize':
        result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'ont','version':'0.2.0'}}
    elif method=='tools/list':result={'tools':[{'name':'ont_capabilities','description':'Read Ont integration boundaries','inputSchema':{'type':'object','properties':{},'additionalProperties':False}}]}
    elif method=='tools/call' and request.get('params',{}).get('name')=='ont_capabilities':
        result={'content':[{'type':'text','text':'Ont: control plane, worker protocol, evaluation, and optional trusted integrations. Live providers require operator configuration.'}]}
    elif method=='ping':result={}
    else:return {'jsonrpc':'2.0','id':rid,'error':{'code':-32601,'message':'Method not found'}}
    return {'jsonrpc':'2.0','id':rid,'result':result}

def main():
    for line in sys.stdin:
        try:
            if len(line)>100000:raise ValueError('Request too large')
            response=handle(json.loads(line))
        except (ValueError,TypeError,AttributeError):response={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid request'}}
        if response:print(json.dumps(response),flush=True)
if __name__=='__main__':main()
