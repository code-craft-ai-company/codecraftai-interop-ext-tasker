"""
    .. module:: clientroles
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the clientroles functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from enum import Enum

class ClientRoles(str, Enum):
    """
        Enumerates standard client roles within a landscape.
    """

    TaskerServer = "taskerserver"
