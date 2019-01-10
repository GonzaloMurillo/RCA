#!/usr/bin/env python
# coding=utf-8

from flask import jsonify, request
from rest_api_server import app
import os
from util import version, logger
import json

_log = logger.get_logger(__name__)

# Globals - Move to ctxdoing class/object
asup_file_save_path = None
asup_auto_cores_location = None
asup_elysium_serial_number = None

ASUP_FILE_INPUT_METHODS = {
    'FILE_UPLOAD': 1,
    'AUTO_CORES_PATH': 2,
    'ELYSIUM_SERIAL_NUMBER': 3
    }
asup_file_input_method = None

@app.route("/api/asup/file", methods=['POST'])
def asup_file_upload():
    global asup_file_save_path, asup_file_input_method
    
    _log.info("ASUP file uploaded: %s", request.files)
    
    f = request.files['asup']
    asup_file_save_path = os.path.join(app.config['RUNTIME_WORKING_DIR'], f.filename)
    f.save(asup_file_save_path)
    asup_file_input_method = ASUP_FILE_INPUT_METHODS['FILE_UPLOAD']
    _log.info('[asup_file_input_method=FILE_UPLOAD] ASUP file saved locally as: %s', asup_file_save_path)

    return (jsonify({}),
            200,
            {'ContentType': 'application/json'})

@app.route("/api/asup/auto_cores_path", methods=['POST'])
def asup_file_auto_cores_path():
    global asup_auto_cores_location, asup_file_input_method
    
    data = json.loads(request.data)
    asup_auto_cores_location = data['auto_cores_path']
    asup_file_input_method = ASUP_FILE_INPUT_METHODS['AUTO_CORES_PATH']
    _log.info('[asup_file_input_method=AUTO_CORES_PATH] ASUP file located at: %s', asup_auto_cores_location)
    
    return (jsonify({}),
            200,
            {'ContentType': 'application/json'})
    
@app.route("/api/asup/elysium_serial_number", methods=['POST'])
def asup_file_elysium_serial_number():
    global asup_elysium_serial_number, asup_file_input_method
    
    data = json.loads(request.data)
    asup_elysium_serial_number = data['elysium_serial_number']
    asup_file_input_method = ASUP_FILE_INPUT_METHODS['ELYSIUM_SERIAL_NUMBER']
    _log.info('[asup_file_input_method=ELYSIUM_SERIAL_NUMBER] Serial Number: %s', asup_elysium_serial_number)
    
    return (jsonify({}),
            200,
            {'ContentType': 'application/json'})