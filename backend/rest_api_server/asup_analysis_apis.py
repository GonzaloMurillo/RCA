#!/usr/bin/env python
# coding=utf-8

from flask import jsonify, request
from rest_api_server import app
import datetime
import time
import os
from util import version, logger
import json
from rest_api_server.dellemc.datadomain import DataDomain
# from pdfhelper import PDFHelper


_log = logger.get_logger(__name__)

# Globals - Move to ctxdoing class/object
asup_file_save_path = []
asup_auto_cores_location = None
asup_elysium_serial_number = None
selected_replication_contexts = None
selected_asup_files = []

ASUP_FILE_INPUT_METHODS = {
    'FILE_UPLOAD': 1,
    'AUTO_CORES_PATH': 2,
    'ELYSIUM_SERIAL_NUMBER': 3
    }
asup_file_input_method = None

# This is for autosupport being provided as an upload

@app.route("/api/asup/file", methods=['POST', 'DELETE'])
def asup_file_upload():
    global asup_file_save_path, asup_file_input_method, selected_asup_files

    if request.method == 'POST':
        _log.debug("ASUP file uploaded: %s", request.files)

        f = request.files['asup']
        file_save_path = os.path.join(app.config['RUNTIME_WORKING_DIR'], f.filename)
        f.save(file_save_path)
        asup_file_save_path.append(file_save_path)
        asup_file_input_method = ASUP_FILE_INPUT_METHODS['FILE_UPLOAD']
        _log.info('[asup_file_input_method=FILE_UPLOAD] ASUP file saved locally as: %s', file_save_path)

    elif request.method == 'DELETE':
        _log.info("Reset uploaded ASUP files")
        asup_file_save_path = []
        selected_asup_files = []

    return (jsonify({}),
            200,
            {'ContentType': 'application/json'})

# This is for autosupport being provided as a path to /auto/cores

@app.route("/api/asup/auto_cores_path", methods=['POST'])
def asup_file_auto_cores_path():
    global asup_auto_cores_location, asup_file_input_method

    data = json.loads(request.data)
    asup_auto_cores_location = data['auto_cores_path']
    asup_file_input_method = ASUP_FILE_INPUT_METHODS['AUTO_CORES_PATH']
    _log.info('[asup_file_input_method=AUTO_CORES_PATH] ASUP file located at: %s', asup_auto_cores_location)
    _log.debug("Location of the autosupport files:{}".format(asup_auto_cores_location))
    return (jsonify({}),
            200,
            {'ContentType': 'application/json'})

# This is for autosupport being provided from Elysium

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

@app.route("/api/asup/list", methods=['GET', 'POST'])
def asup_files_list():
    '''
    For the selected input method, open each ASUP file and return a list of
    all ASUP files with their metadata.
    This API is used by the GUI to select which ASUP file(s) are to be analyzed

    :return: List of dicts
    '''
    global asup_file_input_method, asup_file_save_path, selected_asup_files
    _log.debug("Method asup_files_list")
    if request.method == 'GET':
        asup_files = []
        if ASUP_FILE_INPUT_METHODS['FILE_UPLOAD'] == asup_file_input_method:
            for f in asup_file_save_path:
                asup_file_save_path_escaped=f.encode("utf-8")
                dd_obj=DataDomain()
                _log.debug("Autosupport to use:{}".format(asup_file_save_path_escaped))
                dd_obj.use_asup_file(asup_file_save_path_escaped)
                _log.debug("Obtaining date of the autosupport:")
                generated_on_date_obtained_from_asup=dd_obj.get_generated_on()

                asup_file_metadata = {
                    'filePath': os.path.basename(f),
                    'generatedDate': generated_on_date_obtained_from_asup
                }
                asup_files.append(asup_file_metadata)
                _log.debug("Content of asup_files_metadata:{}".format(asup_files))
                generated_on_date_obtained_from_asup=""
                del dd_obj

        return (jsonify(asup_files),
                200,
                {'ContentType': 'application/json'})

    elif request.method == 'POST':
        selected_asup_files = json.loads(request.data)
        _log.info("Selected ASUP files for analysis: %s", selected_asup_files)

        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})


# Displaying just the source (and valid) replication context from the autosupport

