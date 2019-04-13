#!/usr/bin/env python
# coding=utf-8
import threading

import flask_login
import schedule
from flask import jsonify, request, session
from flask_login import login_user, logout_user
import json
from datetime import datetime, timedelta
import shutil
import time

from auth.user_auth import DellUser
from rest_api_server import app, login_manager
from rest_api_server.asup_analysis_apis import ReplCtxView, AsupView

from util import logger

_log = logger.get_logger(__name__)

# Time after which a session is considered to be inactive and automatically expired
AUTO_EXPIRE_SESSION_TIMEOUT = timedelta(seconds=15)

# Check for expired sessions at this interval (in minutes)
AUTO_EXPIRE_SESSION_INTERVAL = 10


@login_manager.user_loader
def load_user(user_id):
    '''
    Handler for looking up a DellUser object for a currently logged in user

    :param user_id: Unicode string
    :return: DellUser object or None
    '''
    return DellUser.get(user_id)


@app.route("/api/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        creds = json.loads(request.data)

        # No username/password for now, just login using email
        if '@dell.com' not in creds['email']:
            return ("Please use your <code>@dell.com</code> email address to login.",
                    400,
                    {'ContentType': 'text/html'})

        # Create a new DellUser object and pass it to Flask-login to start a session
        user = DellUser(creds['email'])
        login_user(user)
        session['ip'] = request.remote_addr

        _log.info("Logged in as user: %s", user)

        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})

    # For debugging only, not used by GUI
    if request.method == 'GET':
        val = session.get('ip', 'Not yet logged in')

        _log.info("IP: %s, Currently logged in user: %s", val, flask_login.current_user)

        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})


@app.route("/api/logout", methods=['GET'])
def logout():
    _log.info("Logged out user: %s", flask_login.current_user)
    logout_user()

    return (jsonify({}),
            200,
            {'ContentType': 'application/json'})


def auto_expire_sessions():
    sessions = ReplCtxView.get_dd_engine_objects()
    current_time = datetime.now()

    _log.info("[AUTO_EXPIRE] Begin auto-expiring %d sessions...", len(sessions))

    # Don't iterate over the dict itself because we are popping elements in it, create a copy of its keys instead
    for user in list(sessions):
        dd_obj = sessions[user]
        _log.debug("[AUTO_EXPIRE] Session for '%s' last used at %s with %s",
                   user, dd_obj.last_used_timestamp, dd_obj)
        if (current_time - dd_obj.last_used_timestamp) >= AUTO_EXPIRE_SESSION_TIMEOUT:
            _log.info("[AUTO_EXPIRE] Session for '%s' has expired", user)

            # Delete the reference to the DataDomain object
            ReplCtxView.remove_dd_engine_object_for_user(user)

            # Delete ASUP files for this user, if any
            asup_files_directory = AsupView.asup_directory_for_user(user)

            _log.info("[AUTO_EXPIRE] Deleting all ASUP files in directory: %s", asup_files_directory)
            shutil.rmtree(asup_files_directory, ignore_errors=True)
        else:
            _log.debug("[AUTO_EXPIRE] Session for '%s' has not yet expired", user)


def auto_expire_session_scheduler_thread():
    while True:
        _log.info("[AUTO_EXPIRE] Check for expired sessions every %d minutes", AUTO_EXPIRE_SESSION_INTERVAL)
        auto_expire_sessions()
        time.sleep(AUTO_EXPIRE_SESSION_INTERVAL)


def start_auto_expire_session_scheduler():
    _log.info("[AUTO_EXPIRE] Start scheduler at an interval of %d minutes", AUTO_EXPIRE_SESSION_INTERVAL)

    # Create a thread to run all scheduled tasks in
    t = threading.Thread(target=auto_expire_session_scheduler_thread)
    t.daemon = True

    # Let the thread run until the program terminates, no use-case for stopping it
    t.start()
