"""
    Regression tests for the result unpacking in the tasker copy of :class:`CommandsExt`.  ``run_cmd`` returns
    ``(status, stdout, stderr)``; the methods used to unpack it as ``status, stderr, stdout``, which swapped the
    two streams in the raised :class:`CommandError` and its message.  The client, system context and session
    are small fakes that script the ``run_cmd`` results.
"""

from typing import List, Optional, Tuple

import ccai.testbase as testbase

from ccai.errors.exceptions import CommandError
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
        return

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False

    def directory_exists(self, path: str) -> bool:
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
