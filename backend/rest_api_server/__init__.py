#!/usr/bin/env python
# coding=utf-8

# All imports are relative to the top 'backend' directory
import os, sys
import traceback
sys.path.append(os.path.abspath(os.path.join(os.curdir, '..')))
# 3rd party imports
try:
    from flask import Flask
    from flask_cors import CORS, cross_origin
except Exception as e:
    traceback.print_exc()
    sys.stderr.write("Failed to import some Python modules, use requirements.txt "
                     "to install 3rd party external dependencies")
    sys.exit(1)

# Internal imports
import util.bootstrap as bootstrap
import util.logger as logger

_log = logger.get_logger(__name__)

runtime_path = bootstrap.get_runtime_path()

# Create the Flask app and init config
app = Flask(__name__)

# Need Cross-origin headers for local development
CORS(app)

app.config['RUNTIME_WORKING_DIR'] = runtime_path
app.config['STATIC_DIR_PATH'] = os.path.join(runtime_path, "static")

_log.debug("RRUNTIME_WORKING_DIR: %s", app.config['RUNTIME_WORKING_DIR'])
_log.debug("STATIC_DIR_PATH: %s", app.config['STATIC_DIR_PATH'])

# Import other Flask sub-modules containing URL handlers
import default_routes
