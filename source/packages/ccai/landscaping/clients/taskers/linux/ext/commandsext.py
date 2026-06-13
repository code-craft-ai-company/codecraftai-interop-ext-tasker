"""
    .. module:: commandsext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the commandsext functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Optional, TYPE_CHECKING

import os
import weakref

from ccai.errors.exceptions import CommandError, SemanticError

from ccai.interop.interfaces.isystemcontext import ISystemContext
from ccai.xmodules.xformatting import format_command_result

from ccai.interop.protocols.ssh.sshagent import SshSession

if TYPE_CHECKING:
    from ccai.landscaping.clients.taskers.linux.linuxtaskerclient import LinuxTaskerClient

class CommandsExt:
    """
        Provides command execution helpers for a Linux client.
    """

    def __init__(self, client: "LinuxTaskerClient"):
        """
            Creates a :class:`CommandsExt` instance bound to a client.

            :param client: The :class:`LinuxTaskerClient` this extension operates on.
        """
        self._client_ref = weakref.ref(client)
        return

    @property
    def client(self) -> "LinuxTaskerClient":
        """
            Returns the owning :class:`LinuxTaskerClient` instance.
        """
        return self._client_ref()

    def cifs_mount(self, share: str, mpoint: str, username: Optional[str]=None,
                   password: Optional[str]=None, domain: Optional[str]=None,
                   basis_session: Optional[ISystemContext]=None):
        """
            Mounts a CIFS share on the remote client.

            :param share: UNC share to mount.
            :param mpoint: Remote mount point.
            :param username: Optional user name for the share.
            :param password: Optional password for the share.
            :param domain: Optional domain for the share.
            :param basis_session: Optional session to base operations on.
        """

        status, stdout, stderr = None, None, None

        sysctx = self.client.get_default_system_context()

        session: ISystemContext
        with sysctx.open_session(basis_session=basis_session) as session:
            mparent = os.path.dirname(mpoint)
            if not session.directory_exists(mparent):
                errmsg = f"The parent directory '{mparent}' of the specified mount point must exist. mpoint={mpoint}"
                raise SemanticError(errmsg)

            mount_cmd = f"mkdir -p {mpoint}"
            status, stderr, stdout = session.run_cmd(mount_cmd)
            if status != 0:
                errmsg = f"Error attempting to create mount point mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mount_cmd, status, stdout, stderr, exp_status=0)
                raise CommandError(errmsg, status, stdout, stderr)

            if username is not None and password is None:
                errmsg = "If you provide a username then you must provide a password."
                raise SemanticError(errmsg)
            
            if domain is not None and username is None:
                errmsg = "If you provide a domain you must provide a username and password."
                raise SemanticError(errmsg)
    
            options = ""
            if username is not None:
                options += f"-o username=\"{username}\" "

            if password is not None:
                options += f"password=\"{password}\" "

            if domain is not None:
                options += f"domain={domain}"

            mnt_cmd = f"mount -t cifs \"{share}\" \"{mpoint}\""
            status, stderr, stdout = session.run_cmd(mnt_cmd)
            if status != 0:
                ipaddr = self.client.ipaddr
                errmsg = f"Error attempting to mount cifs share={share} on mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mnt_cmd, status, stdout, stderr, exp_status=0, target=ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

        return
    
    def nfs_mount(self, host:str, export: str, mpoint: str, basis_session: Optional[ISystemContext]=None):
        """
            Mounts an NFS export on the remote client.

            :param host: Host providing the export.
            :param export: Path to the export on the host.
            :param mpoint: Mount point on the remote machine.
            :param basis_session: Optional session to base operations on.
        """
        status, stdout, stderr = None, None, None

        sysctx = self.client.get_default_system_context()

        session: ISystemContext
        with sysctx.open_session(basis_session=basis_session) as session:

            mparent = os.path.dirname(mpoint)
            if not session.directory_exists(mparent):
                errmsg = f"The parent directory '{mparent}' of the specified mount point must exist. mpoint={mpoint}"
                raise SemanticError(errmsg)

            mkdir_cmd = f"mkdir -p {mpoint}"
            status, stderr, stdout = session.run_cmd(mkdir_cmd)
            if status != 0:
                errmsg = f"Error attempting to create mount point mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mkdir_cmd, status, stdout, stderr, exp_status=0)
                raise CommandError(errmsg, status, stdout, stderr)

            mnt_cmd = f"mount -t nfs {host}:\"{export}\" \"{mpoint}\""
            status, stderr, stdout = session.run_cmd(mnt_cmd)
            if status != 0:
                ipaddr = self.client.ipaddr
                errmsg = f"Error attempting to mount nfsmoun export={export} on mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mnt_cmd, status, stdout, stderr, exp_status=0, target=ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

        return

    def system_logger(self, msg: str, basis_session: Optional[ISystemContext]=None):
        """
            Writes a message to the system log on the remote host.

            :param msg: Message text to log.
            :param basis_session: Optional session to base operations on.
        """
        
        status, stdout, stderr = None, None, None

        sysctx = self.client.get_default_system_context()

        session: ISystemContext
        with sysctx.open_session(basis_session=basis_session) as session:
            command = f'sudo logger "{msg}"'
            status, stderr, stdout = session.run_cmd(command)
            if status != 0:
                ipaddr = self.client.ipaddr
                errmsg = f"Error attempting to log a message."
                errmsg = format_command_result(errmsg, command, status, stdout, stderr, exp_status=0, target=ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

        return

    def umount(self, mpoint: str, flags:str="", basis_session: Optional[ISystemContext]=None):
        """
            Unmounts a filesystem from the specified mount point.

            :param mpoint: Mount point to unmount.
            :param flags: Optional flags passed to the unmount command.
            :param basis_session: Optional session to base operations on.
        """
        status, stdout, stderr = None, None, None

        sysctx = self.client.get_default_system_context()

        session: ISystemContext
        with sysctx.open_session(basis_session=basis_session) as session:

            mnt_cmd = f"umount {flags} \"{mpoint}\""
            status, stderr, stdout = session.run_cmd(mnt_cmd)
            if status != 0:
                errmsg = f"Error attempting to unmount mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mnt_cmd, status, stdout, stderr, exp_status=0)
                raise CommandError(errmsg, status, stdout, stderr)

        return
