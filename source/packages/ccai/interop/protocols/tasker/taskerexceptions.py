
"""
    .. module:: taskerexceptions
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: taskerexceptions module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

class TaskingGroupAssertionError(AssertionError):
    """
        Represents an AssertionError that is raised in response to the validation of a
        collection of taskings
    """
