"""Installed Ont command line."""
import argparse

def main():
    parser=argparse.ArgumentParser(prog='ont',description='Ont software factory')
    parser.add_argument('--version',action='version',version='Ont 0.1.0')
    commands=parser.add_subparsers(dest='command',required=True)
    serve=commands.add_parser('serve',help='Start the control plane')
    serve.add_argument('--host',default='127.0.0.1');serve.add_argument('--port',type=int,default=3000)
    demo=commands.add_parser('demo',help='Prepare an isolated labeled demo and optionally serve it')
    demo.add_argument('--db',default='data/presentation.sqlite3');demo.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args()
    if args.command=='serve':
        import uvicorn
        uvicorn.run('ont.app:app',host=args.host,port=args.port)
    else:
        import json
        from .presentation import prepare
        try:report=prepare(args.db)
        except ValueError as error:parser.error(str(error))
        print(json.dumps(report,indent=2))
        if not args.prepare_only:
            import uvicorn
            from .app import create_app
            uvicorn.run(create_app(args.db),host='127.0.0.1',port=3000)

if __name__=='__main__':main()
