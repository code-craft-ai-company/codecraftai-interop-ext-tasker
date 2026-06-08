import pickle
import logging
import ccai.testbase as testbase
from ccai.interop.protocols.tasker.taskernode import TaskerNode
from ccai.interop.protocols.tasker.taskeraspects import TaskerAspects
import ccai.interop.protocols.tasker.taskernode as taskernode
from ccai.testbase.mocking import create_module_patch


class DummyRoot:
    def __init__(self):
        self.session_open_args = []
        self.session_close_args = []
        self.execute_tasking_args = []
        self.call_tasking_method_args = []

    def session_open(self, **kwargs):
        self.session_open_args.append(kwargs)
        return "SID"

    def session_close(self, session_id=None):
        self.session_close_args.append(session_id)
        return

    def execute_tasking(self, **kwargs):
        self.execute_tasking_args.append(kwargs)
        return {
            "module_name": kwargs["module_name"],
            "tasking_id": "tid",
            "task_name": kwargs["tasking_name"],
            "log_dir": "/logs",
        }

    def call_tasking_method(self, **kwargs):
        args = pickle.loads(kwargs["pkl_args"])
        kwargs_val = pickle.loads(kwargs["pkl_kwargs"])
        self.call_tasking_method_args.append((kwargs["session_id"], kwargs["tasking_id"], kwargs["method_name"], args, kwargs_val))
        return pickle.dumps("RESP")

    def get_tasking_progress(self, **kwargs):
        return None


class DummyClient:
    def __init__(self, root):
        self.root = root
        self.closed = False

    def close(self):
        self.closed = True
        return


class DummyPromise:
    def __init__(self, *args):
        self.args = args
        return


def test_create_connection_uses_timeout_and_connects():
    dummy = DummyClient(DummyRoot())
    with create_module_patch(taskernode.rpyc, "connect") as mock_conn:
        mock_conn.configure(return_value=dummy)
        aspects = TaskerAspects(sync_request_timeout=5)
        node = TaskerNode("1.1.1.1", 10, aspect=aspects)
        client = node._create_connection()

    testbase.assert_equal(client, dummy)
    testbase.assert_equal(mock_conn.call_count, 1)
    cargs, ckwargs = mock_conn.call_args
    testbase.assert_equal(cargs, ("1.1.1.1", 10))
    testbase.assert_equal(ckwargs["keepalive"], True)
    testbase.assert_equal(ckwargs["config"]["sync_request_timeout"], 5)
    testbase.assert_equal(node._protocol_config["sync_request_timeout"], 5)
    return


def test_session_open_sets_session_id_and_closes_client():
    root = DummyRoot()
    client = DummyClient(root)
    node = TaskerNode("1.2.3.4", 11)
    node._create_connection = lambda: client
    sid = node.session_open(worker="wk", wref=None, output_directory="out", log_level=logging.INFO, aspects="AP")

    testbase.assert_equal(client.closed, True)
    testbase.assert_equal(sid, "SID")
    testbase.assert_equal(node.session_id, "SID")
    call = root.session_open_args[0]
    testbase.assert_equal(call["worker"], "wk")
    testbase.assert_equal(call["wref"], node.ipaddr)
    testbase.assert_equal(call["output_directory"], "out")
    testbase.assert_equal(call["log_level"], logging.INFO)
    testbase.assert_equal(call["aspects"], "AP")
    return


def test_session_close_resets_session_id_and_calls_remote():
    root = DummyRoot()
    client = DummyClient(root)
    node = TaskerNode("1.2.3.4", 11)
    node._session_id = "SID"
    node._create_connection = lambda: client

    node.session_close()

    testbase.assert_equal(client.closed, True)
    testbase.assert_equal(node.session_id, None)
    testbase.assert_equal(root.session_close_args, ["SID"])
    return


def test_execute_tasking_returns_promise():
    root = DummyRoot()
    client = DummyClient(root)
    node = TaskerNode("1.2.3.4", 11)
    node._session_id = "SID"
    node._create_connection = lambda: client
    with (
        create_module_patch(taskernode.rpyc, "BgServingThread") as mock_thread,
        create_module_patch(taskernode, "TaskingResultPromise") as mock_promise
    ):
        dummy_thread = object()
        mock_thread.configure(return_value=dummy_thread)
        captured = []
        def promise_ctor(*args):
            captured.append(args)
            return DummyPromise(*args)
        mock_promise.configure(side_effect=promise_ctor)

        prom = node.execute_tasking(module_name="mod", tasking_name="Task", param=1)

    testbase.assert_equal(isinstance(prom, DummyPromise), True)
    testbase.assert_equal(mock_thread.call_count, 1)
    testbase.assert_equal(len(root.execute_tasking_args), 1)
    call = root.execute_tasking_args[0]
    testbase.assert_equal(call["session_id"], "SID")
    testbase.assert_equal(call["worker"], node.ipaddr)
    testbase.assert_equal(call["module_name"], "mod")
    testbase.assert_equal(call["tasking_name"], "Task")
    testbase.assert_equal(call["param"], 1)
    testbase.assert_equal(captured[0][0], client)
    testbase.assert_equal(captured[0][1], dummy_thread)
    testbase.assert_equal(captured[0][2], "mod")
    testbase.assert_equal(captured[0][3], "tid")
    testbase.assert_equal(captured[0][4], "Task")
    testbase.assert_equal(captured[0][5], "/logs")
    testbase.assert_equal(captured[0][6], "SID")
    testbase.assert_equal(captured[0][7], node)
    return


def test_call_tasking_method_pickles_arguments():
    root = DummyRoot()
    client = DummyClient(root)
    node = TaskerNode("1.2.3.4", 11)
    node._session_id = "SID"
    node._create_connection = lambda: client

    result = node.call_tasking_method(tasking_id="tid", method_name="meth", args=[1, 2], kwargs={"k": 3})

    testbase.assert_equal(result, "RESP")
    testbase.assert_equal(client.closed, True)
    testbase.assert_equal(root.call_tasking_method_args, [("SID", "tid", "meth", [1, 2], {"k": 3})])
    return
