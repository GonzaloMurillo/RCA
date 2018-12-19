#!/usr/bin/env python
# coding=utf-8

from rest_api_server import app
from flask import send_file, send_from_directory
import os
import util.logger as logger

_log = logger.get_logger(__name__)

@app.route("/")
def index():
    '''
    Serve the 'index.html' page by default
    '''
    return send_file(os.path.join(app.config['STATIC_DIR_PATH'], "index.html"))

@app.route('/<path:path>')
def route_static_files(path):
    '''
    Serve all other supporting files (*.js, *.css etc.)
    '''
    return send_from_directory(app.config['STATIC_DIR_PATH'], path)
