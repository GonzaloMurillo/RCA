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
selected_replication_contexts = None

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
    
@app.route("/api/asup/analysis/replication_contexts", methods=['GET', 'POST'])
def replication_contexts_list():
    global selected_replication_contexts, asup_file_input_method
    
    if request.method == 'GET':
        # Call ctxdoing to analyze the ASUP file and get a list of repl ctx
        # Create an object, TODO if-else for different asup_file_input_method
        # ctxdoing = AsupAnalyzer(asup_file_input_method, asup_file_save_path)
        # repl_ctx_list = ctxdoing.get_repl_ctx_list()
        
        repl_ctx_list = [
                {'ctx': 1, 
                 'source': {
                     'host': 'dd390gcsr01.nam.nsroot.net',
                     'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep', 
                     },
                 'destination': {
                     'host': 'dd390gcsr02.nam.nsroot.net',
                     'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep'
                    }
                },
                {'ctx': 2, 
                 'source': {
                     'host': 'dd390gcsr01.nam.nsroot.net',
                     'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu2_rep', 
                     },
                 'destination': {
                     'host': 'dd390gcsr02.nam.nsroot.net',
                     'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu2_rep'
                     }
                },
                {'ctx': 3, 
                 'source': {
                     'host': 'dd390gcsr01.nam.nsroot.net',
                     'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu3_rep', 
                     },
                 'destination': {
                     'host': 'dd390gcsr02.nam.nsroot.net',
                     'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu3_rep'
                     }
                }
            ]
        
        _log.info("Found %d replication contexts", len(repl_ctx_list))
        
        return (jsonify(repl_ctx_list),
                200,
                {'ContentType': 'application/json'})
        
    elif request.method == 'POST':
        selected_replication_contexts = json.loads(request.data)
        _log.info("Selected %d replication contexts for analysis", len(selected_replication_contexts))
        
        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})

@app.route("/api/asup/analysis/replication_contexts/time_spent", methods=['GET'])
def analyze_replication_contexts():    
    # Call ctxdoing to analyze selected replication contexts
    # 'data' is a list similar to that returned by ctxdoing.get_repl_ctx_list()
    # result = ctxdoing.analyze_repl_ctx(data)
    
    result = [
        {
          'ctx': 1,
          'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu1_rep',
          'destination': 'dd390gcsr01.nam.nsroot.net',
          # Save PNG generated by matplotlib in app.config['STATIC_DIR_PATH'] andgive it a UUID
          # Then set this path to /static/img-uuid-here.png
          'graphImage': 'assets/replicationgraph.png', 
          'ctxUsageTime': [
            { "key": "Total time spent by the replication context", "value": "11362471 seconds" },
            { "key": "Time sending references", "value": "0.2" },
            { "key": "Time sending segments", "value": "1.5" },
            { "key": "Time receiving references", "value": "0.4" },
            { "key": "Time waiting for references from destination", "value": "1.4" },
            { "key": "Time waiting getting references", "value": "2.9" },
            { "key": "Time local reading segments", "value": "93.6" },
            { "key": "Time sending small files", "value": "0.0" },
            { "key": "Time sending sketches", "value": "0.0" },
            { "key": "Time receiving bases", "value": "0.0" },
            { "key": "Time reading bases", "value": "0.0" },
            { "key": "Time getting chunk info", "value": "0.0" },
            { "key": "Time unpacking chunks of info", "value": "0.0" }
          ]
        },
        {
          'ctx': 2,
          'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu2_rep',
          'destination': 'dd390gcsr01.nam.nsroot.net',
          'graphImage': 'assets/replicationgraph.png',
          'ctxUsageTime': [
            { "key": "Total time spent by the replication context", "value": "11362471 seconds" },
            { "key": "Time sending references", "value": "0.2" },
            { "key": "Time sending segments", "value": "1.5" },
            { "key": "Time receiving references", "value": "0.4" },
            { "key": "Time waiting for references from destination", "value": "1.4" },
            { "key": "Time waiting getting references", "value": "2.9" },
            { "key": "Time local reading segments", "value": "93.6" },
            { "key": "Time sending small files", "value": "0.0" },
            { "key": "Time sending sketches", "value": "0.0" },
            { "key": "Time receiving bases", "value": "0.0" },
            { "key": "Time reading bases", "value": "0.0" },
            { "key": "Time getting chunk info", "value": "0.0" },
            { "key": "Time unpacking chunks of info", "value": "0.0" }
          ]
        },
        {
          'ctx': 3,
          'mtree': '/data/col1/dd390gcsr01_crebm4900_lsu3_rep',
          'destination': 'dd390gcsr01.nam.nsroot.net',
          'graphImage': 'assets/replicationgraph.png',
          'ctxUsageTime': [
            { "key": "Total time spent by the replication context", "value": "11362471 seconds" },
            { "key": "Time sending references", "value": "0.2" },
            { "key": "Time sending segments", "value": "1.5" },
            { "key": "Time receiving references", "value": "0.4" },
            { "key": "Time waiting for references from destination", "value": "1.4" },
            { "key": "Time waiting getting references", "value": "2.9" },
            { "key": "Time local reading segments", "value": "93.6" },
            { "key": "Time sending small files", "value": "0.0" },
            { "key": "Time sending sketches", "value": "0.0" },
            { "key": "Time receiving bases", "value": "0.0" },
            { "key": "Time reading bases", "value": "0.0" },
            { "key": "Time getting chunk info", "value": "0.0" },
            { "key": "Time unpacking chunks of info", "value": "0.0" }
          ]
        }
    ]
    
    _log.info("Analyzed %d replication contexts", len(result))
    
    return (jsonify(result),
            200,
            {'ContentType': 'application/json'})