"""
    .. module:: commandsext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the commandsext functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import List, Optional, TYPE_CHECKING

import os
import posixpath
import shlex
import weakref

from ccai.errors.exceptions import CommandError, SemanticError

from ccai.interop.interfaces.isystemcontext import ISystemContext
from ccai.xmodules.xformatting import format_command_result

if TYPE_CHECKING:
    from ccai.landscaping.clients.taskers.linux.linuxtaskerclient import LinuxTaskerClient


REDACTED_PASSWORD = "***"


def check_cifs_credentials(username: Optional[str] = None, password: Optional[str] = None,
                           domain: Optional[str] = None):
    """
        Checks that a set of CIFS credentials can be passed to ``mount.cifs``.

        ``mount.cifs`` splits its ``-o`` option on commas and has no escape for a comma in an option value on
        the command line.  Windows account and domain names cannot contain a comma, so a comma in the user
        name or the domain is rejected.  A password may contain commas; :func:`create_cifs_mount_command`
        passes such a password in the ``PASSWD`` environment variable instead.

        :param username: Optional user name for the share.
        :param password: Optional password for the share.
        :param domain: Optional domain for the share.

        :raises: SemanticError when the credentials are incomplete or cannot be passed to ``mount.cifs``.
    """

    if username is not None and password is None:
        errmsg = "If you provide a username then you must provide a password."
        raise SemanticError(errmsg)

    if domain is not None and username is None:
        errmsg = "If you provide a domain you must provide a username and password."
        raise SemanticError(errmsg)

    for option_name, option_value in [("username", username), ("domain", domain)]:
        if option_value is not None and "," in option_value:
            errmsg_lines = [
                f"The CIFS '{option_name}' cannot contain a comma: {option_name}={option_value}",
                "mount.cifs separates its options with commas and cannot parse a comma inside an option",
                "value, and Windows account and domain names cannot contain one.",
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise SemanticError(errmsg)

    return


def create_cifs_mount_command(share: str, mpoint: str, username: Optional[str] = None,
                              password: Optional[str] = None, domain: Optional[str] = None,
                              redact_password: bool = False) -> str:
    """
        Creates the shell command that mounts a CIFS share.

        The credentials are passed as one comma separated ``-o`` option, ``username=<user>,password=<pass>,
        domain=<domain>``.  ``mount.cifs`` takes everything after the first '=' as the value and does not
        process quotes, so the values are not quoted inside the option; every argument of the command is
        quoted for the remote shell instead.  ``mount.cifs`` documents that a password containing a comma
        cannot be parsed from the command line but is read correctly from the ``PASSWD`` environment variable,
        which it uses when no password option is given, so such a password is passed with
        ``env PASSWD=<pass> mount ...``.

        :param share: UNC share to mount.
        :param mpoint: Remote mount point.
        :param username: Optional user name for the share.
        :param password: Optional password for the share.
        :param domain: Optional domain for the share.
        :param redact_password: Build the command with the password replaced by ``***``, for reporting.

        :returns: The mount command.
        :raises: SemanticError when the credentials cannot be passed to ``mount.cifs``.
    """

    check_cifs_credentials(username=username, password=password, domain=domain)

    command_password = password
    if password is not None and redact_password:
        command_password = REDACTED_PASSWORD

    parts: List[str] = []
    options_list: List[str] = []

    if username is not None:
        options_list.append(f"username={username}")

    if password is not None:
        if "," in password:
            parts.append("env")
            parts.append(f"PASSWD={command_password}")
        else:
            options_list.append(f"password={command_password}")

    if domain is not None:
        options_list.append(f"domain={domain}")

    parts.extend(["mount", "-t", "cifs"])
    if len(options_list) > 0:
        parts.append("-o")
        parts.append(",".join(options_list))
    parts.append(share)
    parts.append(mpoint)

    quoted_parts = [shlex.quote(part) for part in parts]
    mnt_cmd = " ".join(quoted_parts)

    return mnt_cmd


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

            :raises: SemanticError when the credentials are incomplete or cannot be passed to ``mount.cifs``
                     (see :func:`check_cifs_credentials`), CommandError when a command fails.
        """

        status, stdout, stderr = None, None, None

        sysctx = self.client.get_default_system_context()

        # Check the credentials before anything is changed on the remote client.
        check_cifs_credentials(username=username, password=password, domain=domain)

        session: ISystemContext
        with sysctx.open_session(basis_session=basis_session) as session:
            # The mount point is a path on the remote Linux client, so it follows POSIX path rules
            # whatever the platform of the controller running this code.
            mparent = posixpath.dirname(mpoint)
            if not session.directory_exists(mparent):
                errmsg = f"The parent directory '{mparent}' of the specified mount point must exist. mpoint={mpoint}"
                raise SemanticError(errmsg)

            quoted_mpoint = shlex.quote(mpoint)
            mount_cmd = f"mkdir -p {quoted_mpoint}"
            status, stdout, stderr = session.run_cmd(mount_cmd)
            if status != 0:
                errmsg = f"Error attempting to create mount point mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mount_cmd, status, stdout, stderr, exp_status=0)
                raise CommandError(errmsg, status, stdout, stderr)

            mnt_cmd = create_cifs_mount_command(share, mpoint, username=username, password=password, domain=domain)
            status, stdout, stderr = session.run_cmd(mnt_cmd)
            if status != 0:
                ipaddr = self.client.ipaddr
                errmsg = f"Error attempting to mount cifs share={share} on mpoint={mpoint}."

                # Report the command with the password redacted so it does not reach the exception text or logs.
                reported_cmd = create_cifs_mount_command(share, mpoint, username=username, password=password,
                                                         domain=domain, redact_password=True)

                errmsg = format_command_result(errmsg, reported_cmd, status, stdout, stderr, exp_status=0, target=ipaddr)
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

            # The mount point is a path on the remote Linux client, so it follows POSIX path rules
            # whatever the platform of the controller running this code.
            mparent = posixpath.dirname(mpoint)
            if not session.directory_exists(mparent):
                errmsg = f"The parent directory '{mparent}' of the specified mount point must exist. mpoint={mpoint}"
                raise SemanticError(errmsg)

            quoted_mpoint = shlex.quote(mpoint)
            mkdir_cmd = f"mkdir -p {quoted_mpoint}"
            status, stdout, stderr = session.run_cmd(mkdir_cmd)
            if status != 0:
                errmsg = f"Error attempting to create mount point mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mkdir_cmd, status, stdout, stderr, exp_status=0)
                raise CommandError(errmsg, status, stdout, stderr)

            source = f"{host}:{export}"
            quoted_source = shlex.quote(source)
            mnt_cmd = f"mount -t nfs {quoted_source} {quoted_mpoint}"
            status, stdout, stderr = session.run_cmd(mnt_cmd)
            if status != 0:
                ipaddr = self.client.ipaddr
                errmsg = f"Error attempting to mount nfs export={export} on mpoint={mpoint}."
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
            quoted_msg = shlex.quote(msg)
            command = f"sudo logger {quoted_msg}"
            status, stdout, stderr = session.run_cmd(command)
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

            parts = ["umount"]
            if flags is not None and len(flags) > 0:
                flag_parts = shlex.split(flags)
                parts.extend(flag_parts)
            parts.append(mpoint)

            quoted_parts = [shlex.quote(part) for part in parts]
            mnt_cmd = " ".join(quoted_parts)
            status, stdout, stderr = session.run_cmd(mnt_cmd)
            if status != 0:
                errmsg = f"Error attempting to unmount mpoint={mpoint}."
                errmsg = format_command_result(errmsg, mnt_cmd, status, stdout, stderr, exp_status=0)
                raise CommandError(errmsg, status, stdout, stderr)

        return
