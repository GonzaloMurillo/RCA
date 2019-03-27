#!/usr/bin/env python
# coding=utf-8
import flask_login
from flask import jsonify, request, session
from flask_login import login_user, logout_user
import json

from auth.user_auth import DellUser
from rest_api_server import app, login_manager

from util import logger

_log = logger.get_logger(__name__)


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
