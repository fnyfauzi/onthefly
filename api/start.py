
if __name__ == '__main__':
    import signal, uvicorn
    import os.path as op
    import socket
    from app.utils.log import config_log

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    log_config = config_log(op.abspath(op.dirname(__file__)), 'debug')
    uvicorn.run('app.main:app', host='0.0.0.0', port=4178, log_config=log_config, reload=False)
