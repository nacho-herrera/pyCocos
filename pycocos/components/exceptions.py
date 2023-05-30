# -*- coding: utf-8 -*-
"""
    pyCocos.exceptions
    Defines API exceptions
"""


class ApiException(Exception):
    """
    Represent a controlled exception raised by the library.
    """

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg
