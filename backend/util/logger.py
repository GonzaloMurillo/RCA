#!/usr/bin/env python
# coding=utf-8

'''Logging module
Provides APIs that are wrappers over the Python 'logging' module
'''

import logging, os, sys, traceback
from logging.config import fileConfig

current_log_file_path = None

def init_logger(log_file_path):
    '''
    Initialize the logger using a hard-coded dict

    :param log_file_path: Absolute path to the log file (should be a directory)
    '''
    global current_log_file_path
    try:
        log_file_name = 'ctxdoing.log'
        current_log_file_path = os.path.abspath(os.path.join(log_file_path, log_file_name))

        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'file': {
                    'format': '%(asctime)s %(threadName)s %(name)-12s %(levelname)-8s | %(message)s',
                },
                'console': {
                    'format': '%(levelname)-8s %(message)s'
                }
            },
            'handlers': {
                'file': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'file',
                    'filename': current_log_file_path,
                    'mode': 'a',
                    'maxBytes': 15728640, # 15MB max file size
                    'backupCount': 1,     # Keep only a single log file
                },
                'console': {
                    'level': 'INFO',                    # Change this to 'debug' to see all logs on the console while running this app/script
                    'class': 'logging.StreamHandler',
                    'formatter': 'console'
                },
            },

            'loggers': {
                # Add custom logger on a per-package basis here, if required
            },
            'root': {
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            },
        }

        logging.config.dictConfig(LOGGING)
    except:
        traceback.print_exc()
        # If we don't have logging, then it will be impossible to debug any issues with the app
        # We don't want to end up in that situation, so abort now
        sys.stderr.write('Failed to initialize logger, aborting execution.\n')
        sys.stderr.write("Ensure that the current user has write permissions in this directory: {}\n".format(os.path.abspath(log_file_path)))
        sys.exit(1)

def get_logger(module_name):
    '''
    Get an instance of a module-level logger

    :param module_name: Name of the calling module (use __name__)
    '''
    try:
        return logging.getLogger(module_name)
    except:
        raise Exception("Failed to get the logger module name")
