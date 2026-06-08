"""
    .. module:: linuxclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the LinuxClient object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import TYPE_CHECKING

from ccai.interop.interfaces.isystemcontext import ISystemContext
from ccai.landscaping.friendlyidentifier import FriendlyIdentifier
from ccai.landscaping.clients.clientbase import ClientBase

from ccai.landscaping.clients.taskers.linux.ext.commandsext import CommandsExt
from ccai.landscaping.clients.taskers.linux.ext.configureext import ConfigureExt

from ccai.interop.protocols.ssh.sshagent import SshAgent


if TYPE_CHECKING:
    from ccai.landscaping.landscape import Landscape
    from ccai.landscaping.coordinators.coordinatorbase import CoordinatorBase

class LinuxTaskerClient(ClientBase):
    """
        Client implementation for hosts running the Linux OS.
    """

    EXT_COMMANDS = CommandsExt
    EXT_CONFIGURE = ConfigureExt

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Initializes a :class:`LinuxClient` instance.

            :param lscape: The landscape this client belongs to.
            :param coordinator: Coordinator managing this client.
            :param friendly_id: Identifier associated with the client.
            :param device_type: The declared device type.
            :param device_config: Configuration dictionary for the client.
        """
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)

        self._ext_commands = self.EXT_COMMANDS(self)
        self._ext_configure = self.EXT_CONFIGURE(self)
        return

    @property
    def commands(self) -> CommandsExt:
        """
            Returns the commands extension for this client.
        """
        return self._ext_commands
    
    @property
    def configure(self) -> ConfigureExt:
        """
            Returns the configuration extension for this client.
        """
        return self._ext_configure

    @property
    def ssh(self) -> SshAgent:
        """
            Returns the SSH agent extension for this client.
        """
        sshagent = self._extensions["network/ssh"]
        return sshagent

    def get_default_system_context(self) -> ISystemContext:
        """
            Called to get an ISystemContext instance that is a default system type.
        """
        return self.ssh

