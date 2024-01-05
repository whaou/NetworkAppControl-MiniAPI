def run():
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(
        'Run the MiniAPI server')
    parser.add_argument('--bind',
                        '-b',
                        type=str,
                        default='127.0.0.1',
                        help='interface to bind to')
    parser.add_argument('--port',
                        '-p',
                        type=int,
                        default=3001,
                        help='Port number of the Rx AtBridge service on the server')
    args = parser.parse_args()

    uvicorn.run("miniapi.main:app", host=args.bind, port=args.port, reload=False)
