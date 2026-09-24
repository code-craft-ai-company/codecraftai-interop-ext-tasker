"""
    Regression tests for the tasker copy of :class:`CommandsExt`.  They cover the result unpacking (``run_cmd``
    returns ``(status, stdout, stderr)``; the methods used to unpack it as ``status, stderr, stdout``, which
    swapped the two streams in the raised :class:`CommandError` and its message) and the fixes ported from the
    landscaping copy: the CIFS credentials are passed in the mount command, the arguments are quoted for the
    remote shell, the remote mount point follows POSIX path rules and the NFS error message is spelled right.
    The CIFS credentials are passed the way ``mount.cifs`` parses them: unquoted values in one comma separated
    ``-o`` option, a password containing a comma in the ``PASSWD`` environment variable, and a comma in the user
    name or domain rejected.  The client, system context and session are small fakes that script the
    ``run_cmd`` results.
"""

from typing import List, Optional, Tuple

import ntpath
import os
import shlex

import ccai.testbase as testbase

from ccai.errors.exceptions import CommandError, SemanticError
from ccai.landscaping.clients.taskers.linux.ext.commandsext import CommandsExt


FAILED_STDOUT = "MY_STDOUT"
FAILED_STDERR = "MY_STDERR"


class FakeSession:
    """
        A session whose ``run_cmd`` returns scripted ``(status, stdout, stderr)`` results in order and records
        the commands it was given.
    """

    def __init__(self, results: List[Tuple[int, str, str]]):
        self.results = list(results)
        self.commands: List[str] = []
        self.checked_directories: List[str] = []
        return

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False

    def directory_exists(self, path: str) -> bool:
        self.checked_directories.append(path)
        return True

    def run_cmd(self, command: str) -> Tuple[int, str, str]:
        self.commands.append(command)
        rtnval = self.results.pop(0)
        return rtnval


class FakeSystemContext:
    """
        A system context that opens the one fake session.
    """

    def __init__(self, session: FakeSession):
        self._session = session
        return

    def open_session(self, basis_session: Optional[object] = None) -> FakeSession:
        return self._session


class FakeClient:
    """
        A client exposing the members :class:`CommandsExt` uses.
    """

    def __init__(self, session: FakeSession):
        self.ipaddr = "1.2.3.4"
        self._sysctx = FakeSystemContext(session)
        return

    def get_default_system_context(self) -> FakeSystemContext:
        return self._sysctx


def _assert_streams_in_order(raised: Optional[CommandError]):
    """
        Checks that the raised error carries stdout and stderr in their own fields and message sections.

        :param raised: The error raised by the method under test.
    """
    testbase.assert_true(raised is not None, "CommandError raised for the failing command")
    testbase.assert_equal(raised.status, 1)
    testbase.assert_equal(raised.stdout, FAILED_STDOUT)
    testbase.assert_equal(raised.stderr, FAILED_STDERR)

    message = str(raised)
    stdout_section = message.index("STDOUT:")
    stdout_text = message.index(FAILED_STDOUT)
    stderr_section = message.index("STDERR:")
    stderr_text = message.index(FAILED_STDERR)
    testbase.assert_true(stdout_section < stdout_text < stderr_section, "stdout text reported under the STDOUT section")
    testbase.assert_true(stderr_section < stderr_text, "stderr text reported under the STDERR section")
    return


def test_cifs_mount_reports_stdout_and_stderr_in_order():
    """
        A failing CIFS mount command reports its stdout and stderr in the right fields.
    """
    session = FakeSession([(0, "", ""), (1, FAILED_STDOUT, FAILED_STDERR)])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    raised = None
    try:
        cmd_ext.cifs_mount("//server/share", "/mnt/point")
    except CommandError as xcpt:
        raised = xcpt

    testbase.assert_equal(len(session.commands), 2)
    _assert_streams_in_order(raised)

    return


def test_nfs_mount_reports_stdout_and_stderr_in_order():
    """
        A failing mount point creation for an NFS mount reports its stdout and stderr in the right fields.
    """
    session = FakeSession([(1, FAILED_STDOUT, FAILED_STDERR)])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    raised = None
    try:
        cmd_ext.nfs_mount("nfshost", "/export", "/mnt/point")
    except CommandError as xcpt:
        raised = xcpt

    _assert_streams_in_order(raised)

    return


def test_system_logger_reports_stdout_and_stderr_in_order():
    """
        A failing logger command reports its stdout and stderr in the right fields.
    """
    session = FakeSession([(1, FAILED_STDOUT, FAILED_STDERR)])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    raised = None
    try:
        cmd_ext.system_logger("hello")
    except CommandError as xcpt:
        raised = xcpt

    _assert_streams_in_order(raised)

    return


