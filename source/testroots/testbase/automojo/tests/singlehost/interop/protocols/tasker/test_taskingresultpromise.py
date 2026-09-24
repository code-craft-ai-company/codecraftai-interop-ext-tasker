import gc

import ccai.testbase as testbase

from ccai.interop.protocols.tasker.taskingresultpromise import (
    TaskingResultPromise,
    TaskingRef,
)


class DummyClient:
    def __init__(self, calls=None):
        self.close_count = 0
        self._calls = calls
        return

    def close(self):
        self.close_count += 1
        if self._calls is not None:
            self._calls.append("client.close")
        return


class DummyResponder:
    def __init__(self, calls=None):
        self.stop_count = 0
        self._calls = calls
        return

    def stop(self):
        self.stop_count += 1
        if self._calls is not None:
            self._calls.append("responder.stop")
        return


class FailingResponder:
    def stop(self):
        raise RuntimeError("responder stop failed")


class DummyMonitor:
    def __init__(self, calls=None):
        self.released = []
        self._calls = calls
        return

    def release(self, tasking_id):
        self.released.append(tasking_id)
        if self._calls is not None:
            self._calls.append("monitor.release")
        return


class DummyNode:
    def __init__(self):
        self.cancel_args = []
        self.call_args = None
        self.events = ["event"]
        self.result = "result"
        self.progress = "progress"
        self.ready_sequence = []
        self.ready_call_count = 0
        self.default_ready = True

    def cancel_tasking(self, tasking_id):
        self.cancel_args.append(tasking_id)

    def call_tasking_method(self, tasking_id, method_name, args, kwargs):
        self.call_args = (tasking_id, method_name, args, kwargs)
        return "call_ret"

    def get_tasking_events(self, tasking_id):
        return self.events

    def get_tasking_result(self, tasking_id):
        return self.result

    def get_tasking_progress(self, tasking_id):
        return self.progress

    def has_completed_and_result_ready(self, tasking_id):
        self.ready_call_count += 1
        if self.ready_sequence:
            return self.ready_sequence.pop(0)
        return self.default_ready


def create_promise(node: DummyNode) -> TaskingResultPromise:
    return TaskingResultPromise(
        DummyClient(),
        DummyResponder(),
        "module",
        "taskid",
        "Task",
        "/tmp",
        "sess",
        node,
    )


def test_taskingref_as_dict() -> None:
    tref = TaskingRef("mod", "id", "name", "/tmp/log")
    testbase.assert_equal(
        tref.as_dict(),
        {
            "module_name": "mod",
            "tasking_id": "id",
            "task_name": "name",
            "log_dir": "/tmp/log",
        },
    )
    return


def test_cancel_invokes_node() -> None:
    node = DummyNode()
    prom = create_promise(node)
    prom.cancel()
    testbase.assert_equal(node.cancel_args, ["taskid"])
    return


def test_call_tasking_method_forwards_args() -> None:
    node = DummyNode()
    prom = create_promise(node)
    result = prom.call_tasking_method("run", 1, 2, foo="bar")
    testbase.assert_equal(result, "call_ret")
    testbase.assert_equal(
        node.call_args,
        ("taskid", "run", (1, 2), {"foo": "bar"}),
    )
    return


def test_getters_return_node_values() -> None:
    node = DummyNode()
    prom = create_promise(node)
    testbase.assert_equal(prom.get_events(), ["event"])
    testbase.assert_equal(prom.get_result(), "result")
    testbase.assert_equal(prom.get_progress(), "progress")
    return


def test_is_task_complete_relays_node() -> None:
    node = DummyNode()
    node.ready_sequence = [True]
    prom = create_promise(node)
    testbase.assert_equal(prom.is_task_complete(), True)
    testbase.assert_equal(node.ready_call_count, 1)
    return


def test_wait_completes_when_done() -> None:
    node = DummyNode()
    node.ready_sequence = [False, False, True]
    prom = create_promise(node)
    prom.wait(timeout=1, interval=0)
    testbase.assert_equal(node.ready_call_count >= 3, True)
    return


