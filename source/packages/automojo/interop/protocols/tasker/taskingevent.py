"""
    .. module:: taskingevent
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: taskingevent module.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Optional, Union


class TaskingEvent:
    """
        A :class:`TaskingEvent` object used to report events.
    """

    def __init__(self, tasking_id: str, event_name: str, payload: Optional[dict] = None):
        """
            Constructs a :class:`TaskingEvent`.

            :param tasking_id: The identifier for the tasking instance.
            :param event_name: The name of the event being reported.
            :param payload: Optional payload associated with the event.
        """
        self._tasking_id = tasking_id
        self._event_name = event_name
        self._payload = payload
        return

    @property
    def event_name(self) -> str:
        """
            Name of the event.

            :returns: The event name string.
        """
        return self._event_name

    @property
    def payload(self) -> Union[dict, None]:
        """
            Optional payload associated with the event.

            :returns: The payload dictionary or ``None``.
        """
        return self._payload

    @property
    def tasking_id(self) -> str:
        """
            Identifier of the originating tasking.

            :returns: The tasking identifier string.
        """
        return self._tasking_id

    @classmethod
    def from_dict(cls, data: dict) -> "TaskingEvent":
        """
            Creates a :class:`TaskingEvent` from a dictionary representation.

            :param data: The event dictionary.

            :returns: A new :class:`TaskingEvent` instance.
        """
        obj = cls(data["tasking-id"], data["event-name"], data["payload"])
        return obj

    def as_dict(self) -> dict:
        """
            Serializes the event as a dictionary.

            :returns: A dictionary representation of the event.
        """
        rtnval = {
            "event-name": self._event_name,
            "payload": self._payload,
            "tasking-id": self._tasking_id,
        }
        return rtnval
