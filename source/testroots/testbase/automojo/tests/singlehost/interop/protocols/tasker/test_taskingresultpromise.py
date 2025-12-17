import automojo.testbase as testbase

from automojo.interop.protocols.tasker.taskingresultpromise import (
    TaskingResultPromise,
    TaskingRef,
)


class DummyClient:
    def close(self):
        return


class DummyResponder:
    def stop(self):
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
