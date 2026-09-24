import ccai.testbase as testbase

from ccai.errors.exceptions import AbstractMethodError, SemanticError
from ccai.interop.protocols.tasker.taskercontroller import ClientTaskerController, TaskerController
from ccai.interop.protocols.tasker.taskernode import TaskerClientNode
from ccai.interop.protocols.tasker.tasking import TaskingIdentity, Tasking
from ccai.interop.protocols.tasker.taskingevent import TaskingEvent
from ccai.interop.protocols.tasker.taskeraspects import TaskerAspects
from ccai.testbase.mocking import create_class_patch, create_module_patch
from ccai.testbase.results.model.taskingresult import TaskingResult
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


class FakeNetworkClient:
    """
        A network client exposing the ``ipaddr`` that :class:`ClientTaskerController` reads.
    """

    def __init__(self, ipaddr: str):
        self.ipaddr = ipaddr
        return


def test_base_start_tasker_network_accepts_the_clients_parameter() -> None:
    """
        The abstract ``TaskerController.start_tasker_network`` declares the optional ``clients`` parameter that
        the client controller override uses, so a call through the base type reaches the abstract method error
        instead of failing with a TypeError for the unexpected argument.
    """
    controller = TaskerController()

    raised = None
    try:
        controller.start_tasker_network([FakeNetworkClient("1.2.3.4")], output_directory="/tmp/out")
    except AbstractMethodError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "AbstractMethodError raised by the abstract start_tasker_network")
    testbase.assert_true("start_tasker_network" in str(raised), "the error names the method to overload")
    return


def test_client_start_tasker_network_without_clients_raises_semantic_error() -> None:
    """
        ``ClientTaskerController.start_tasker_network`` still requires its clients; calling it without them
        raises a SemanticError that names the parameter and leaves the network unstarted.
    """
    controller = ClientTaskerController()

    raised = None
    try:
        controller.start_tasker_network()
    except SemanticError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "SemanticError raised when 'clients' is missing")
    testbase.assert_true("'clients'" in str(raised), "the error names the missing 'clients' parameter")
    testbase.assert_equal(controller._network_started, False)
    testbase.assert_equal(controller.tasker_nodes, [])
    return


def test_client_start_tasker_network_opens_a_session_per_client() -> None:
    """
        The positional ``clients`` call used by existing callers still starts a node for every client.
    """
    controller = ClientTaskerController()
    clients = [FakeNetworkClient("10.0.0.1"), FakeNetworkClient("10.0.0.2")]

    opened = []

    with create_class_patch(TaskerClientNode, "session_open") as mock_open:
        mock_open.configure(side_effect=lambda **kwargs: opened.append(kwargs))
        controller.start_tasker_network(clients, output_directory="/tmp/out")

    testbase.assert_equal(controller._network_started, True)
    testbase.assert_equal([node.ipaddr for node in controller.tasker_nodes], ["10.0.0.1", "10.0.0.2"])
    testbase.assert_equal([entry["worker"] for entry in opened], ["10.0.0.1", "10.0.0.2"])
    testbase.assert_equal([entry["wref"] for entry in opened], ["0", "1"])
    testbase.assert_equal([entry["output_directory"] for entry in opened], ["/tmp/out", "/tmp/out"])
    return
