#!/usr/bin/env python
# coding=utf-8

# All imports are relative to the top 'backend' directory
import os, sys
import traceback

import telemetry

sys.path.append(os.path.abspath(os.path.join(os.curdir, '..')))
# 3rd party imports
try:
    from flask import Flask
    from flask_cors import CORS, cross_origin
    from flask_login import LoginManager
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
CORS(app, supports_credentials=True)

app.config['RUNTIME_WORKING_DIR'] = runtime_path
app.config['STATIC_DIR_PATH'] = os.path.join(runtime_path, "static")

_log.debug("RUNTIME_WORKING_DIR: %s", app.config['RUNTIME_WORKING_DIR'])
_log.debug("STATIC_DIR_PATH: %s", app.config['STATIC_DIR_PATH'])

# Route prefix for class-based views
app.config['URL_DEFAULT_PREFIX_FOR_API'] = "/api"

# Setup session management
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)

# Import other Flask sub-modules containing URL handlers
import rest_api_server.default_routes
import rest_api_server.session_mgmt_apis
import rest_api_server.common_apis
import rest_api_server.asup_analysis_apis

# Start the session auto-expiry thread
session_mgmt_apis.start_auto_expire_session_scheduler()

# Initialize the telemetry DB
from telemetry import db as telemetry
telemetry.initialize_db(runtime_path)