def test_umount_reports_stdout_and_stderr_in_order():
    """
        A failing unmount command reports its stdout and stderr in the right fields.
    """
    session = FakeSession([(1, FAILED_STDOUT, FAILED_STDERR)])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    raised = None
    try:
        cmd_ext.umount("/mnt/point")
    except CommandError as xcpt:
        raised = xcpt

    _assert_streams_in_order(raised)

    return


def test_cifs_mount_passes_the_credentials_as_one_mount_option():
    """
        The CIFS user name, password and domain reach the mount command as a single comma separated ``-o``
        option (they used to be built into an options string that was never used).  The values are not
        wrapped in double quotes: the argument is already shell-quoted and mount.cifs does not strip quotes,
        so they would become part of the credentials.
    """
    session = FakeSession([(0, "", ""), (0, "", "")])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    cmd_ext.cifs_mount("//server/share", "/mnt/point", username="myuser", password="mypass", domain="mydomain")

    testbase.assert_equal(len(session.commands), 2)
    mount_argv = shlex.split(session.commands[1])
    expected_argv = [
        "mount", "-t", "cifs", "-o", "username=myuser,password=mypass,domain=mydomain",
        "//server/share", "/mnt/point"
    ]
    testbase.assert_equal(mount_argv, expected_argv)
    return


def test_cifs_mount_without_credentials_has_no_mount_option():
    """
        A CIFS mount without credentials does not pass an empty ``-o`` option.
    """
    session = FakeSession([(0, "", ""), (0, "", "")])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    cmd_ext.cifs_mount("//server/share", "/mnt/point")

    mount_argv = shlex.split(session.commands[1])
    testbase.assert_equal(mount_argv, ["mount", "-t", "cifs", "//server/share", "/mnt/point"])
    return


def test_cifs_mount_passes_credential_characters_literally():
    """
        Spaces, quotes, backslashes and shell metacharacters in the credentials reach mount.cifs unchanged
        inside the single mount option argument.
    """
    session = FakeSession([(0, "", ""), (0, "", "")])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    cmd_ext.cifs_mount("//server/share", "/mnt/point", username="my user", password='pa"ss\\$(id)=x\'y')

    mount_argv = shlex.split(session.commands[1])
    testbase.assert_equal(mount_argv[:4], ["mount", "-t", "cifs", "-o"])
    testbase.assert_equal(mount_argv[4], 'username=my user,password=pa"ss\\$(id)=x\'y')
    testbase.assert_equal(mount_argv[5:], ["//server/share", "/mnt/point"])
    return


def test_cifs_mount_passes_a_password_with_a_comma_in_the_environment():
    """
        mount.cifs cannot parse a password containing a comma from its options, and reads it from the PASSWD
        environment variable instead, so such a password is passed with ``env PASSWD=...`` and left out of
        the ``-o`` option.
    """
    session = FakeSession([(0, "", ""), (0, "", "")])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    cmd_ext.cifs_mount("//server/share", "/mnt/point", username="myuser", password="pa,ss", domain="mydomain")

    mount_argv = shlex.split(session.commands[1])
    expected_argv = [
        "env", "PASSWD=pa,ss", "mount", "-t", "cifs", "-o", "username=myuser,domain=mydomain",
        "//server/share", "/mnt/point"
    ]
    testbase.assert_equal(mount_argv, expected_argv)
    return


def test_cifs_mount_rejects_a_comma_in_the_username_or_domain():
    """
        A comma in the user name or the domain cannot be passed to mount.cifs, so it raises a SemanticError
        naming the option before any command runs on the client.
    """
    for username, domain, option_name in [("my,user", None, "username"), ("myuser", "my,domain", "domain")]:
        session = FakeSession([])
        client = FakeClient(session)
        cmd_ext = CommandsExt(client)

        raised = None
        try:
            cmd_ext.cifs_mount("//server/share", "/mnt/point", username=username, password="pass", domain=domain)
        except SemanticError as xcpt:
            raised = xcpt

        testbase.assert_true(raised is not None, f"SemanticError raised for a comma in the {option_name}")
        testbase.assert_true(f"'{option_name}' cannot contain a comma" in str(raised), "the error names the option")
        testbase.assert_equal(session.commands, [])

    return


