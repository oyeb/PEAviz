"""
Exceptions of the PEAviz module
"""

class PEAvizTrackerAttributeError(TypeError):
    """
    Supplied attribute is not of type (``list`` or ``dict``) or the ``list``
    is of incorrect size.
    """

class PEAvizAdapterAttributeError(TypeError):
    """
    Supplied attribute is not of type ``dict``.
    """
