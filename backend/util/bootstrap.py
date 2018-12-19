#!/usr/bin/env python
# coding=utf-8

import os, sys
import traceback
  
def get_runtime_path():
    ''' If this Python module is being run in the context of a PyInstaller EXE,
    then detect it and set the current working directory accordingly
    
    :return runtime_path: Correct CWD to be used, regardless of PyInstaller
    '''
    if getattr(sys, 'frozen', False):
        runtime_path = sys._MEIPASS
    else:
        # This file is under util/boorstrap.py, so go one level up
        runtime_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
     
    return os.path.abspath(runtime_path)

def get_preamble():
    '''
    Print a string with version, system info and file paths
    '''
    import os, sys, platform, getpass, socket
    import util.version as version
    import util.logger as logger
        
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = '<unknown>'
        
    try:
        hostname = socket.gethostname()
    except:
        hostname = '<unknown>'
    
    preamble = """
ctxdoing
============================
v{} released on {}
============================
OS: {}
Python: {}
System: {} on {}/{}
Working directory: {}
Commandline: {}
============================
Log file: {}
============================
    """.format(version.__version__, version.__release_date__,
               platform.platform(),
               sys.version,
               getpass.getuser(), hostname, ip,
               get_runtime_path(),
               ' '.join(sys.argv),
               logger.current_log_file_path)
    
    return preamble

# Actual bootstrapping code, executed with this module is imported
try:
    import util.logger as logger
    logger.init_logger(get_runtime_path())
    _logger = logger.get_logger(__name__)
    # This will print on the console as well as the log file, so we know when a new execution started
    _logger.info(get_preamble())
except:
    traceback.print_exc()
    sys.stderr.write('Failed to bootstrap the application.\n')
