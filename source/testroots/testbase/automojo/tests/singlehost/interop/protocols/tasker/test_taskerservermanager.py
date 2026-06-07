import os
import tempfile

import ccai.testbase as testbase

from ccai.interop.protocols.tasker.taskerservermanager import (
    spawn_tasking_server_process,
    TaskerServerManager,
)


def test_spawn_returns_running_server() -> None:
    mgr, proxy = spawn_tasking_server_process(("127.0.0.1", 0))
    try:
        proxy.start()
        ipaddr, port = proxy.get_service_endpoint()
    finally:
        proxy.close()
        mgr.shutdown()
    testbase.assert_equal(isinstance(mgr, TaskerServerManager), True)
    testbase.assert_equal(isinstance(ipaddr, str), True)
    testbase.assert_equal(port > 0, True)
    return


def test_spawn_uses_logging_directory() -> None:
    logdir = tempfile.mkdtemp(prefix="tasker-test-")
    mgr, proxy = spawn_tasking_server_process(("127.0.0.1", 0), logging_directory=logdir)
    try:
        proxy.start()
    finally:
        proxy.close()
        mgr.shutdown()
    log_file = os.path.join(logdir, "tasker-server.log")
    testbase.assert_equal(os.path.isfile(log_file), True)
    return
