# -*- coding: utf-8 -*-

class JsonApiError(Exception):
    def __init__(self, error, details=None):
        self.error = error
        self.details = details
