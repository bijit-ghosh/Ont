"""Accept the standard preview host/port flags and start the ASGI server."""
import argparse
import uvicorn
p=argparse.ArgumentParser()
p.add_argument('--host',default='127.0.0.1')
p.add_argument('--port',type=int,default=3000)
p.add_argument('--strictPort',action='store_true')
a=p.parse_args()
uvicorn.run('ont.app:app',host=a.host,port=a.port)