def test_cifs_mount_failure_redacts_the_password():
    """
        The command reported in the error of a failing CIFS mount shows the credentials option with the
        password redacted.
    """
    session = FakeSession([(0, "", ""), (1, FAILED_STDOUT, FAILED_STDERR)])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    raised = None
    try:
        cmd_ext.cifs_mount("//server/share", "/mnt/point", username="myuser", password="s3cret-value")
    except CommandError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "CommandError raised for the failing mount")
    message = str(raised)
    testbase.assert_true("username=myuser,password=***" in message, "the reported command shows the redacted password")
    testbase.assert_equal("s3cret-value" in message, False)
    return


def test_cifs_mount_failure_redacts_a_password_passed_in_the_environment():
    """
        The command reported for a failing CIFS mount whose password is passed in PASSWD shows the redacted
        password in the same form.
    """
    session = FakeSession([(0, "", ""), (1, FAILED_STDOUT, FAILED_STDERR)])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    raised = None
    try:
        cmd_ext.cifs_mount("//server/share", "/mnt/point", username="myuser", password="s3cret,value")
    except CommandError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "CommandError raised for the failing mount")
    message = str(raised)
    testbase.assert_true("env 'PASSWD=***' mount -t cifs -o username=myuser" in message,
                         "the reported command shows the redacted PASSWD")
    testbase.assert_equal("s3cret" in message, False)
    return


def test_cifs_mount_quotes_the_mount_point():
    """
        A mount point with a space is passed to ``mkdir`` and ``mount`` as one argument.
    """
    session = FakeSession([(0, "", ""), (0, "", "")])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    cmd_ext.cifs_mount("//server/share", "/mnt/my share")

    testbase.assert_equal(shlex.split(session.commands[0]), ["mkdir", "-p", "/mnt/my share"])
    testbase.assert_equal(shlex.split(session.commands[1])[-1], "/mnt/my share")
    return


def test_cifs_mount_checks_the_remote_parent_directory_with_posix_rules():
    """
        The parent of the remote mount point is found with POSIX path rules even when the controller's
        ``os.path`` follows Windows rules, where a backslash is also a separator.
    """
    session = FakeSession([(0, "", ""), (0, "", "")])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    local_path_module = os.path
    os.path = ntpath
    try:
        cmd_ext.cifs_mount("//server/share", "/mnt/back\\slash")
    finally:
        os.path = local_path_module

    testbase.assert_equal(session.checked_directories, ["/mnt"])
    return


def test_nfs_mount_quotes_its_arguments():
    """
        The NFS source and the mount point are each passed as one quoted argument.
    """
    session = FakeSession([(0, "", ""), (0, "", "")])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    cmd_ext.nfs_mount("nfshost", "/export/my data", "/mnt/my point")

    testbase.assert_equal(shlex.split(session.commands[0]), ["mkdir", "-p", "/mnt/my point"])
    testbase.assert_equal(shlex.split(session.commands[1]), ["mount", "-t", "nfs", "nfshost:/export/my data", "/mnt/my point"])
    return


def test_nfs_mount_failure_message_names_the_nfs_mount():
    """
        The error for a failing NFS mount names an "nfs" export (it used to read "nfsmoun").
    """
    session = FakeSession([(0, "", ""), (1, FAILED_STDOUT, FAILED_STDERR)])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    raised = None
    try:
        cmd_ext.nfs_mount("nfshost", "/export", "/mnt/point")
    except CommandError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "CommandError raised for the failing mount")
    message = str(raised)
    testbase.assert_true("Error attempting to mount nfs export=/export on mpoint=/mnt/point." in message,
                         "the error names the nfs export")
    testbase.assert_equal("nfsmoun " in message, False)
    return


def test_system_logger_passes_the_message_as_one_argument():
    """
        A message with quotes and shell metacharacters reaches ``logger`` as one literal argument.
    """
    session = FakeSession([(0, "", "")])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    message = 'say "hi" $(reboot) `id`; exit'
    cmd_ext.system_logger(message)

    testbase.assert_equal(shlex.split(session.commands[0]), ["sudo", "logger", message])
    return


def test_umount_quotes_the_mount_point_and_splits_the_flags():
    """
        The unmount flags are passed as separate arguments and the mount point as one quoted argument.
    """
    session = FakeSession([(0, "", ""), (0, "", "")])
    client = FakeClient(session)
    cmd_ext = CommandsExt(client)

    cmd_ext.umount("/mnt/my point", flags="-f -l")
    cmd_ext.umount("/mnt/point")

    testbase.assert_equal(session.commands[0], "umount -f -l '/mnt/my point'")
    testbase.assert_equal(session.commands[1], "umount /mnt/point")
    return
