import automojo.testbase as testbase

from automojo.interop.protocols.tasker.taskercontroller import TaskerController
from automojo.interop.protocols.tasker.tasking import TaskingIdentity, Tasking
from automojo.interop.protocols.tasker.taskingevent import TaskingEvent
from automojo.interop.protocols.tasker.taskeraspects import TaskerAspects
from automojo.testbase.mocking import create_module_patch
from automojo.testbase.results.model.taskingresult import TaskingResult
import time


class DummyNode:
    def __init__(self):
        self.calls = []

    def execute_tasking(self, *, module_name, tasking_name, parent_id=None, summary_progress=None, aspects=None, **kwargs):
        self.calls.append((module_name, tasking_name, parent_id, summary_progress, aspects, kwargs))
        return f"promise-{tasking_name}"

    def reinitialize_logging(self, **kwargs):
        self.log_params = kwargs
        return


class DummyPromise:
    def __init__(self, events_when=None, complete_after=1, result=None):
        self._events_when = events_when or {}
        self._complete_after = complete_after
        self._iteration = 0
        if result is None:
            result = TaskingResult("id", "name", "parent", "worker")
        self._result = result

    def get_events(self):
        return self._events_when.get(self._iteration, [])

    def is_task_complete(self):
        complete = self._iteration >= self._complete_after
        self._iteration += 1
        return complete

    def get_result(self):
        return self._result


def test_execute_tasking_variants() -> None:
    controller = TaskerController()
    node1 = DummyNode()
    node2 = DummyNode()
    controller._tasker_nodes = [node1, node2]

    identity = TaskingIdentity("mod", "Task")
    plist = controller.execute_tasking_on_all_nodes(tasking=identity, parent_id="p1", summary_progress="sum", aspects="asp", extra=1)
    testbase.assert_equal(plist, ["promise-Task", "promise-Task"])
    testbase.assert_equal(node1.calls[0][0], "mod")
    testbase.assert_equal(node1.calls[0][1], "Task")
    testbase.assert_equal(node1.calls[0][2], "p1")
    testbase.assert_equal(node1.calls[0][3], "sum")
    testbase.assert_equal(node1.calls[0][4], "asp")
    testbase.assert_equal(node1.calls[0][5], {"extra": 1})

    class SampleTask(Tasking):
        pass

    SampleTask.__module__ = "dummy"

    controller.execute_tasking_on_node(node1, tasking=SampleTask, parent_id="p2")
    testbase.assert_equal(node1.calls[1][0], "dummy")
    testbase.assert_equal(node1.calls[1][1], "SampleTask")
    testbase.assert_equal(node1.calls[1][2], "p2")
    return


def test_wait_for_any_to_event_success() -> None:
    aspects = TaskerAspects(completion_timeout=0.2, completion_interval=0.0)
    controller = TaskerController(aspects=aspects)

    evt = TaskingEvent("t1", "DONE")
    p1 = DummyPromise(events_when={1: [evt]}, complete_after=1)
    p2 = DummyPromise(events_when={}, complete_after=3)

    with create_module_patch(time, "sleep") as slp:
        slp.configure(return_value=None)
        evts = controller.wait_for_any_to_event("DONE", [p1, p2], aspects)
    testbase.assert_equal(evts, [evt])
    return


def test_wait_for_any_to_event_error_when_task_complete_without_event() -> None:
    aspects = TaskerAspects(completion_timeout=0.1, completion_interval=0.0)
    controller = TaskerController(aspects=aspects)

    p1 = DummyPromise(events_when={}, complete_after=1)
    err = None
    with create_module_patch(time, "sleep") as slp:
        slp.configure(return_value=None)
        try:
            controller.wait_for_any_to_event("X", [p1], aspects)
        except RuntimeError as exc:
            err = exc
    testbase.assert_equal(isinstance(err, RuntimeError), True)
    return


def test_wait_for_tasking_results_returns_results() -> None:
    aspects = TaskerAspects(completion_timeout=0.2, completion_interval=0.0)
    controller = TaskerController(aspects=aspects)

    r1 = TaskingResult("id1", "t1", "p", "w")
    r2 = TaskingResult("id2", "t2", "p", "w")

    p1 = DummyPromise(complete_after=1, result=r1)
    p2 = DummyPromise(complete_after=2, result=r2)

    with create_module_patch(time, "sleep") as slp:
        slp.configure(return_value=None)
        results = controller.wait_for_tasking_results([p1, p2], aspects)

    testbase.assert_equal(results, [r1, r2])
    return
