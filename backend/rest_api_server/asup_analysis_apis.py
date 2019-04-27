#!/usr/bin/env python
# coding=utf-8
import shutil
import tempfile

import flask_login
from flask import jsonify, request, session
from flask_classy import FlaskView, route
from flask_login import login_required, logout_user

from rest_api_server import app
import time
import os

from telemetry.db import VerdictEnum
from util import logger
import json
from rest_api_server.dellemc.datadomain import DataDomain
from telemetry import db as telemetry
# from pdfhelper import PDFHelper

_log = logger.get_logger(__name__)

class AsupView(FlaskView):
    """
    APIs for dealing with ASUP files

    /api/asup/...
    """
    decorators = [login_required]
    route_prefix = app.config['URL_DEFAULT_PREFIX_FOR_API']
    asup_file_save_path_base = tempfile.mkdtemp()

    ASUP_FILE_INPUT_METHODS = {
        'FILE_UPLOAD': 'FILE_UPLOAD',
        'AUTO_CORES_PATH': 'AUTO_CORES_PATH',
        'ELYSIUM_SERIAL_NUMBER': 'ELYSIUM_SERIAL_NUMBER'
        }

    @classmethod
    def delete_all_uploaded_files(cls):
        _log.info("Deleting all uploaded ASUP files at: %s", cls.asup_file_save_path_base)
        shutil.rmtree(cls.asup_file_save_path_base, ignore_errors=True)

    @classmethod
    def asup_directory_for_user(cls, user):
        """
        Get the absolute path to a directory where the specified user's ASUP files
        are uploaded

        :param user: Email address of the user
        :return:
        """
        path = os.path.abspath(os.path.join(cls.asup_file_save_path_base, user))
        _log.debug("ASUP files for user '%s' are at: %s", user, path)

        return path

    def _get_asup_file_save_path(self):
        """
        Get the ASUP file save path for the current user session

        :return: String
        """
        try:
            path = session['ASUP_FILE_UPLOAD_PATH']
        except KeyError:
            current_user_email = flask_login.current_user.email
            path = self.asup_directory_for_user(current_user_email)
            session['ASUP_FILE_UPLOAD_PATH'] = path

        # Always try to create the dir as the auto-expiry may have deleted it
        os.makedirs(path, exist_ok=True)
        return path

    def _get_available_files_path_list(self):
        """
        Get a list with paths to already uploaded (or sourced from somewhere) ASUP files

        :return: List of strings
        """
        path_list = []
        if self._get_asup_input_method() == self.ASUP_FILE_INPUT_METHODS['FILE_UPLOAD']:
            path_list = os.listdir(self._get_asup_file_save_path())
            path_list = list(map(lambda filename: os.path.join(self._get_asup_file_save_path(), filename), path_list))
            
        elif self._get_asup_input_method() == self.ASUP_FILE_INPUT_METHODS['AUTO_CORES_PATH']:
            path_list = self._find_asup_files_in_auto_cores(self._get_input_auto_cores_path())
            path_list = list(map(lambda filename: os.path.join(self._get_input_auto_cores_path(), filename), path_list))
        
        _log.debug("ASUP files available for current session: %s", path_list)

        return path_list

    def _delete_available_files(self):
        _log.info("Deleting all ASUP files at: %s", self._get_asup_file_save_path())
        shutil.rmtree(self._get_asup_file_save_path(), ignore_errors=True)

    @classmethod
    def get_selected_files_path_list(cls):
        """
        Get a list of user selected ASUPs as paths to already uploaded ASUP files

        :return: List of strings
        """
        try:
            path_list = session['ASUP_FILE_UPLOAD_SELECTED_PATH_LIST']
        except KeyError:
            session['ASUP_FILE_UPLOAD_SELECTED_PATH_LIST'] = []
            path_list = session['ASUP_FILE_UPLOAD_SELECTED_PATH_LIST']

        return path_list

    def _set_selected_files_path_list(self, list):
        """
        Set the list of user selected ASUPs in the current session

        :param list: List of strings
        """
        session['ASUP_FILE_UPLOAD_SELECTED_PATH_LIST'] = list

    def _set_asup_input_method(self, method):
        """
        Set the input method used for the current user session

        :param method: One of the methods in AsupView.ASUP_FILE_INPUT_METHODS
        """
        existing_method = session.get('ASUP_FILE_INPUT_METHOD', None)
        if existing_method and existing_method != method:
            _log.warn("Replacing existing method '%s' with new method '%s' for user '%s'",
                      existing_method, method, flask_login.current_user)

        session['ASUP_FILE_INPUT_METHOD'] = method

    def _get_asup_input_method(self):
        """
        Set the input method used for the current user session

        :return: One of the strings in AsupView.ASUP_FILE_INPUT_METHODS
                 Raises an exception if _set_asup_input_method() was never called
        """
        try:
            method = session['ASUP_FILE_INPUT_METHOD']
        except KeyError:
            _log.exception("ASUP file input method not yet set for the current user session: '%s'",
                           flask_login.current_user)
            raise

        return method
    
    def _set_input_auto_cores_path(self, auto_cores_path):
        session['INPUT_AUTO_CORES_PATH'] = auto_cores_path
        
    def _get_input_auto_cores_path(self):
        try:
            auto_cores_path = session['INPUT_AUTO_CORES_PATH']
        except:
            _log.exception("Input /auto/cores path not yet set!")
            raise
        
        return auto_cores_path
    
    def _walk_dir_for_files(self, path, filter_name):
        files = []
        try:
            for (dirpath, dirnames, filenames) in os.walk(path):
                files = [f for f in filenames if filter_name in f]
                
                # Do not search sub-dirs
                break
        except:
            _log.exception("Failed to list files in path '%s'", path)
            pass
        
        return files
    
    def _find_asup_files_in_auto_cores(self, path):
        # First look at the Durham /auto/cores
        asup_files_list = self._walk_dir_for_files(path, 'autosupport')
        
        # Then look at the Santa Clara /auto/cores
        if not asup_files_list:
            path = path.replace('/auto/cores', '/mnt/sc-cores')
            asup_files_list = self._walk_dir_for_files(path, 'autosupport')
        
        if asup_files_list:
            _log.info("%d ASUP files found at '%s', using this as the input path",
                      len(asup_files_list), path)
            self._set_input_auto_cores_path(path)
        
        return asup_files_list

    @route("upload/", methods=['POST', 'DELETE'])
    def upload(self):
        """
        Upload a single ASUP file from the browser

        Call DELETE once to reset any existing uploads
        Call POST multiple times, once for each ASUP file

        :return:
        """
        if request.method == 'POST':
            _log.debug("ASUP file uploaded: %s", request.files)

            f = request.files['asup']
            file_save_path = os.path.join(self._get_asup_file_save_path(), f.filename)
            try:
                f.save(file_save_path)
            except:
                _log.exeption("Failed to save uploaded file to disk: %s", file_save_path)
                return ("Failed to save the uploaded file on the server, please report this issue.",
                        500,
                        {'ContentType': 'text/html'})

            self._set_asup_input_method(self.ASUP_FILE_INPUT_METHODS['FILE_UPLOAD'])
            _log.info('[asup_file_input_method=FILE_UPLOAD] ASUP file saved locally as: %s', file_save_path)

        elif request.method == 'DELETE':
            _log.info("Reset uploaded ASUP files")
            self._delete_available_files()
            self.get_selected_files_path_list().clear()

        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})

    @route("auto_cores_path/", methods=['POST'])
    def auto_cores_path(self):
        data = json.loads(request.data)

        asup_auto_cores_location = data['auto_cores_path']
        
        asup_files_list = self._find_asup_files_in_auto_cores(asup_auto_cores_location)
        
        if not asup_files_list:
            _log.error("Did not find any ASUP files at '%s' for '%s'",
                       asup_auto_cores_location, flask_login.current_user.email)
            return ("No ASUP files found at <strong>'%s'</strong>, please check the path and try again.<br>"\
                    "Both Durham and Santa Clara /auto/cores mounts are checked." % (asup_auto_cores_location),
                    405,
                    {'ContentType': 'text/html'}
                    )
        
        self._set_asup_input_method(self.ASUP_FILE_INPUT_METHODS['AUTO_CORES_PATH'])
        _log.info('[asup_file_input_method=AUTO_CORES_PATH] ASUP file(s) located at: %s', asup_auto_cores_location)

        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})

    @route("elysium/", methods=['POST'])
    def elysium(self):
        data = json.loads(request.data)

        asup_elysium_serial_number = data['elysium_serial_number']

        # TODO: Retrieve ASUP files from Elysium using the serial number and other filters and
        #       save them locally, then populate the list
        self._get_available_files_path_list().extend([])
        self._set_asup_input_method(self.ASUP_FILE_INPUT_METHODS['ELYSIUM_SERIAL_NUMBER'])
        _log.info('[asup_file_input_method=ELYSIUM_SERIAL_NUMBER] Serial Number: %s', asup_elysium_serial_number)

        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})

    def metadata_list(self):
        """
        For the selected input method, open each ASUP file and return a list of
        all ASUP files with their metadata.
        This API is used by the GUI to select which ASUP file(s) are to be analyzed

        :return: List of dicts
        """
        asup_files = []

        if not len(self._get_available_files_path_list()):
            # We should never get to this point without having selected at lease one ASUP file, so this means
            # the user session has expired
            return force_logout()

        # ASUP_FILE_INPUT_METHOD doesn't matter, the path to all available files is populated in all methods
        for f in self._get_available_files_path_list():
            asup_file_save_path_escaped = f.encode("utf-8")

            # Create an ASUP parser instance
            dd_obj = DataDomain()
            _log.debug("Autosupport to use:{}".format(asup_file_save_path_escaped))
            dd_obj.use_asup_file(asup_file_save_path_escaped)

            # Parse the ASUP file to get metadata
            _log.debug("Obtaining date of the autosupport:")
            generated_on_date_obtained_from_asup = dd_obj.get_generated_on()

            # Fill in the response JSON
            asup_file_metadata = {
                'filePath': os.path.basename(f),
                'generatedDate': generated_on_date_obtained_from_asup
            }
            asup_files.append(asup_file_metadata)
            _log.debug("Content of asup_files_metadata:{}".format(asup_files))
            generated_on_date_obtained_from_asup = ""
            del dd_obj

        return (jsonify(asup_files),
                200,
                {'ContentType': 'application/json'})

    @route("select/", methods=['POST'])
    def select(self):
        """
        Select one or more ASUP files for analysis

        :return:
        """
        selected_asup_files = json.loads(request.data)

        for f in selected_asup_files:
            # The GUI doesn't get the full path, so convert it here before saving
            if self._get_asup_input_method() == self.ASUP_FILE_INPUT_METHODS['FILE_UPLOAD']:
                f['filePath'] = os.path.join(self._get_asup_file_save_path(), f['filePath'])
            elif self._get_asup_input_method() == self.ASUP_FILE_INPUT_METHODS['AUTO_CORES_PATH']:
                f['filePath'] = os.path.join(self._get_input_auto_cores_path(), f['filePath'])
            
        self._set_selected_files_path_list(selected_asup_files)

        _log.info("User '%s' selected %d ASUP files for analysis: %s",
                  flask_login.current_user.email, len(selected_asup_files), selected_asup_files)

        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})


