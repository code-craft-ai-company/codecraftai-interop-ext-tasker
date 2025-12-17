import threading
import tempfile
import automojo.testbase as testbase

from automojo.interop.protocols.tasker.taskerserver import TaskerServer


def _create_server(tmpdir):
    return TaskerServer(
        hostname="localhost",
        port=0,
        registrar=None,
        logging_directory=str(tmpdir)
    )


def test_get_service_endpoint_matches_listener() -> None:
    tmpdir = tempfile.mkdtemp()
    svr = _create_server(tmpdir)
    exp = svr.listener.getsockname()
    ip, port = svr.get_service_endpoint()
    testbase.assert_equal((ip, port), exp)
    svr.close()
    return


def test_start_runs_service_thread() -> None:
    tmpdir = tempfile.mkdtemp()
    svr = _create_server(tmpdir)

    def fake_listen():
        svr.active = True
    def fake_register():
        return
    def fake_accept():
        svr.active = False
        return
    svr._listen = fake_listen
    svr._register = fake_register
    svr.accept = fake_accept

    svr.start()
    svr._server_thread.join(timeout=1)
    testbase.assert_equal(svr._server_thread.is_alive(), False)
    svr.close()
    return


def test_serve_forever_runs_in_current_thread() -> None:
    tmpdir = tempfile.mkdtemp()
    svr = _create_server(tmpdir)

    def fake_listen():
        svr.active = True
    def fake_register():
        return
    def fake_accept():
        svr.active = False
        return
    svr._listen = fake_listen
    svr._register = fake_register
    svr.accept = fake_accept

    svr.serve_forever()
    testbase.assert_equal(svr.active, False)
    svr.close()
    return
