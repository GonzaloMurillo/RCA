#!/usr/bin/env python
# coding=utf-8

# Versioning is to be kept simple by using the following convention:
# [major].[minor].[patch] [alpha|beta]
#
# Include the optional "alpha" or "beta" string in __version__ itself.
# eg. "1.0.0" or "1.0.2 beta" or "1.1.0"
#
# Update the release date on the day of check-in when the version is updated.
#
# This string is used as-is on the CLI help display and the 'about' page in the HTML frontend
__version__ = "1.0.0 beta"
__release_date__ = "19-Dec-2018"
__pretty_version__ = 'ctxdoing v' + __version__ + ' released on ' + __release_date__