class ReplCtxView(FlaskView):
    """
    APIs for dealing with Replication Contexts

    /api/replctx/...
    """
    decorators = [login_required]
    route_prefix = app.config['URL_DEFAULT_PREFIX_FOR_API']

    dd_engines = {}

    def _save_dd_engine_for_session(self, dd):
        """
        Save the Data Domain engine object for the current session

        :param dd:
        """
        current_user_email = flask_login.current_user.email
        _log.debug("Save DD object %s for session '%s'", dd, current_user_email)
        self.dd_engines[current_user_email] = dd

    def _get_dd_engine_for_session(self):
        """
        Get the previously saved DD engine object for the current session

        :return: Instance of DataDomain
        """
        current_user_email = flask_login.current_user.email
        _log.debug("Get DD object for session '%s'", current_user_email)
        return self.dd_engines[current_user_email]

    @classmethod
    def get_dd_engine_objects(cls):
        """
        Return all available in-memory DD engine objects

        :return: Dict of user_emails:DD_objects
        """
        return cls.dd_engines

    @classmethod
    def remove_dd_engine_object_for_user(cls, user):
        """
        Remove the DD engine object for the specified user from memory

        :param user: Email address identifier for the user
        """
        cls.dd_engines.pop(user, None)

    def _set_selected_replication_contexts(self, list):
        session['REPLICATION_CTX_SELECTED_LIST'] = list

    def _get_selected_replication_contexts(self):
        return session.get('REPLICATION_CTX_SELECTED_LIST', [])

    def list(self):
        selected_asup_files = AsupView.get_selected_files_path_list()
        number_of_asup_files = len(selected_asup_files)
        _log.debug("Selected %d ASUP files for RCA: %s", number_of_asup_files, selected_asup_files)

        if not number_of_asup_files:
            # We should never get to this point without having selected at lease one ASUP file, so this means
            # the user session has expired
            return force_logout()

        if (number_of_asup_files == 1):
            asup_file_save_path_escaped = selected_asup_files[0]['filePath'].encode(
                "utf-8")  # To remove issues with path in Windows
            _log.debug(asup_file_save_path_escaped)
            dd = DataDomain()
            dd.use_asup_file(
                asup_file_save_path_escaped)  # Most of the backend is done in the class DataDomain, we create an instance
            dd.parse_asup_file_for_replication_contexts_info()

        elif (number_of_asup_files == 2):
            # Ok, the user has selected two autosupport files, we need to calculate delta difference
            data_domain = []
            data_domain.append(DataDomain())
            data_domain.append(DataDomain())

            # We need to use strptime to convert the string to a proper date
            # The format of the date that comes from the asup is like Wed Mar 6 2019 06:21:44
            # Check:https://www.journaldev.com/23365/python-string-to-datetime-strptime
            if time.strptime(selected_asup_files[0]['generatedDate'], "%a %b %d %Y %H:%M:%S") < time.strptime(
                    selected_asup_files[1]['generatedDate'], "%a %b %d %Y %H:%M:%S"):
                _log.debug("First if")
                _log.debug("{} is < than {}".format(selected_asup_files[0]['generatedDate'],
                                                    selected_asup_files[1]['generatedDate']))
                # raw_input("Press a key")
                data_domain[0].use_asup_file(selected_asup_files[1]['filePath'])
                data_domain[1].use_asup_file(selected_asup_files[0]['filePath'])
                _log.warning("The asup of the newer:{}".format(selected_asup_files[1]['filePath']))
                _log.warning("The asup of the older:{}".format(selected_asup_files[0]['filePath']))

            elif time.strptime(selected_asup_files[0]['generatedDate'], "%a %b %d %Y %H:%M:%S") > time.strptime(
                    selected_asup_files[1]['generatedDate'], "%a %b %d %Y %H:%M:%S"):

                _log.debug("Second if")
                _log.debug("{} is > than {}".format(selected_asup_files[0]['generatedDate'],
                                                    selected_asup_files[1]['generatedDate']))
                # raw_input("Press a key")
                data_domain[0].use_asup_file(selected_asup_files[0]['filePath'])
                data_domain[1].use_asup_file(selected_asup_files[1]['filePath'])
                _log.warning("The asup of the newer:{}".format(selected_asup_files[0]['filePath']))
                _log.warning("The asup of the older:{}".format(selected_asup_files[1]['filePath']))

            elif selected_asup_files[0]['generatedDate'] == selected_asup_files[1]['generatedDate']:

                # The GENERATED_DATE is the same, so this seems to be the same file, or in any case makes no sense to calculate delta differences
                _log.error("Both autosupports are the same file, it makes no sense to calculate the delta difference")
                return (
                "<br>Cannot calculate delta difference because both autosupports are the same file, <strong>try again by selecting 2 different ASUP files for the same Data Domain.</strong>",
                405, {'ContentType': 'text/html'})

            # We know populate the context information for both the data_domain objects
            data_domain[0].parse_asup_file_for_replication_contexts_info()
            data_domain[1].parse_asup_file_for_replication_contexts_info()

            # Now data_domain[0] is the newer asup and data_domain[1] is the older one
            # We check here if both asups are referred to the same serial
            if (data_domain[0].serial_number == data_domain[1].serial_number):
                _log.debug("Both asups are referred to the same serial number ")

                data_domain[0].calculate_delta_difference(data_domain[1])
                _log.info(
                    "The delta difference of the object:{}".format(data_domain[0].return_lrepl_client_time_stats_delta))
                data_domain[0].make_lrepl_client_time_stats_equal_to_delta_time_stats()

                dd = data_domain[
                    0]  # We just point the dd object to newer dd, where the lrepl_client_time_stats are the delta difference, as we called make_lrepl_client_time_stats_equal_to_delta_time_stats()

            else:
                _log.debug("The serial number of both asups do not match")
                return ("The serial number of the uploaded ASUP files do not match, we cannot calculate the delta difference of different DataDomain systems.<br/>\
                            <ul>\
                                <li>%s: %s</li>\
                                <li>%s: %s</li>\
                                </ul>" % (
                    os.path.basename(selected_asup_files[0]['filePath']), data_domain[0].serial_number, os.path.basename(selected_asup_files[1]['filePath']),
                    data_domain[1].serial_number), 405, {'ContentType': 'text/html'})

        _log.debug("START of the method to display the contexts of the autosuport that has being uploaded")
        repl_ctx_list = []
        _log.debug("Replication Contexts frontend {}".format(dd.replication_contexts_frontend))

        for item in dd.replication_contexts_frontend:  # In dd.replication_contexts_frontend, we have just the contexts displayed in the frontend, but we want to filter from them just to display source and valid replication contexts
            _log.debug("Searching for just source replication contexts")
            if (dd.is_source_context(item['ctx'])):
                _log.debug("The context{}, is a source replication context".format(item))
                _log.debug(
                    "Adding the context number:{} to the list of source and valid replication contexts".format(item))
                repl_ctx_list.append(item)

        _log.debug("Found %d source and valid replication contexts", len(repl_ctx_list))
        _log.debug("List to jsonify {}".format(repl_ctx_list))
        _log.debug("END of the method to display the contexts of the autosuport that has being uploaded")

        # Save the Data Domain object for the current session
        self._save_dd_engine_for_session(dd)

        return (jsonify(repl_ctx_list),
                200,
                {'ContentType': 'application/json'})

    @route('select/', methods=['POST'])
    def select(self):
        selected_replication_contexts = json.loads(request.data)
        self._set_selected_replication_contexts(selected_replication_contexts)

        _log.info("Selected replication contexts for session '%s' analysis: %s",
                  flask_login.current_user.email, selected_replication_contexts)

        return (jsonify({}),
                200,
                {'ContentType': 'application/json'})

    def analyze(self):
        try:
            selected_replication_contexts = self._get_selected_replication_contexts()
            dd = self._get_dd_engine_for_session()
        except KeyError:
            return force_logout()

        # Call get_replication_analysis to analyze selected replication contexts
        _log.debug("Selected contexts for analysis: {}".format(selected_replication_contexts))

        temporal_data_structure = dd.get_replication_analysis(selected_replication_contexts, app)

        if (temporal_data_structure == -1):  # This happens if the difference for one context between 2 dates is negative
            telemetry.track_analysis(flask_login.current_user.email, {
                'ddos_version': dd.ddos_version,
                'serialno': dd.serial_number,
                'replctx': '1',
                'verdict': VerdictEnum.VERDICT_ERROR,
                'suggested_fix': 'NEGATIVE DELTA DIFFERENCE'
            })

            return (
            "<strong>NEGATIVE DELTA DIFFERENCE</strong><br><br>This could happen when the difference in the metrics for one context between two dates is negative.<br><br>If the DDFS has been restarted between the two selected dates, this error is normal because 'Lrepl Client Time Stats' is a cumulative metric that start from 0 whenever the FS is restarted.<br><br>In that case use the 'Single Autosupport Upload' to obtain metrics.<br>Otherwise report a problem sending an e-mail: gonzalo.murillotello@dell.com.",
            405, {'ContentType': 'text/html'})

        else:

            final_data_structure = temporal_data_structure

            # Track telemetry data for each repl ctx in the result
            for analysis_result in final_data_structure:
                for suggested_fix in analysis_result['suggestedFix']:
                    # If there is at least one step in the action items, it means a problem was detected, otherwise everything is OK
                    # TODO: Maybe return a boolean that says if there is a problem?
                    if suggested_fix['action_item']['list_of_steps']:
                        verdict = VerdictEnum.VERDICT_LAG
                    else:
                        verdict = VerdictEnum.VERDICT_OK

                    telemetry.track_analysis(flask_login.current_user.email, {
                        'ddos_version': dd.ddos_version,
                        'serialno': dd.serial_number,
                        'replctx': str(analysis_result['ctxDetails']['ctx']),
                        'verdict': verdict,
                        'suggested_fix': suggested_fix['action_item']['one_liner']
                    })

            return (jsonify(final_data_structure),
                    200,
                    {'ContentType': 'application/json'})

AsupView.register(app)
ReplCtxView.register(app)


def force_logout():
    """
    Attempting to access persistent objects after a session as (auto-)expired will cause an exception,
    to handle this we force logout the current user to start over

    This cannot be in session_mgmt_apis.py because it imports the current module and will cause a circular dependency

    :return: HTTP response
    """
    _log.info("Forcing logout for expired session '%s'", flask_login.current_user.email)
    _log.debug("User had session args: %s", session)
    logout_user()

    return ("", 401, {})