def test_wait_timeout_raises_error() -> None:
    node = DummyNode()
    node.ready_sequence = [False] * 100
    node.default_ready = False
    prom = create_promise(node)
    exc = None
    try:
        prom.wait(timeout=0.01, interval=0)
    except Exception as err:
        exc = err
    testbase.assert_equal(isinstance(exc, TimeoutError), True)
    return


def create_closable_promise(client, responder, monitor=None) -> TaskingResultPromise:
    return TaskingResultPromise(
        client,
        responder,
        "module",
        "taskid",
        "Task",
        "/tmp",
        "sess",
        DummyNode(),
        progress_monitor=monitor,
    )


def test_close_releases_monitor_stops_responder_and_closes_client() -> None:
    """
        close() releases the progress monitoring of the tasking, stops the responder thread and closes the
        dedicated client, in that order.
    """
    calls = []
    client = DummyClient(calls)
    responder = DummyResponder(calls)
    monitor = DummyMonitor(calls)
    prom = create_closable_promise(client, responder, monitor)

    testbase.assert_equal(prom.closed, False)
    prom.close()

    testbase.assert_equal(prom.closed, True)
    testbase.assert_equal(calls, ["monitor.release", "responder.stop", "client.close"])
    testbase.assert_equal(monitor.released, ["taskid"])
    return


def test_close_is_idempotent() -> None:
    """
        Closing a promise more than once, including the finalizer running after an explicit close, releases
        its resources only once.
    """
    client = DummyClient()
    responder = DummyResponder()
    monitor = DummyMonitor()
    prom = create_closable_promise(client, responder, monitor)

    prom.close()
    prom.close()
    # Dropping the last reference runs the __del__ fallback, which must not close anything again.
    del prom
    gc.collect()

    testbase.assert_equal(client.close_count, 1)
    testbase.assert_equal(responder.stop_count, 1)
    testbase.assert_equal(monitor.released, ["taskid"])
    return


def test_context_manager_closes_the_promise() -> None:
    """
        Using the promise as a context manager closes it when the context exits.
    """
    client = DummyClient()
    responder = DummyResponder()

    with create_closable_promise(client, responder) as prom:
        testbase.assert_equal(prom.closed, False)

    testbase.assert_equal(prom.closed, True)
    testbase.assert_equal(client.close_count, 1)
    testbase.assert_equal(responder.stop_count, 1)
    return


def test_context_manager_closes_the_promise_and_propagates_errors() -> None:
    """
        An error raised inside the context still closes the promise and is not swallowed.
    """
    client = DummyClient()
    responder = DummyResponder()

    raised = None
    prom = None
    try:
        with create_closable_promise(client, responder) as prom:
            raise ValueError("inside the context")
    except ValueError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "the error raised inside the context propagates")
    testbase.assert_equal(prom.closed, True)
    testbase.assert_equal(client.close_count, 1)
    return


def test_close_closes_the_client_when_the_responder_fails_to_stop() -> None:
    """
        A responder that fails to stop does not leave the client open, and the failure reaches the caller
        of an explicit close.
    """
    client = DummyClient()
    prom = create_closable_promise(client, FailingResponder())

    raised = None
    try:
        prom.close()
    except RuntimeError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "the responder failure propagates from close()")
    testbase.assert_equal(client.close_count, 1)
    testbase.assert_equal(prom.closed, True)

    # The finalizer does not retry the failed close and does not raise.
    del prom
    gc.collect()
    testbase.assert_equal(client.close_count, 1)
    return


def test_close_closes_the_client_without_a_responder() -> None:
    """
        A promise created without a responder thread still closes its client.
    """
    client = DummyClient()
    prom = create_closable_promise(client, None)

    prom.close()

    testbase.assert_equal(client.close_count, 1)
    return


def test_finalizer_closes_an_unclosed_promise() -> None:
    """
        The finalizer remains as a fallback and closes a promise that was not closed explicitly.
    """
    client = DummyClient()
    responder = DummyResponder()
    monitor = DummyMonitor()
    prom = create_closable_promise(client, responder, monitor)

    del prom
    gc.collect()

    testbase.assert_equal(client.close_count, 1)
    testbase.assert_equal(responder.stop_count, 1)
    testbase.assert_equal(monitor.released, ["taskid"])
    return
