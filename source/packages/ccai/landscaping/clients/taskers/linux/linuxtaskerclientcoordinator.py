"""
    .. module:: linuxclientcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the LinuxPoolCoordinator which is used for managing connectivity with pools of LINUX capable devices

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional, TYPE_CHECKING

from ccai.credentials.basecredential import BaseCredential
from ccai.landscaping.clients.clientcoordinatorbase import ClientCoordinatorBase

from ccai.interop.protocols.ssh.sshagent import SshAgent
from ccai.landscaping.coordinators.integrationclasses import INTEGRATION_CLASS_NETWORK_SSH

from ccai.landscaping.clients.taskers.constants import INTEGRATION_CLASS_FOR_LINUX_TASKER_CLIENT
from ccai.landscaping.clients.taskers.linux.linuxtaskerclient import LinuxTaskerClient


if TYPE_CHECKING:
    from ccai.landscaping.landscape import Landscape

class LinuxTaskerClientCoordinator(ClientCoordinatorBase):
    """
        The :class:`LinuxPoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote Linux
        client.
    """

    INTEGRATION_CLASS = INTEGRATION_CLASS_FOR_LINUX_TASKER_CLIENT
    CLIENT_TYPE = LinuxTaskerClient

    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        """
            Creates a :class:`LinuxClientCoordinator` instance.

            :param lscape: The landscape this coordinator belongs to.
        """
        super().__init__(lscape, *args, **kwargs)
        return


    def configure_devices(self, landscape: "Landscape") -> list:
        """
            Called by configuration tools running in the "Infrastructure Orchestration" layer to configure
            a coordinator devices.
        """
        results = []

        return results


    def create_ssh_agent(self, device: LinuxTaskerClient, device_info: Dict[str, Any], host: str, cred: BaseCredential,
                         users: Optional[dict] = None, port: int = 22, pty_params: Optional[dict] = None):
        """
            Attaches an SSH agent extension to a Linux client.

            :param device: The device instance to attach to.
            :param device_info: Configuration dictionary for the device.
            :param host: Host name of the target device.
            :param cred: SSH credential to use for the connection.
            :param users: Optional user mapping information.
            :param port: SSH port number.
            :param pty_params: Optional pseudo terminal parameters.
        """

        ssh_agent = SshAgent(host, cred, users=users, port=port, pty_params=pty_params)

        device.attach_extension(INTEGRATION_CLASS_NETWORK_SSH, ssh_agent)
        return