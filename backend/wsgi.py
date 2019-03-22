#!/usr/bin/env python
# coding=utf-8

import util.bootstrap
import os, sys, signal

import util.logger as logger
_log = logger.get_logger(__name__)

from rest_api_server import app
application = app

if __name__ == "__main__":
    application.run()
