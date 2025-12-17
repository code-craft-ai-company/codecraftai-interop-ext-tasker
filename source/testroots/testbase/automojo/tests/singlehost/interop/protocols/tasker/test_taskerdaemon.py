import os
import tempfile
import argparse

import automojo.testbase as testbase
from automojo.testbase.mocking import create_module_patch, create_class_patch

from automojo.interop.protocols.tasker import taskerdaemon


def _setup_temp_server_paths():
    """Create a temp directory and patch daemon class paths."""
    tmpdir = tempfile.mkdtemp(prefix="tdtest_")
    logdir = os.path.join(tmpdir, "logs")
    cfg = os.path.join(tmpdir, "tasker.conf")
    pidfile = os.path.join(tmpdir, "tasker.pid")
    with open(cfg, "w"):
        pass

    orig_logdir = taskerdaemon.TaskerServerDaemon.SERVER_LOGDIR
    orig_pidfile = taskerdaemon.TaskerServerDaemon.SERVER_PID_FILE
    orig_cfg = taskerdaemon.TaskerServerDaemon.SERVER_CONFIG_PATH

    taskerdaemon.TaskerServerDaemon.SERVER_LOGDIR = logdir
    taskerdaemon.TaskerServerDaemon.SERVER_PID_FILE = pidfile
    taskerdaemon.TaskerServerDaemon.SERVER_CONFIG_PATH = cfg

    return tmpdir, (orig_logdir, orig_pidfile, orig_cfg)


def _restore_server_paths(paths):
    taskerdaemon.TaskerServerDaemon.SERVER_LOGDIR = paths[0]
    taskerdaemon.TaskerServerDaemon.SERVER_PID_FILE = paths[1]
    taskerdaemon.TaskerServerDaemon.SERVER_CONFIG_PATH = paths[2]
    return


def test_write_trace_appends_lines():
    tmpdir = tempfile.mkdtemp(prefix="wtrace_")
    logfile = os.path.join(tmpdir, "trace.log")

    taskerdaemon.write_trace(logfile, "alpha")
    taskerdaemon.write_trace(logfile, "beta")

    with open(logfile, "r") as tf:
        lines = [ln.strip() for ln in tf.readlines()]

    testbase.assert_equal(lines, ["alpha", "beta"])
    return


def test_process_exists_true_and_false():
    tmpdir, orig = _setup_temp_server_paths()
    try:
        daemon = taskerdaemon.TaskerServerDaemon()
        with create_module_patch(taskerdaemon.os, "kill") as mock_kill:
            mock_kill.configure(return_value=None)
            testbase.assert_equal(daemon.process_exists(1), True)

        def raise_oserror(pid, sig):
            raise OSError()

        with create_module_patch(taskerdaemon.os, "kill") as mock_kill:
            mock_kill.configure(side_effect=raise_oserror)
            testbase.assert_equal(daemon.process_exists(2), False)
    finally:
        _restore_server_paths(orig)
    return


def test_remove_pidfile_deletes_existing_file():
    tmpdir, orig = _setup_temp_server_paths()
    try:
        daemon = taskerdaemon.TaskerServerDaemon()
        with open(daemon._pid_file, "w") as pf:
            pf.write("1")
        testbase.assert_equal(os.path.exists(daemon._pid_file), True)
        daemon._remove_pidfile()
        testbase.assert_equal(os.path.exists(daemon._pid_file), False)
    finally:
        _restore_server_paths(orig)
    return


def test_daemon_main_start_action_invokes_start():
    tmpdir, orig = _setup_temp_server_paths()
    try:
        with create_class_patch(taskerdaemon.TaskerServerDaemon, "start") as mock_start:
            mock_start.configure(return_value=None)
            with create_class_patch(argparse.ArgumentParser, "parse_args") as mock_parse:
                mock_parse.configure(return_value=argparse.Namespace(action="start", debug=False))
                taskerdaemon.tasker_daemon_main()
        testbase.assert_equal(mock_start.call_count, 1)
    finally:
        _restore_server_paths(orig)
    return


def test_daemon_main_debug_flag_forces_start():
    tmpdir, orig = _setup_temp_server_paths()
    try:
        with create_class_patch(taskerdaemon.TaskerServerDaemon, "start") as mock_start:
            mock_start.configure(return_value=None)
            with create_class_patch(taskerdaemon.TaskerServerDaemon, "stop") as mock_stop:
                mock_stop.configure(return_value=None)
                with create_class_patch(argparse.ArgumentParser, "parse_args") as mock_parse:
                    mock_parse.configure(return_value=argparse.Namespace(action="stop", debug=True))
                    taskerdaemon.tasker_daemon_main()
        testbase.assert_equal(mock_start.call_count, 1)
        testbase.assert_equal(mock_stop.call_count, 0)
    finally:
        _restore_server_paths(orig)
    return
