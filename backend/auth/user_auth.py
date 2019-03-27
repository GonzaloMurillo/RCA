#!/usr/bin/env python
# coding=utf-8
from flask_login import UserMixin

from util import logger

_log = logger.get_logger(__name__)

class DellUser(UserMixin):
    '''
    Class representing an authenticated user who has logged in to this app
    '''

    # Global list of currently logged in users
    user_list = {}

    @classmethod
    def get(cls, user_id):
        '''
        Get a DellUser object by lookup using user_id

        :param user_id: Unicode string

        :return: DellUser object or None
        '''
        try:
            return DellUser.user_list[user_id]
        except KeyError:
            _log.exception("User %s is not logged in", user_id)

        # Flask-Login expects a return value of None for invalid user_ids, not an exception
        return None

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        '''
        Generate and return a unique ID for this logged in user

        :return: Unicode string
        '''
        return u'UNIQUE_ID'
