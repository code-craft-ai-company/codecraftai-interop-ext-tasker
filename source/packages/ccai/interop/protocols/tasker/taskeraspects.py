"""
    .. module:: taskeraspects
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerAspects` class which is used to instruct behavior
    around tasking.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
    
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Dict, Optional


DEFAULT_COMPLETION_TIMEOUT = 7 * 24 * 60 * 60  # The Default Timeout is 1 Week
DEFAULT_COMPLETION_INTERVAL = 10

DEFAULT_INACTIVITY_TIMEOUT = 1200  # 20 Minutes
DEFAULT_INACTIVITY_INTERVAL = 0.5

DEFAULT_PROGRESS_INTERVAL = 30

from ccai.aspects.aspects import Aspects as AspectsBase
from ccai.testbase.results.model.progressdelivery import ProgressDeliveryMethod


class TaskerAspects(AspectsBase):
    """
        Parameterization object describing task execution behavior.
    """

    def __init__(
        self,
        completion_timeout: Optional[float] = DEFAULT_COMPLETION_TIMEOUT,
        completion_interval: Optional[float] = DEFAULT_COMPLETION_INTERVAL,
        inactivity_timeout: Optional[float] = DEFAULT_INACTIVITY_TIMEOUT,
        inactivity_interval: Optional[float] = DEFAULT_INACTIVITY_INTERVAL,
        progress_delivery: Optional[Dict[str, float]] = None,
        sync_request_timeout: Optional[float] = None,
    ):
        """
            Constructs a :class:`TaskerAspects` object describing task execution parameters.
            
            :param completion_timeout: Maximum wait time for a task to complete.
            :param completion_interval: Polling interval while waiting for completion.
            :param inactivity_timeout: Timeout for detecting inactivity.
            :param inactivity_interval: Polling interval for inactivity checks.
            :param progress_delivery: Progress delivery settings.
            :param sync_request_timeout: Timeout for synchronous requests.
        """

        super().__init__(completion_interval=completion_interval, completion_timeout=completion_timeout)

        self.inactivity_timeout = inactivity_timeout
        self.inactivity_interval = inactivity_interval
        self.progress_delivery = progress_delivery
        self.sync_request_timeout = sync_request_timeout
        return

    def as_dict(self) -> dict:
        """
            Returns this instance as a dictionary.
            
            :returns: Dictionary representation of the aspects.
        """
        data = {
            "completion_timeout": self.completion_timeout,
            "completion_interval": self.completion_interval,
            "inactivity_timeout": self.inactivity_timeout,
            "inactivity_interval": self.inactivity_interval,
            "progress_delivery": self.progress_delivery,
            "sync_request_timeout": self.sync_request_timeout,
        }
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "TaskerAspects":
        """
            Creates a :class:`TaskerAspects` from a dictionary.
            
            :param data: Dictionary of aspect values.
            
            :returns: A new :class:`TaskerAspects` instance.
        """

        obj = TaskerAspects(**data)
        return obj


DEFAULT_TASKER_ASPECTS = TaskerAspects()

DEFAULT_SUMMARY_PROGRESS_TASKER_ASPECTS = TaskerAspects(
    progress_delivery={
        ProgressDeliveryMethod.SUMMARY_PULL_PROGRESS: DEFAULT_PROGRESS_INTERVAL
    }
)