@app.route("/api/asup/analysis/replication_contexts", methods=['GET', 'POST'])
def replication_contexts_list():
    global selected_replication_contexts, asup_file_input_method, dd, selected_asup_files
    # I do convert in global de dd object of class DataDomain

    _log.debug("Method replication_contexts_list")
    _log.debug(asup_file_input_method)

    # Backend for the upload method

    if(asup_file_input_method==1): #File has been uploaded

        _log.debug(selected_asup_files)
        number_of_asup_files=len(selected_asup_files)
        _log.debug("Number of asup files:{}".format(len(selected_asup_files)))

        if(number_of_asup_files==1):

            asup_file_save_path_escaped=selected_asup_files[0]['filePath'].encode("utf-8") # To remove issues with path in Windows
            _log.debug(asup_file_save_path_escaped)
            dd=DataDomain()
            dd.use_asup_file(asup_file_save_path_escaped) # Most of the backend is done in the class DataDomain, we create an instance
            dd.parse_asup_file_for_replication_contexts_info()

        elif (number_of_asup_files==2):
            # Ok, the user has selected two autosupport files, we need to calculate delta difference
            data_domain = []
            data_domain.append(DataDomain())
            data_domain.append(DataDomain())

            # We need to use strptime to convert the string to a proper date
            # The format of the date that comes from the asup is like Wed Mar 6 2019 06:21:44
            # Check:https://www.journaldev.com/23365/python-string-to-datetime-strptime
            if time.strptime(selected_asup_files[0]['generatedDate'],"%a %b %d %Y %H:%M:%S") < time.strptime(selected_asup_files[1]['generatedDate'],"%a %b %d %Y %H:%M:%S"):
                _log.debug("First if")
                _log.debug("{} is < than {}".format(selected_asup_files[0]['generatedDate'],selected_asup_files[1]['generatedDate']))
                #raw_input("Press a key")
                data_domain[0].use_asup_file(selected_asup_files[1]['filePath'])
                data_domain[1].use_asup_file(selected_asup_files[0]['filePath'])
                _log.warning("The asup of the newer:{}".format(selected_asup_files[1]['filePath']))
                _log.warning("The asup of the older:{}".format(selected_asup_files[0]['filePath']))

            elif time.strptime(selected_asup_files[0]['generatedDate'],"%a %b %d %Y %H:%M:%S") > time.strptime(selected_asup_files[1]['generatedDate'],"%a %b %d %Y %H:%M:%S"):

                _log.debug("Second if")
                _log.debug("{} is > than {}".format(selected_asup_files[0]['generatedDate'],selected_asup_files[1]['generatedDate']))
                #raw_input("Press a key")
                data_domain[0].use_asup_file(selected_asup_files[0]['filePath'])
                data_domain[1].use_asup_file(selected_asup_files[1]['filePath'])
                _log.warning("The asup of the newer:{}".format(selected_asup_files[0]['filePath']))
                _log.warning("The asup of the older:{}".format(selected_asup_files[1]['filePath']))

            elif selected_asup_files[0]['generatedDate'] == selected_asup_files[1]['generatedDate'] :

                # The GENERATED_DATE is the same, so this seems to be the same file, or in any case makes no sense to calculate delta differences
                _log.error("Both autosupports are the same file, it makes no sense to calculate the delta difference")
                return ("<br>Cannot calculate delta difference because both autosupports are the same file, <strong>try again by selecting 2 different ASUP files for the same Data Domain.</strong>",405,{'ContentType':'text/html'})

            # We know populate the context information for both the data_domain objects
            data_domain[0].parse_asup_file_for_replication_contexts_info()
            data_domain[1].parse_asup_file_for_replication_contexts_info()

            # Now data_domain[0] is the newer asup and data_domain[1] is the older one
            # We check here if both asups are referred to the same serial
            if(data_domain[0].serial_number==data_domain[1].serial_number):
                _log.debug("Both asups are referred to the same serial number ")

                data_domain[0].calculate_delta_difference(data_domain[1])
                _log.info("The delta difference of the object:{}".format(data_domain[0].return_lrepl_client_time_stats_delta))
                data_domain[0].make_lrepl_client_time_stats_equal_to_delta_time_stats()

                dd=data_domain[0] # We just point the dd object to newer dd, where the lrepl_client_time_stats are the delta difference, as we called make_lrepl_client_time_stats_equal_to_delta_time_stats()

            else:
                _log.debug("The serial number of both asups do not match")
                return ("The serial number of the uploaded ASUP files do not match, we cannot calculate the delta difference of different DataDomain systems.<br/>\
                    <ul>\
                        <li>%s: %s</li>\
                        <li>%s: %s</li>\
                        </ul>" % (selected_asup_files[0]['filePath'], data_domain[0].serial_number, selected_asup_files[1]['filePath'], data_domain[1].serial_number),405,{'ContentType':'text/html'})




    if request.method == 'GET':

        _log.debug("START of the method to display the contexts of the autosuport that has being uploaded")
        repl_ctx_list = []
        _log.debug("Replication Contexts frontend {}".format(dd.replication_contexts_frontend))
        for item in dd.replication_contexts_frontend: # In dd.replication_contexts_frontend, we have just the contexts displayed in the frontend, but we want to filter from them just to display source and valid replication contexts
            _log.debug("Searching for just source replication contexts")
            if(dd.is_source_context(item['ctx'])):
                _log.debug("The context{}, is a source replication context".format(item))
                _log.debug("Adding the context number:{} to the list of source and valid replication contexts".format(item))
                repl_ctx_list.append(item)


        _log.debug("Found %d source and valid replication contexts", len(repl_ctx_list))
        _log.debug("List to jsonify {}".format(repl_ctx_list))
        _log.debug("END of the method to display the contexts of the autosuport that has being uploaded")
        return (jsonify(repl_ctx_list),
                200,
                {'ContentType': 'application/json'})

    # Is this if we click backwards in the browser?
    elif request.method == 'POST':
        selected_replication_contexts = json.loads(request.data)


        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})

# This is where the real analysis of the context happens
@app.route("/api/asup/analysis/replication_contexts/time_spent", methods=['GET'])
def analyze_replication_contexts():
    # Call get_replication_analysis to analyze selected replication contexts
    _log.debug("Selected contexts for analysis: {}".format(selected_replication_contexts))

    temporal_data_structure=dd.get_replication_analysis(selected_replication_contexts,app)

    if(temporal_data_structure==-1): # This happens if the difference for one context between 2 dates is negative

        return ("<strong>NEGATIVE DELTA DIFFERENCE</strong><br><br>This could happen when the difference in the metrics for one context between two dates is negative.<br><br>If the DDFS has been restarted between the two selected dates, this error is normal because 'Lrepl Client Time Stats' is a cumulative metric that start from 0 whenever the FS is restarted.<br><br>In that case use the 'Single Autosupport Upload' to obtain metrics.<br>Otherwise report a problem sending an e-mail: gonzalo.murillotello@dell.com.", 405, {'ContentType': 'text/html'})

    else:

        final_data_structure=temporal_data_structure

        return (jsonify(final_data_structure),
                200,
                {'ContentType': 'application/json'})
