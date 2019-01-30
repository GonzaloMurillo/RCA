#!/usr/bin/env python
# coding=utf-8

import util.bootstrap
import os, sys, signal

import util.logger as logger
_log = logger.get_logger(__name__)

# Flask 'app' module, initialized when imported
flask_app = None
flask_server = None

# Port used to serve HTTP requests by Flask - use this in the frontend to make REST API calls
HTTP_API_PORT = 5000

 # Accept requests on all network interfaces (including the public IP)
HTTP_API_IP = '0.0.0.0'

def cleanup_before_shutdown():
    ''' Placeholder for cleanup operations, if any
    This function is called when the user stops the app by pressing ctrl+C
    '''
    pass

# Function pointers to be called on Flask app shutdown
SHUTDOWN_CALLBACKS = [cleanup_before_shutdown]
shutdown_in_progress = False

def start_flask_server():
    ''' Start the Flask REST API server

    This function blocks indefinitely
    '''
    global flask_app
    from rest_api_server import app
    #app.config['STATIC_FOLDER']='C:\\gonzalobackend\\ctxdoing\\backend\\static\\' # gonzalo

    flask_app = app

    from werkzeug.serving import make_server
    _log.info("Start Flask server on IP: %s:%d", HTTP_API_IP, HTTP_API_PORT)

    # Register the CTRL+C signal handler
    signal.signal(signal.SIGINT, stop_server)

    # This will start the REST API server and block forever
    # Current REST API implementation is not thread-safe, so Flask runs in a single threaded mode.
    # To make Flask handle multiple concurrent requests, pass 'threaded=True' to make_server()
    flask_server = make_server(HTTP_API_IP, HTTP_API_PORT, flask_app)
    flask_server.serve_forever()

def stop_server(signal, frame):
    ''' Handler for the CTRL+C signal

    Executes all registered shutdown callbacks and then quits with exit_code 0
    '''
    global shutdown_in_progress

    if shutdown_in_progress:
        _log.error("Already shutting down, please be patient...")
        return
    else:
        shutdown_in_progress = True

    _log.debug("Handling signal %s on frame %s", signal, frame)
    _log.info("Gracefully shutting down, please wait. This may take up to 1 minute.")

    for cb in SHUTDOWN_CALLBACKS:
        try:
            cb()
        except:
            _log.exception("Failed to execute callback %s on app shutdown", str(cb))

    _log.info("Execution complete, bye!")
    sys.exit(0)

def main():
    _log.info("Starting app...")
    start_flask_server()

if __name__ == '__main__':
    main()
