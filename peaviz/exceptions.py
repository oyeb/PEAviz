#!/usr/bin/python3
# -*- coding: utf-8 -*-

class PEAvizTrackerAttributeError(TypeError):
    """
    Supplied attribute is not of type (``list`` or ``dict``) or the ``list``
    is of incorrect size.
    """

class PEAvizAdapterAttributeError(TypeError):
    """
    Supplied attribute is not of type ``dict``.
    """
