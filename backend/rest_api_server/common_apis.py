#!/usr/bin/env python
# coding=utf-8

from flask import jsonify, request
from rest_api_server import app

from util import version, logger

_log = logger.get_logger(__name__)

@app.route("/api/version", methods=['GET'])
def get_version():
    result = {'version': version.__pretty_version__ }
    _log.info("REST API returns version: %s", result)

    return (jsonify(result),
            200,
            {'ContentType': 'application/json'})
