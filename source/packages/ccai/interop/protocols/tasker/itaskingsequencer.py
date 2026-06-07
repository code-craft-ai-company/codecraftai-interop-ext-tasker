"""
    .. module:: itaskingsequencer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: itaskingsequencer module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import Protocol

from ccai.errors.exceptions import AbstractMethodError


from ccai.testbase.results.recorders.resultrecorder import ResultRecorder
from ccai.testbase.results.model.taskinggroup import TaskingGroup
from ccai.testbase.results.model.taskingresult import TaskingResult


class ITaskingSequencer(Protocol):
    """
        Protocol defining the interface for task sequencing helpers.
    """

    def create_tasking_result(
        self, scope_id: str, name: str, parent_inst: str
    ) -> TaskingResult:
        """
            Creates a :class:`TaskingResult` object used to capture the outcome of a task.
            
            :param scope_id: The scope identifier for the result.
            :param name: The name of the tasking instance.
            :param parent_inst: The parent instance identifier.
            
            :returns: A :class:`TaskingResult` instance.
        """
        raise AbstractMethodError(
            "ITaskingSequencer.create_tasking_result must be overloaded by derived types"
        )

    def create_tasking_group(
        self, scope_id: str, name: str, parent_inst: str
    ) -> TaskingGroup:
        """
            Creates a :class:`TaskingGroup` for grouping related tasking results.
            
            :param scope_id: The scope identifier for the group.
            :param name: The name of the tasking group.
            :param parent_inst: The parent instance identifier.
            
            :returns: A :class:`TaskingGroup` instance.
        """
        raise AbstractMethodError(
            "ITaskingSequencer.create_tasking_group must be overloaded by derived types"
        )

    def get_recorder(self) -> ResultRecorder:
        """
            Retrieves the :class:`ResultRecorder` used for recording results.
            
            :returns: The active :class:`ResultRecorder` instance.
        """
        raise AbstractMethodError(
            "ITaskingSequencer.get_recorder must be overloaded by derived types"
        )

    def get_top_scope_id(self) -> str:
        """
            Gets the identifier of the current top-level scope.
            
            :returns: The active scope identifier.
        """
        raise AbstractMethodError(
            "ITaskingSequencer.get_top_scope_id must be overloaded by derived types"
        )
